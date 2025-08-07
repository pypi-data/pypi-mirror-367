import csv
import time
import datetime
import logging
import os
import pickle
from typing import Dict, List, Tuple, Optional, Any, Callable
from multiprocessing.dummy import Pool

import polyline
import requests
import yaml
from pydantic import BaseModel
from shapely.geometry import Point

# Import functions from modules
from canterburycommuto.PlotMaps import plot_routes, plot_routes_and_buffers
from canterburycommuto.HelperFunctions import generate_unique_filename, write_csv_file, safe_split
from canterburycommuto.Computations import (
    find_common_nodes,
    split_segments,
    calculate_segment_distances,
    create_segment_rectangles,
    filter_combinations_by_overlap,
    find_overlap_boundary_nodes,
    create_buffered_route,
    get_buffer_intersection,
    get_route_polygon_intersections,
)

class RouteBase(BaseModel):
    """Base model for route endpoints (split lat/lon) and basic metrics."""
    ID: str
    OriginAlat: Optional[float] = None
    OriginAlong: Optional[float] = None
    DestinationAlat: Optional[float] = None
    DestinationAlong: Optional[float] = None
    OriginBlat: Optional[float] = None
    OriginBlong: Optional[float] = None
    DestinationBlat: Optional[float] = None
    DestinationBlong: Optional[float] = None
    aDist: Optional[float] = None
    aTime: Optional[float] = None
    bDist: Optional[float] = None
    bTime: Optional[float] = None

class FullOverlapResult(RouteBase):
    """Detailed result with full segment and overlap analysis."""
    overlapDist: Optional[float] = None
    overlapTime: Optional[float] = None
    aBeforeDist: Optional[float] = None
    aBeforeTime: Optional[float] = None
    bBeforeDist: Optional[float] = None
    bBeforeTime: Optional[float] = None
    aAfterDist: Optional[float] = None
    aAfterTime: Optional[float] = None
    bAfterDist: Optional[float] = None
    bAfterTime: Optional[float] = None


class SimpleOverlapResult(RouteBase):
    """Simplified result with only overlap distance and time."""
    overlapDist: Optional[float] = None
    overlapTime: Optional[float] = None


class IntersectionRatioResult(RouteBase):
    """Result showing ratio of route overlap for A and B."""
    aIntersecRatio: Optional[float] = None
    bIntersecRatio: Optional[float] = None

class DetailedDualOverlapResult(RouteBase):
    """Detailed result with A/B overlaps and pre/post overlap segments."""
    aoverlapDist: Optional[float] = None
    aoverlapTime: Optional[float] = None
    boverlapDist: Optional[float] = None
    boverlapTime: Optional[float] = None

    aBeforeDist: Optional[float] = None
    aBeforeTime: Optional[float] = None
    aAfterDist: Optional[float] = None
    aAfterTime: Optional[float] = None

    bBeforeDist: Optional[float] = None
    bBeforeTime: Optional[float] = None
    bAfterDist: Optional[float] = None
    bAfterTime: Optional[float] = None

class SimpleDualOverlapResult(RouteBase):
    """Simplified result with only A/B overlap distances and times."""
    aoverlapDist: Optional[float] = None
    aoverlapTime: Optional[float] = None
    boverlapDist: Optional[float] = None
    boverlapTime: Optional[float] = None

# Global cache for Google API responses
api_response_cache = {}

# Global URL for Google Maps Routes API (v2)
GOOGLE_API_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"

# Global URL for local GraphHopper server (assumes user followed setup)
GRAPHOPPER_BASE_URL = "http://localhost:8989"

# Function to read a csv file and then asks the users to manually enter their corresponding column variables with respect to OriginA, DestinationA, OriginB, and DestinationB.
# The following functions also help determine if there are errors in the code. 

# Always save the log in the current working directory, not in the results folder
log_path = os.path.join(os.getcwd(), "validation_errors_timing.log")

# Set up logging
logging.basicConfig(
    filename=log_path,
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def is_valid_coordinate(coord: str) -> bool:
    """
    Checks if the coordinate string is a valid latitude,longitude pair.
    Validates format, numeric values, and geographic bounds.

    Returns True if valid, False otherwise.
    """
    if not isinstance(coord, str):
        return False
    parts = coord.strip().split(",")
    if len(parts) != 2:
        return False

    try:
        lat = float(parts[0].strip())
        lon = float(parts[1].strip())
        if not (-90 <= lat <= 90):
            return False
        if not (-180 <= lon <= 180):
            return False
        return True
    except ValueError:
        return False

def read_csv_file(
    csv_file: str,
    input_dir: str,
    home_a_lat: str,
    home_a_lon: str,
    work_a_lat: str,
    work_a_lon: str,
    home_b_lat: str,
    home_b_lon: str,
    work_b_lat: str,
    work_b_lon: str,
    id_column: Optional[str] = None,
    skip_invalid: bool = True
) -> Tuple[List[Dict[str, str]], int]:
    """
    Reads a CSV file with separate latitude/longitude columns for each endpoint,
    combines them into coordinate strings, and maps to standardized names.
    Optionally handles/generates an ID column.
    Parameters:
    -----------
    csv_file : str
        Name of the input CSV file.
    input_dir : str
        Directory where the CSV file is located.
    home_a_lat : str
        Column name for the latitude of home A.
    home_a_lon : str
        Column name for the longitude of home A.
    work_a_lat : str
        Column name for the latitude of work A.
    work_a_lon : str
        Column name for the longitude of work A.
    home_b_lat : str
        Column name for the latitude of home B.
    home_b_lon : str
        Column name for the longitude of home B.
    work_b_lat : str
        Column name for the latitude of work B.
    work_b_lon : str
        Column name for the longitude of work B.
    input_dir : Optional[str], default=None
    id_column : Optional[str], default=None
        Column name for the unique ID of each row. If None or not found, IDs are auto-generated as R1, R2, ...
    skip_invalid : bool, default=True
        If True, rows with invalid coordinates are skipped and logged. If False, the function raises an error on invalid data.

    Returns:
    --------
    Tuple[List[Dict[str, str]], int]
        - List of dictionaries, each with standardized keys:
            'ID', 'OriginA', 'DestinationA', 'OriginB', 'DestinationB'
        - Integer count of rows with invalid coordinates that were skipped (0 if skip_invalid is False).

    Notes:
    ------
    - The function expects the CSV to have 8 columns for latitude and longitude, as specified by the input arguments.
    - The function combines each latitude/longitude pair into a single string "lat,lon" for each endpoint.
    - The function ensures each row has an 'ID' field, either from the CSV or auto-generated.
    """
    csv_path = os.path.join(input_dir, csv_file)
    with open(csv_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        csv_columns = reader.fieldnames

        # Check all required columns exist
        required_columns = [
            home_a_lat, home_a_lon, work_a_lat, work_a_lon,
            home_b_lat, home_b_lon, work_b_lat, work_b_lon
        ]
        for column in required_columns:
            if column not in csv_columns:
                raise ValueError(f"Column '{column}' not found in the CSV file.")

        rows = list(reader)

        # Combine lat/lon into coordinate strings
        for idx, row in enumerate(rows, 1):
            row["OriginA"] = f"{row[home_a_lat].strip()},{row[home_a_lon].strip()}"
            row["DestinationA"] = f"{row[work_a_lat].strip()},{row[work_a_lon].strip()}"
            row["OriginB"] = f"{row[home_b_lat].strip()},{row[home_b_lon].strip()}"
            row["DestinationB"] = f"{row[work_b_lat].strip()},{row[work_b_lon].strip()}"
            # Handle ID column
            if id_column and id_column in csv_columns:
                row["ID"] = row[id_column]
            else:
                row["ID"] = f"R{idx}"

        mapped_data = []
        error_count = 0
        row_number = 1
        for row in rows:
            coords = [
                row["OriginA"],
                row["DestinationA"],
                row["OriginB"],
                row["DestinationB"],
            ]
            invalids = [c for c in coords if not is_valid_coordinate(c)]

            if invalids:
                error_msg = f"Row {row_number} - Invalid coordinates: {invalids}"
                logging.warning(error_msg)
                error_count += 1
                if not skip_invalid:
                    raise ValueError(error_msg)

            # Only keep standardized columns (and ID)
            mapped_row = {
                "ID": row["ID"],
                "OriginA": row["OriginA"],
                "DestinationA": row["DestinationA"],
                "OriginB": row["OriginB"],
                "DestinationB": row["DestinationB"],
            }
            mapped_data.append(mapped_row)
            row_number += 1

        return mapped_data, error_count

def request_cost_estimation(
    csv_file: str,
    input_dir: str,
    home_a_lat: str,
    home_a_lon: str,
    work_a_lat: str,
    work_a_lon: str,
    home_b_lat: str,
    home_b_lon: str,
    work_b_lat: str,
    work_b_lon: str,
    id_column: Optional[str] = None,
    approximation: str = "no",
    commuting_info: str = "no",
    skip_invalid: bool = True
) -> Tuple[int, float]:
    """
    Estimates the number of Google API requests needed based on route pair data
    and approximates the cost.

    Parameters:
    - csv_file (str): Name of the input CSV file.
    - input_dir (str): Directory where the CSV file is located.
    - home_a_lat : Column name for the latitude of home A.
    - home_a_lon : Column name for the longitude of home A.
    - work_a_lat : Column name for the latitude of work A.
    - work_a_lon : Column name for the longitude of work A.
    - home_b_lat : Column name for the latitude of home B.
    - home_b_lon : Column name for the longitude of home B.
    - work_b_lat : Column name for the latitude of work B.
    - work_b_lon : Column name for the longitude of work B.
    - id_column : Column name for the unique ID of each row. If None or not found, IDs are auto-generated as R1, R2, ...
    - approximation (str): Approximation strategy to apply.
    - commuting_info (str): Whether commuting info is to be considered.
    - skip_invalid (bool): Whether to skip invalid rows.

    Returns:
    - Tuple[int, float]: Estimated number of API requests and corresponding cost in USD.
    """

    data_set, pre_api_error_count = read_csv_file(csv_file, input_dir, home_a_lat, home_a_lon, work_a_lat, work_a_lon, home_b_lat, home_b_lon, work_b_lat, work_b_lon, id_column, skip_invalid=skip_invalid)
    n = 0

    for row in data_set:
        origin_a = row["OriginA"]
        destination_a = row["DestinationA"]
        origin_b = row["OriginB"]
        destination_b = row["DestinationB"]

        same_a = origin_a == origin_b
        same_b = destination_a == destination_b
        same_a_dest = origin_a == destination_a
        same_b_dest = origin_b == destination_b

        if approximation == "no":
            n += 1 if same_a and same_b else (7 if commuting_info == "yes" else 3)

        elif approximation == "yes":
            n += 1 if same_a and same_b else (7 if commuting_info == "yes" else 4)

        elif approximation == "yes with buffer":
            if same_a_dest and same_b_dest:
                n += 0
            elif same_a_dest or same_b_dest or (same_a and same_b):
                n += 1
            else:
                n += 2

        elif approximation == "closer to precision" or approximation == "exact":
            if same_a_dest and same_b_dest:
                n += 0
            elif same_a_dest or same_b_dest or (same_a and same_b):
                n += 1
            else:
                n += 8 if commuting_info == "yes" else 4

        else:
            raise ValueError(f"Invalid approximation option: '{approximation}'")

    cost = (n / 1000) * 5  # USD estimate
    return n, cost

def generate_request_body(origin: str, destination: str) -> dict:
    """
    Creates the request body for the Google Maps Routes API (v2).

    Parameters:
    - origin (str): The starting point of the route in "latitude,longitude" format.
    - destination (str): The endpoint of the route in "latitude,longitude" format.

    Returns:
    - dict: JSON body for the Routes API POST request.
    """
    origin_lat, origin_lng = map(float, origin.split(','))
    dest_lat, dest_lng = map(float, destination.split(','))

    return {
        "origin": {
            "location": {
                "latLng": {
                    "latitude": origin_lat,
                    "longitude": origin_lng
                }
            }
        },
        "destination": {
            "location": {
                "latLng": {
                    "latitude": dest_lat,
                    "longitude": dest_lng
                }
            }
        },
        "travelMode": "DRIVE",
        "computeAlternativeRoutes": True,  # enables fallback options
        "routeModifiers": {
            "avoidTolls": False
        }
    }

def get_route_data_google(origin: str, destination: str, api_key: str, save_api_info: bool = False) -> tuple:
    """
    Fetches route data from the Google Maps Routes API (v2) and decodes the polyline.

    Parameters:
    - origin (str): Starting point ("latitude,longitude").
    - destination (str): Endpoint ("latitude,longitude").
    - api_key (str): Google Maps API key with Routes API enabled.
    - save_api_info (bool): Optionally saves raw response in cache.

    Returns:
    - tuple:
        - list of (lat, lng) tuples (route polyline)
        - float: distance in kilometers
        - float: time in minutes
    """
    max_retries = 5
    delay = 10  # seconds

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "routes.legs.distanceMeters,routes.legs.duration,routes.polyline.encodedPolyline"
    }

    body = generate_request_body(origin, destination)

    for attempt in range(max_retries):
        try:
            response = requests.post(GOOGLE_API_URL, json=body, headers=headers)
            data = response.json()

            if response.status_code == 200 and "routes" in data and data["routes"]:
                if save_api_info:
                    global api_response_cache
                    api_response_cache[(origin, destination)] = data

                # Pick the shortest route if alternatives are present
                route = min(data["routes"], key=lambda r: r["legs"][0].get("distanceMeters", float("inf")))

                polyline_points = route["polyline"]["encodedPolyline"]
                coordinates = polyline.decode(polyline_points)

                legs = route.get("legs", [])
                if not legs:
                    raise ValueError("No legs found in route.")

                distance_meters = int(legs[0]["distanceMeters"])
                duration_seconds = int(legs[0]["duration"].replace("s", ""))

                return coordinates, distance_meters / 1000, duration_seconds / 60

            elif response.status_code == 429:
                print(f"Rate limit hit (attempt {attempt + 1}/{max_retries}). Retrying in {delay}s...")
                time.sleep(delay*(attempt+1))

            else:
                print("Error fetching route:", data)
                return [], 0, 0

        except Exception as e:
            print(f"Exception during route extraction: {e}")
            return [], 0, 0

    print("Exceeded maximum retries due to rate limit or repeated failure.")
    return [], 0, 0

def get_route_data_graphhopper(origin: str, destination: str, profile: str = "car", save_api_info: bool = False) -> tuple:
    """
    Fetches route data from a locally hosted GraphHopper server.

    Parameters:
    - origin (str): Starting point in "latitude,longitude" format.
    - destination (str): Endpoint in "latitude,longitude" format.
    - profile (str): Travel mode profile (e.g., "car", "bike", "foot").
    - save_api_info (bool): Whether to store raw API response globally.

    Returns:
    - tuple:
        - list of (latitude, longitude) tuples
        - float: distance in km
        - float: time in minutes
    """
    url = f"{GRAPHOPPER_BASE_URL}/route"
    params = {
        "point": [origin, destination],
        "profile": profile,
        "locale": "en",
        "calc_points": "true",
        "points_encoded": "false"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if save_api_info:
            global api_response_cache
            api_response_cache[(origin, destination)] = data

        if "paths" not in data or not data["paths"]:
            print("No route found.")
            return [], 0, 0

        path = data["paths"][0]
        coords = path["points"]["coordinates"]  # [lon, lat] format
        coordinates = [(lat, lon) for lon, lat in coords]  # Convert to (lat, lon)

        distance_km = path["distance"] / 1000
        time_min = path["time"] / 60000

        return coordinates, distance_km, time_min

    except Exception as e:
        print(f"GraphHopper error: {e}")
        return [], 0, 0

def get_route_data(origin: str, destination: str, method: str = "google", api_key: Optional[str] = None, save_api_info: bool = False) -> tuple:
    """
    Unified routing interface supporting Google and GraphHopper.

    Parameters:
    - origin (str): "latitude,longitude"
    - destination (str): "latitude,longitude"
    - method (str): "google" or "graphhopper"
    - api_key (str): Required for Google
    - save_api_info (bool): Cache raw response

    Returns:
    - tuple: (coordinates, distance_km, time_min)
    """
    if method == "google":
        if api_key is None:
            raise ValueError("API key is required for Google Maps method.")
        return get_route_data_google(origin, destination, api_key, save_api_info)

    elif method == "graphhopper":
        return get_route_data_graphhopper(origin, destination, save_api_info=save_api_info)

    else:
        raise ValueError("Method must be 'google' or 'graphhopper'.")

def wrap_row(args): 
    """
    Wraps a single row-processing task for multithreading.

    Args:
        args (tuple): A tuple containing:
            - row (dict): A dictionary representing a single row of data with keys:
            - api_key (str): API key for route data fetching.
            - row_function (callable): Function that processes a single row.
            - input_dir (str): Directory containing the input CSV file's folder.
            - skip_invalid (bool): If True, skips rows with errors; if False, raises an error.
            - save_api_info (bool): If True, saves API response.
            - method (str): "google" or "graphhopper"

    Returns:
        dict or None
    """
    row, api_key, row_function, input_dir, skip_invalid, save_api_info, method = args
    return row_function(
        (row, api_key, save_api_info),
        method=method,
        skip_invalid=skip_invalid,
        input_dir=input_dir
    )

def process_rows(
    data: List[Dict[str, Any]],
    api_key: str,
    row_function: Callable[
        [Tuple[Dict[str, Any], str, bool], str, bool, str],
        Tuple[Dict[str, Any], int, int]
    ],
    method: str,
    input_dir: str = "",
    processes: Optional[int] = None,
    skip_invalid: bool = True,
    save_api_info: bool = False
) -> Tuple[List[Dict[str, Any]], int, int]:
    """
    Processes a list of data rows using multiprocessing, applying a row_function to each row.

    Each row is passed to a wrapper function that supplies additional context like the API key,
    method, input directory, and flags for error handling and API info saving.

    Args:
        data (List[Dict[str, Any]]): List of input rows (each as a dictionary).
        api_key (str): API key used by the row processing function (e.g., for route services).
        row_function (Callable): Function to apply to each row. Must accept a tuple of 
            (row, api_key, save_api_info) and keyword args: method, skip_invalid, input_dir.
        method (str): Routing method to use, e.g., "google" or "graphhopper".
        input_dir (str, optional): Path to input directory containing reference data or files.
        processes (Optional[int], optional): Number of parallel worker processes. Defaults to CPU count.
        skip_invalid (bool, optional): If True, skips rows that raise errors. If False, raises on error.
        save_api_info (bool, optional): If True, saves the raw API response along with row output.

    Returns:
        Tuple[List[Dict[str, Any]], int, int]:
            - List of successfully processed rows (as dictionaries).
            - Total number of API calls made.
            - Total number of API-related errors encountered.
    """
    args = [
        (row, api_key, row_function, input_dir, skip_invalid, save_api_info, method)
        for row in data
    ]

    processed_rows: List[Dict[str, Any]] = []
    total_api_calls = 0
    total_api_errors = 0
    processed_count = 0

    try:
        with Pool(processes=processes) as pool:
            for result in pool.imap_unordered(wrap_row, args):
                if result is None:
                    continue
                row_result, api_calls, api_errors = result
                processed_rows.append(row_result)
                total_api_calls += api_calls
                total_api_errors += api_errors
                processed_count += 1
                print(f"[INFO] Processed {processed_count} row(s)...")

    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Keyboard interrupt received. Returning partial results...")

    return processed_rows, total_api_calls, total_api_errors

def process_row_overlap(row_and_api_key_and_flag, method, skip_invalid=True, input_dir=""):
    """
    Processes one pair of routes, finds overlap, segments travel, and handles errors based on skip_invalid.

    Args:
        row_and_api_key_and_flag (tuple): (row, api_key, save_api_info)
        method (str): "google" or "graphhopper"
        skip_invalid (bool): If True, skips rows with errors; if False, raises an error.
        input_dir (str): Directory containing the folder of the input CSV file.

    Returns:
        tuple: (result_dict, api_calls, api_errors)
    """
    row, api_key, save_api_info = row_and_api_key_and_flag
    api_calls = 0

    try:
        ID = row["ID"]
        origin_a, destination_a = row["OriginA"], row["DestinationA"]
        origin_b, destination_b = row["OriginB"], row["DestinationB"]

        # Split "lat,lon" into separate variables for each endpoint
        origin_a_lat, origin_a_lon = map(str.strip, origin_a.split(","))
        destination_a_lat, destination_a_lon = map(str.strip, destination_a.split(","))
        origin_b_lat, origin_b_lon = map(str.strip, origin_b.split(","))
        destination_b_lat, destination_b_lon = map(str.strip, destination_b.split(","))

        if origin_a == origin_b and destination_a == destination_b:
            api_calls += 1
            coordinates_a, a_dist, a_time = get_route_data(origin_a, destination_a, method, api_key, save_api_info)
            plot_routes(coordinates_a, [], (), (), ID, input_dir)
            # Return structured full overlap result as a dictionary, along with API stats
            return (
                FullOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=a_dist,
                    aTime=a_time,
                    bDist=a_dist,           
                    bTime=a_time,
                    overlapDist=a_dist,
                    overlapTime=a_time,
                    aBeforeDist=0.0,
                    aBeforeTime=0.0,
                    bBeforeDist=0.0,
                    bBeforeTime=0.0,
                    aAfterDist=0.0,
                    aAfterTime=0.0,
                    bAfterDist=0.0,
                    bAfterTime=0.0,
                ).model_dump(),
                api_calls,
                0  # no error flag
            )
        
        api_calls += 1
        coordinates_a, total_distance_a, total_time_a = get_route_data(origin_a, destination_a, method, api_key, save_api_info)
        api_calls += 1
        coordinates_b, total_distance_b, total_time_b = get_route_data(origin_b, destination_b, method, api_key, save_api_info)

        first_common_node, last_common_node = find_common_nodes(coordinates_a, coordinates_b)

        if not first_common_node or not last_common_node:
            plot_routes(coordinates_a, coordinates_b, (), (), ID, input_dir)
            return (
                FullOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=total_distance_a,
                    aTime=total_time_a,
                    bDist=total_distance_b,
                    bTime=total_time_b,
                    overlapDist=0.0,
                    overlapTime=0.0,
                    aBeforeDist=0.0,
                    aBeforeTime=0.0,
                    bBeforeDist=0.0,
                    bBeforeTime=0.0,
                    aAfterDist=0.0,
                    aAfterTime=0.0,
                    bAfterDist=0.0,
                    bAfterTime=0.0,
                ).model_dump(),
                api_calls,
                0
            )

        before_a, overlap_a, after_a = split_segments(coordinates_a, first_common_node, last_common_node)
        before_b, overlap_b, after_b = split_segments(coordinates_b, first_common_node, last_common_node)

        api_calls += 1
        start_time = time.time()
        _, before_a_distance, before_a_time = get_route_data(origin_a, f"{before_a[-1][0]},{before_a[-1][1]}", method, api_key, save_api_info)
        logging.info(f"Time for before_a API call: {time.time() - start_time:.2f} seconds")

        api_calls += 1
        start_time = time.time()
        _, overlap_a_distance, overlap_a_time = get_route_data(
            f"{overlap_a[0][0]},{overlap_a[0][1]}", f"{overlap_a[-1][0]},{overlap_a[-1][1]}", method, api_key, save_api_info)
        logging.info(f"Time for overlap_a API call: {time.time() - start_time:.2f} seconds")

        api_calls += 1
        start_time = time.time()
        _, after_a_distance, after_a_time = get_route_data(f"{after_a[0][0]},{after_a[0][1]}", destination_a, method, api_key, save_api_info)
        logging.info(f"Time for after_a API call: {time.time() - start_time:.2f} seconds")

        api_calls += 1
        start_time = time.time()
        _, before_b_distance, before_b_time = get_route_data(origin_b, f"{before_b[-1][0]},{before_b[-1][1]}", method, api_key, save_api_info)
        logging.info(f"Time for before_b API call: {time.time() - start_time:.2f} seconds")

        api_calls += 1
        start_time = time.time()
        _, after_b_distance, after_b_time = get_route_data(f"{after_b[0][0]},{after_b[0][1]}", destination_b, method, api_key, save_api_info)
        logging.info(f"Time for after_b API call: {time.time() - start_time:.2f} seconds")

        plot_routes(coordinates_a, coordinates_b, first_common_node, last_common_node, ID, input_dir)

        return (
            FullOverlapResult(
                ID=ID,
                OriginAlat=origin_a_lat,
                OriginAlong=origin_a_lon,
                DestinationAlat=destination_a_lat,
                DestinationAlong=destination_a_lon,
                OriginBlat=origin_b_lat,
                OriginBlong=origin_b_lon,
                DestinationBlat=destination_b_lat,
                DestinationBlong=destination_b_lon,
                aDist=total_distance_a,
                aTime=total_time_a,
                bDist=total_distance_b,
                bTime=total_time_b,
                overlapDist=overlap_a_distance,
                overlapTime=overlap_a_time,
                aBeforeDist=before_a_distance,
                aBeforeTime=before_a_time,
                bBeforeDist=before_b_distance,
                bBeforeTime=before_b_time,
                aAfterDist=after_a_distance if after_a else 0.0,
                aAfterTime=after_a_time if after_a else 0.0,
                bAfterDist=after_b_distance if after_b else 0.0,
                bAfterTime=after_b_time if after_b else 0.0,
            ).model_dump(),
            api_calls,
            0
        )

    except Exception as e:
        if skip_invalid:
            logging.error(f"Error in process_row_overlap for row {row}: {str(e)}")
            ID = row.get("ID", "")
            origin_a_lat, origin_a_lon = safe_split(row.get("OriginA", ""))
            destination_a_lat, destination_a_lon = safe_split(row.get("DestinationA", ""))
            origin_b_lat, origin_b_lon = safe_split(row.get("OriginB", ""))
            destination_b_lat, destination_b_lon = safe_split(row.get("DestinationB", ""))
            return (
                FullOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=None,
                    aTime=None,
                    bDist=None,
                    bTime=None,
                    overlapDist=None,
                    overlapTime=None,
                    aBeforeDist=None,
                    aBeforeTime=None,
                    bBeforeDist=None,
                    bBeforeTime=None,
                    aAfterDist=None,
                    aAfterTime=None,
                    bAfterDist=None,
                    bAfterTime=None,
                ).model_dump(),
                api_calls,
                1
            )

        else:
            raise


def process_routes_with_csv(
    csv_file: str,
    input_dir: str,
    api_key: str,
    home_a_lat: str,
    home_a_lon: str,
    work_a_lat: str,
    work_a_lon: str,
    home_b_lat: str,
    home_b_lon: str,
    work_b_lat: str,
    work_b_lon: str,
    id_column: Optional[str] = None,
    method: str = "google",
    output_csv: str = "output.csv",
    skip_invalid: bool = True,
    save_api_info: bool = False
) -> Tuple[List[Dict[str, any]], int, int, int]:
    """
    Processes route pairs from a CSV file using a row-processing function and writes results to a new CSV file.

    This function:
    - Reads route origin/destination pairs from a CSV file.
    - Maps the user-provided column names to standard labels.
    - Optionally skips or halts on invalid coordinate entries.
    - Uses multithreading.
    - Writes the processed route data to an output CSV file.

    Parameters:
    - csv_file (str): Name of the input CSV file containing the route pairs.
    - input_dir (str): Directory where the CSV file is located.
    - api_key (str): Google Maps API key used for fetching travel route data.
    - home_a_lat : Column name for the latitude of home A.
    - home_a_lon : Column name for the longitude of home A.
    - work_a_lat : Column name for the latitude of work A.
    - work_a_lon : Column name for the longitude of work A.
    - home_b_lat : Column name for the latitude of home B.
    - home_b_lon : Column name for the longitude of home B.
    - work_b_lat : Column name for the latitude of work B.
    - work_b_lon : Column name for the longitude of work B.
    - id_column : Column name for the unique ID of each row. If None or not found, IDs are auto-generated as R1, R2, ...
    - method (str): Routing method to use, either "google" or "graphhopper".
    - output_csv (str): File path for saving the output CSV file (default: "output.csv").
    - skip_invalid (bool): If True (default), invalid rows are logged and skipped; if False, processing halts on the first invalid row.
    - save_api_info (bool): If True, API responses are saved; if False, API responses are not saved.

    Returns:
    - tuple: (
        results (list of dicts),
        pre_api_error_count (int),
        total_api_calls (int),
        total_api_errors (int)
      )
    """
    data, pre_api_error_count = read_csv_file(
        csv_file=csv_file,
        input_dir=input_dir,
        home_a_lat=home_a_lat,
        home_a_lon=home_a_lon,
        work_a_lat=work_a_lat,
        work_a_lon=work_a_lon,
        home_b_lat=home_b_lat,
        home_b_lon=home_b_lon,
        work_b_lat=work_b_lat,
        work_b_lon=work_b_lon,
        id_column=id_column,
        skip_invalid=skip_invalid
    )

    results, total_api_calls, total_api_errors = process_rows(
        data, api_key, process_row_overlap, method=method, input_dir=input_dir, skip_invalid=skip_invalid, save_api_info=save_api_info
    )

    fieldnames = [
        "ID", "OriginAlat", "OriginAlong", "DestinationAlat", "DestinationAlong", 
        "OriginBlat", "OriginBlong", "DestinationBlat", "DestinationBlong",
        "aDist", "aTime", "bDist", "bTime",
        "overlapDist", "overlapTime",
        "aBeforeDist", "aBeforeTime", "bBeforeDist", "bBeforeTime",
        "aAfterDist", "aAfterTime", "bAfterDist", "bAfterTime",
    ]

    write_csv_file(input_dir, results, fieldnames, output_csv)

    return results, pre_api_error_count, total_api_calls, total_api_errors


def process_row_only_overlap(row_api_and_flag, method, skip_invalid=True, input_dir=""):
    """
    Processes a single route pair to compute overlapping travel segments.

    Returns:
    - result_dict (dict): Metrics including distances, times, and overlaps
    - api_calls (int): Number of API calls made for this row
    - api_errors (int): 1 if an exception occurred during processing; 0 otherwise
    """
    row, api_key, save_api_info = row_api_and_flag
    api_calls = 0

    try:
        ID = row["ID"]
        origin_a, destination_a = row["OriginA"], row["DestinationA"]
        origin_b, destination_b = row["OriginB"], row["DestinationB"]

        # Split and convert to float
        origin_a_lat, origin_a_lon = map(float, map(str.strip, origin_a.split(",")))
        destination_a_lat, destination_a_lon = map(float, map(str.strip, destination_a.split(",")))
        origin_b_lat, origin_b_lon = map(float, map(str.strip, origin_b.split(",")))
        destination_b_lat, destination_b_lon = map(float, map(str.strip, destination_b.split(",")))

        if origin_a == origin_b and destination_a == destination_b:
            api_calls += 1
            coordinates_a, a_dist, a_time = get_route_data(origin_a, destination_a, method, api_key, save_api_info)
            plot_routes(coordinates_a, [], (), (), ID, input_dir)
            return (
                SimpleOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=a_dist,
                    aTime=a_time,
                    bDist=a_dist,
                    bTime=a_time,
                    overlapDist=a_dist,
                    overlapTime=a_time,
                ).model_dump(),
                api_calls,
                0
            )

        api_calls += 1
        coordinates_a, total_distance_a, total_time_a = get_route_data(origin_a, destination_a, method, api_key, save_api_info)
        api_calls += 1
        coordinates_b, total_distance_b, total_time_b = get_route_data(origin_b, destination_b, method, api_key, save_api_info)

        first_common_node, last_common_node = find_common_nodes(coordinates_a, coordinates_b)

        if not first_common_node or not last_common_node:
            plot_routes(coordinates_a, coordinates_b, (), (), ID, input_dir)
            return (
                SimpleOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=total_distance_a,
                    aTime=total_time_a,
                    bDist=total_distance_b,
                    bTime=total_time_b,
                    overlapDist=0.0,
                    overlapTime=0.0,
                ).model_dump(),
                api_calls,
                0
            )

        before_a, overlap_a, after_a = split_segments(coordinates_a, first_common_node, last_common_node)
        before_b, overlap_b, after_b = split_segments(coordinates_b, first_common_node, last_common_node)

        api_calls += 1
        start_time = time.time()
        _, overlap_a_distance, overlap_a_time = get_route_data(
            f"{overlap_a[0][0]},{overlap_a[0][1]}",
            f"{overlap_a[-1][0]},{overlap_a[-1][1]}",
            method,
            api_key,
            save_api_info
        )
        logging.info(f"API call for overlap_a took {time.time() - start_time:.2f} seconds")

        overlap_b_distance, overlap_b_time = overlap_a_distance, overlap_a_time

        plot_routes(coordinates_a, coordinates_b, first_common_node, last_common_node, ID, input_dir)

        return (
            SimpleOverlapResult(
                ID=ID,
                OriginAlat=origin_a_lat,
                OriginAlong=origin_a_lon,
                DestinationAlat=destination_a_lat,
                DestinationAlong=destination_a_lon,
                OriginBlat=origin_b_lat,
                OriginBlong=origin_b_lon,
                DestinationBlat=destination_b_lat,
                DestinationBlong=destination_b_lon,
                aDist=total_distance_a,
                aTime=total_time_a,
                bDist=total_distance_b,
                bTime=total_time_b,
                overlapDist=overlap_a_distance,
                overlapTime=overlap_a_time,
            ).model_dump(),
            api_calls,
            0
        )

    except Exception as e:
        if skip_invalid:
            logging.error(f"Error processing row {row}: {str(e)}")
            ID = row.get("ID", "")
            origin_a_lat, origin_a_lon = safe_split(row.get("OriginA", ""))
            destination_a_lat, destination_a_lon = safe_split(row.get("DestinationA", ""))
            origin_b_lat, origin_b_lon = safe_split(row.get("OriginB", ""))
            destination_b_lat, destination_b_lon = safe_split(row.get("DestinationB", ""))

            return (
                SimpleOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=None,
                    aTime=None,
                    bDist=None,
                    bTime=None,
                    overlapDist=None,
                    overlapTime=None,
                ).model_dump(),
                api_calls,
                1
            )
        else:
            raise

def process_routes_only_overlap_with_csv(
    csv_file: str,
    input_dir: str,
    api_key: str,
    home_a_lat: str,
    home_a_lon: str,
    work_a_lat: str,
    work_a_lon: str,
    home_b_lat: str,
    home_b_lon: str,
    work_b_lat: str,
    work_b_lon: str,
    id_column: Optional[str] = None,
    method: str = "google",
    output_csv: str = "output.csv",
    skip_invalid: bool = True,
    save_api_info: bool = False
) -> tuple:
    """
    Processes all route pairs in a CSV to compute overlaps only.

    Returns:
    - results (list): List of processed route dictionaries
    - pre_api_error_count (int): Number of invalid rows skipped before API calls
    - api_call_count (int): Total number of API calls made
    - post_api_error_count (int): Number of errors encountered during processing
    """
    data, pre_api_error_count = read_csv_file(
        csv_file=csv_file,
        input_dir=input_dir,
        home_a_lat=home_a_lat,
        home_a_lon=home_a_lon,
        work_a_lat=work_a_lat,
        work_a_lon=work_a_lon,
        home_b_lat=home_b_lat,
        home_b_lon=home_b_lon,
        work_b_lat=work_b_lat,
        work_b_lon=work_b_lon,
        id_column=id_column,
        skip_invalid=skip_invalid
    )

    results, api_call_count, post_api_error_count = process_rows(
        data, api_key, process_row_only_overlap, method, input_dir, skip_invalid=skip_invalid, save_api_info=save_api_info
    )

    fieldnames = [
        "ID", "OriginAlat", "OriginAlong", "DestinationAlat", "DestinationAlong", 
        "OriginBlat", "OriginBlong", "DestinationBlat", "DestinationBlong",
        "aDist", "aTime", "bDist", "bTime",
        "overlapDist", "overlapTime",
    ]
    write_csv_file(input_dir, results, fieldnames, output_csv)

    return results, pre_api_error_count, api_call_count, post_api_error_count

def wrap_row_multiproc(args):
    """
    Wraps a single row-processing task for use with multiprocessing or multithreading pools.

    This function unpacks the arguments needed to process a single row of data in parallel.
    It supports passing additional arguments (such as input_dir) to the row-processing function.
    If extra arguments are provided, the first is assumed to be input_dir and is passed as a keyword argument.

    Args:
        args (tuple): A tuple containing:
            - row (dict): The data row to process.
            - api_key (str): API key for route data fetching.
            - row_function (callable): The function to process the row.
            - skip_invalid (bool): Whether to skip or raise on error.
            - save_api_info (bool): Whether to save the Google API response.
            - *extra_args: Additional arguments.

    Returns:
        tuple or None: The result of processing the row (e.g., (result_dict, api_calls, api_errors)),
                       or None if the row is skipped due to an error.
    """
    row, api_key, row_function, skip_invalid, save_api_info, *extra_args = args
    return row_function(row, api_key, *extra_args, skip_invalid, save_api_info)

def process_rows_multiproc(
    data,
    api_key,
    row_function,
    processes=None,
    extra_args=(),
    skip_invalid=True,
    save_api_info=False
):
    """
    Processes rows using multithreading and aggregates API call/error counts.

    Returns:
    - results (list): List of processed result dicts
    - api_call_count (int): Total number of API calls across all rows
    - api_error_count (int): Total number of API errors across all rows
    """
    args = [
        (row, api_key, row_function, skip_invalid, save_api_info, *extra_args)
        for row in data
    ]

    processed_rows = []
    api_call_count = 0
    api_error_count = 0
    processed_count = 0

    try:
        with Pool(processes=processes) as pool:
            for result in pool.imap_unordered(wrap_row_multiproc, args):
                if result is None:
                    continue
                row_result, row_api_calls, row_api_errors = result
                processed_rows.append(row_result)
                api_call_count += row_api_calls
                api_error_count += row_api_errors
                processed_count += 1
                print(f"[INFO] Processed {processed_count} row(s)...")

    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Keyboard interrupt received. Returning partial results...")

    return processed_rows, api_call_count, api_error_count

def process_row_overlap_rec_multiproc(
    row: Dict[str, str],
    api_key: str,
    width: int,
    threshold: int,
    method: str,
    input_dir: str,
    skip_invalid: bool,
    save_api_info: bool
) -> Tuple[Dict[str, Any], int, int]:
    """
    Processes a single row using the rectangular overlap method.

    This version includes error handling via the skip_invalid flag:
    - If skip_invalid is True, errors are logged and the row is skipped.
    - If False, exceptions are raised to halt processing.

    Tracks the number of API calls and any errors encountered during processing.

    Args:
        row_and_args (tuple): A tuple containing:
            - row (dict): Route data with OriginA/B and DestinationA/B
            - api_key (str): Google Maps API key
            - width (int): Width for rectangular overlap
            - threshold (int): Overlap filtering threshold
            - skip_invalid (bool): Whether to log and skip or raise on errors
            - save_api_info (bool): Whether to save the API response

    Returns:
        tuple:
            - result_dict (dict): Processed route metrics
            - api_calls (int): Number of API calls made during processing
            - api_errors (int): 1 if error occurred and was skipped; 0 otherwise
    """
    api_calls = 0

    try:
        ID = row["ID"]
        origin_a, destination_a = row["OriginA"], row["DestinationA"]
        origin_b, destination_b = row["OriginB"], row["DestinationB"]
        origin_a_lat, origin_a_lon = map(float, map(str.strip, origin_a.split(",")))
        destination_a_lat, destination_a_lon = map(float, map(str.strip, destination_a.split(",")))
        origin_b_lat, origin_b_lon = map(float, map(str.strip, origin_b.split(",")))
        destination_b_lat, destination_b_lon = map(float, map(str.strip, destination_b.split(",")))

        if origin_a == origin_b and destination_a == destination_b:
            api_calls += 1
            start_time = time.time()
            coordinates_a, a_dist, a_time = get_route_data(origin_a, destination_a, method, api_key, save_api_info)
            logging.info(f"Time for same-route API call: {time.time() - start_time:.2f} seconds")
            plot_routes(coordinates_a, [], (), (), ID, input_dir)
            return (
                FullOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=a_dist,
                    aTime=a_time,
                    bDist=a_dist,
                    bTime=a_time,
                    overlapDist=a_dist,
                    overlapTime=a_time,
                    aBeforeDist=0.0,
                    aBeforeTime=0.0,
                    bBeforeDist=0.0,
                    bBeforeTime=0.0,
                    aAfterDist=0.0,
                    aAfterTime=0.0,
                    bAfterDist=0.0,
                    bAfterTime=0.0,
                ).model_dump(),
                api_calls,
                0
            )

        api_calls += 1
        start_time = time.time()
        coordinates_a, total_distance_a, total_time_a = get_route_data(origin_a, destination_a, method, api_key, save_api_info)
        logging.info(f"Time for coordinates_a API call: {time.time() - start_time:.2f} seconds")

        api_calls += 1
        start_time = time.time()
        coordinates_b, total_distance_b, total_time_b = get_route_data(origin_b, destination_b, method, api_key, save_api_info)
        logging.info(f"Time for coordinates_b API call: {time.time() - start_time:.2f} seconds")

        first_common_node, last_common_node = find_common_nodes(coordinates_a, coordinates_b)

        if not first_common_node or not last_common_node:
            plot_routes(coordinates_a, coordinates_b, (), (), ID, input_dir)
            return (
                FullOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=total_distance_a,
                    aTime=total_time_a,
                    bDist=total_distance_b,
                    bTime=total_time_b,
                    overlapDist=0.0,
                    overlapTime=0.0,
                    aBeforeDist=0.0,
                    aBeforeTime=0.0,
                    bBeforeDist=0.0,
                    bBeforeTime=0.0,
                    aAfterDist=0.0,
                    aAfterTime=0.0,
                    bAfterDist=0.0,
                    bAfterTime=0.0,
                ).model_dump(),
                api_calls,
                0
            )


        before_a, overlap_a, after_a = split_segments(coordinates_a, first_common_node, last_common_node)
        before_b, overlap_b, after_b = split_segments(coordinates_b, first_common_node, last_common_node)

        a_segment_distances = calculate_segment_distances(before_a, after_a)
        b_segment_distances = calculate_segment_distances(before_b, after_b)

        rectangles_a = create_segment_rectangles(
            a_segment_distances["before_segments"] + a_segment_distances["after_segments"], width=width)
        rectangles_b = create_segment_rectangles(
            b_segment_distances["before_segments"] + b_segment_distances["after_segments"], width=width)

        filtered_combinations = filter_combinations_by_overlap(
            rectangles_a, rectangles_b, threshold=threshold)

        boundary_nodes = find_overlap_boundary_nodes(
            filtered_combinations, rectangles_a, rectangles_b)

        if (
            not boundary_nodes["first_node_before_overlap"]
            or not boundary_nodes["last_node_after_overlap"]
        ):
            boundary_nodes = {
                "first_node_before_overlap": {
                    "node_a": first_common_node,
                    "node_b": first_common_node,
                },
                "last_node_after_overlap": {
                    "node_a": last_common_node,
                    "node_b": last_common_node,
                },
            }

        api_calls += 1
        start_time = time.time()
        _, before_a_dist, before_a_time = get_route_data(
            origin_a,
            f"{boundary_nodes['first_node_before_overlap']['node_a'][0]},{boundary_nodes['first_node_before_overlap']['node_a'][1]}",
            method,
            api_key,
            save_api_info
        )
        logging.info(f"Time for before_a API call: {time.time() - start_time:.2f} seconds")

        api_calls += 1
        start_time = time.time()
        _, overlap_a_dist, overlap_a_time = get_route_data(
            f"{boundary_nodes['first_node_before_overlap']['node_a'][0]},{boundary_nodes['first_node_before_overlap']['node_a'][1]}",
            f"{boundary_nodes['last_node_after_overlap']['node_a'][0]},{boundary_nodes['last_node_after_overlap']['node_a'][1]}",
            method,
            api_key,
            save_api_info
        )
        logging.info(f"Time for overlap_a API call: {time.time() - start_time:.2f} seconds")

        api_calls += 1
        start_time = time.time()
        _, after_a_dist, after_a_time = get_route_data(
            f"{boundary_nodes['last_node_after_overlap']['node_a'][0]},{boundary_nodes['last_node_after_overlap']['node_a'][1]}",
            destination_a,
            method,
            api_key,
            save_api_info
        )
        logging.info(f"Time for after_a API call: {time.time() - start_time:.2f} seconds")

        api_calls += 1
        start_time = time.time()
        _, before_b_dist, before_b_time = get_route_data(
            origin_b,
            f"{boundary_nodes['first_node_before_overlap']['node_b'][0]},{boundary_nodes['first_node_before_overlap']['node_b'][1]}",
            method,
            api_key,
            save_api_info
        )
        logging.info(f"Time for before_b API call: {time.time() - start_time:.2f} seconds")

        api_calls += 1
        start_time = time.time()
        _, after_b_dist, after_b_time = get_route_data(
            f"{boundary_nodes['last_node_after_overlap']['node_b'][0]},{boundary_nodes['last_node_after_overlap']['node_b'][1]}",
            destination_b,
            method,
            api_key,
            save_api_info
        )
        logging.info(f"Time for after_b API call: {time.time() - start_time:.2f} seconds")

        plot_routes(coordinates_a, coordinates_b, first_common_node, last_common_node, ID, input_dir)

        return (
            FullOverlapResult(
                ID=ID,
                OriginAlat=origin_a_lat,
                OriginAlong=origin_a_lon,
                DestinationAlat=destination_a_lat,
                DestinationAlong=destination_a_lon,
                OriginBlat=origin_b_lat,
                OriginBlong=origin_b_lon,
                DestinationBlat=destination_b_lat,
                DestinationBlong=destination_b_lon,
                aDist=total_distance_a,
                aTime=total_time_a,
                bDist=total_distance_b,
                bTime=total_time_b,
                overlapDist=overlap_a_dist,
                overlapTime=overlap_a_time,
                aBeforeDist=before_a_dist,
                aBeforeTime=before_a_time,
                bBeforeDist=before_b_dist,
                bBeforeTime=before_b_time,
                aAfterDist=after_a_dist,
                aAfterTime=after_a_time,
                bAfterDist=after_b_dist,
                bAfterTime=after_b_time,
            ).model_dump(),
        api_calls,
        0
    )

    except Exception as e:
        if skip_invalid:
            logging.error(f"Error in process_row_overlap_rec_multiproc for row {row}: {str(e)}")
            ID = row.get("ID", "")
            origin_a_lat, origin_a_lon = safe_split(row.get("OriginA", ""))
            destination_a_lat, destination_a_lon = safe_split(row.get("DestinationA", ""))
            origin_b_lat, origin_b_lon = safe_split(row.get("OriginB", ""))
            destination_b_lat, destination_b_lon = safe_split(row.get("DestinationB", ""))

            return (
                FullOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=None,
                    aTime=None,
                    bDist=None,
                    bTime=None,
                    overlapDist=None,
                    overlapTime=None,
                    aBeforeDist=None,
                    aBeforeTime=None,
                    bBeforeDist=None,
                    bBeforeTime=None,
                    aAfterDist=None,
                    aAfterTime=None,
                    bAfterDist=None,
                    bAfterTime=None,
                ).model_dump(),
                api_calls,
                1
            )

        else:
            raise

def overlap_rec(
    csv_file: str,
    input_dir: str,
    api_key: str,
    home_a_lat: str,
    home_a_lon: str,
    work_a_lat: str,
    work_a_lon: str,
    home_b_lat: str,
    home_b_lon: str,
    work_b_lat: str,
    work_b_lon: str,
    id_column: Optional[str] = None,
    output_csv: str = "outputRec.csv",
    threshold: int = 50,
    width: int = 100,
    method: str = "google",
    skip_invalid: bool = True,
    save_api_info: bool = False
) -> tuple:
    """
    Processes routes using the rectangular overlap method with a defined threshold and width.

    Parameters:
    - csv_file (str): Name of the input CSV file.
    - input_dir (str): Directory where the CSV file is located.
    - api_key (str): Google API key for routing.
    - home_a_lat (str): Column name for the latitude of home A.
    - home_a_lon (str): Column name for the longitude of home A.
    - work_a_lat (str): Column name for the latitude of work A.
    - work_a_lon (str): Column name for the longitude of work A.
    - home_b_lat (str): Column name for the latitude of home B.
    - home_b_lon (str): Column name for the longitude of home B.
    - work_b_lat (str): Column name for the latitude of work B.
    - work_b_lon (str): Column name for the longitude of work B.
    - id_column (Optional[str]): Column name for the unique ID of each row. If None or not found, IDs are auto-generated as R1, R2, ...
    - output_csv (str): Path for the output CSV file.
    - threshold (int): Overlap threshold distance.
    - width (int): Buffer width for rectangular overlap.
    - method (str): Routing method to use, either "google" or "graphhopper".
    - skip_invalid (bool): If True, skips invalid rows and logs them.
    - save_api_info (bool): If True, save API response.

    Returns:
    - tuple: (
        results (list): Processed results with travel and overlap metrics,
        pre_api_error_count (int),
        api_call_count (int),
        post_api_error_count (int)
      )
    """
    # Step 1: Read input CSV
    data, pre_api_error_count = read_csv_file(
        csv_file=csv_file,
        input_dir=input_dir,
        home_a_lat=home_a_lat,
        home_a_lon=home_a_lon,
        work_a_lat=work_a_lat,
        work_a_lon=work_a_lon,
        home_b_lat=home_b_lat,
        home_b_lon=home_b_lon,
        work_b_lat=work_b_lat,
        work_b_lon=work_b_lon,
        id_column=id_column,
        skip_invalid=skip_invalid
    )

    # Step 2: Process with multiproc + interruption support
    processed_rows, api_call_count, post_api_error_count = process_rows_multiproc(
        data,
        api_key,
        row_function=process_row_overlap_rec_multiproc,  # Pass your actual processor here
        extra_args=(width, threshold, method, input_dir),
        skip_invalid=skip_invalid,
        save_api_info=save_api_info
    )

    # Step 3: Write if anything was processed
    if processed_rows:
        fieldnames = list(processed_rows[0].keys())
        write_csv_file(input_dir, processed_rows, fieldnames, output_csv)

    return processed_rows, pre_api_error_count, api_call_count, post_api_error_count

def process_row_only_overlap_rec(
    row: dict,
    api_key: str,
    width: float,
    threshold: float,
    method: str,
    input_dir: str,
    skip_invalid: bool,
    save_api_info: bool
):
    """
    Processes a single row to compute only the overlapping portion of two routes
    using the rectangular buffer approximation method.

    Args:
        row_and_args (tuple): A tuple containing:
            - row (dict): Contains "OriginA", "DestinationA", "OriginB", "DestinationB"
            - api_key (str): Google Maps API key
            - width (int): Width of buffer for overlap detection
            - threshold (int): Distance threshold for overlap detection
            - method (str): Routing method to use (e.g., "driving", "walking")
            - input_dir (str): Directory for saving output files
            - skip_invalid (bool): Whether to skip errors or halt on first error
            - save_api_info (bool): Whether to save the Google API response

    Returns:
        tuple:
            - dict: Dictionary of route and overlap metrics (or None values if error)
            - int: Number of API calls made
            - int: Number of errors encountered (0 or 1)
    """
    api_calls = 0
    try:
        ID = row["ID"]
        origin_a, destination_a = row["OriginA"], row["DestinationA"]
        origin_b, destination_b = row["OriginB"], row["DestinationB"]
        origin_a_lat, origin_a_lon = map(float, map(str.strip, origin_a.split(",")))
        destination_a_lat, destination_a_lon = map(float, map(str.strip, destination_a.split(",")))
        origin_b_lat, origin_b_lon = map(float, map(str.strip, origin_b.split(",")))
        destination_b_lat, destination_b_lon = map(float, map(str.strip, destination_b.split(",")))


        if origin_a == origin_b and destination_a == destination_b:
            api_calls += 1
            start_time = time.time()
            coordinates_a, a_dist, a_time = get_route_data(origin_a, destination_a, method, api_key, save_api_info=save_api_info)
            logging.info(f"Time for same-route API call: {time.time() - start_time:.2f} seconds")
            plot_routes(coordinates_a, [], (), (), ID, input_dir)
            return (
                SimpleOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=a_dist,
                    aTime=a_time,
                    bDist=a_dist,
                    bTime=a_time,
                    overlapDist=a_dist,
                    overlapTime=a_time,
                ).model_dump(),
                api_calls,
                0
            )

        api_calls += 1
        start_time = time.time()
        coordinates_a, total_distance_a, total_time_a = get_route_data(origin_a, destination_a, method, api_key, save_api_info=save_api_info)
        logging.info(f"Time for coordinates_a API call: {time.time() - start_time:.2f} seconds")

        api_calls += 1
        start_time = time.time()
        coordinates_b, total_distance_b, total_time_b = get_route_data(origin_b, destination_b, method, api_key, save_api_info=save_api_info)
        logging.info(f"Time for coordinates_b API call: {time.time() - start_time:.2f} seconds")

        first_common_node, last_common_node = find_common_nodes(coordinates_a, coordinates_b)

        if not first_common_node or not last_common_node:
            plot_routes(coordinates_a, coordinates_b, None, None, ID, input_dir)
            return (
                SimpleOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=total_distance_a,
                    aTime=total_time_a,
                    bDist=total_distance_b,
                    bTime=total_time_b,
                    overlapDist=0.0,
                    overlapTime=0.0,
                ).model_dump(),
                api_calls,
                0
            )

        before_a, overlap_a, after_a = split_segments(coordinates_a, first_common_node, last_common_node)
        before_b, overlap_b, after_b = split_segments(coordinates_b, first_common_node, last_common_node)

        a_segment_distances = calculate_segment_distances(before_a, after_a)
        b_segment_distances = calculate_segment_distances(before_b, after_b)

        rectangles_a = create_segment_rectangles(
            a_segment_distances["before_segments"] + a_segment_distances["after_segments"], width=width)
        rectangles_b = create_segment_rectangles(
            b_segment_distances["before_segments"] + b_segment_distances["after_segments"], width=width)

        filtered_combinations = filter_combinations_by_overlap(
            rectangles_a, rectangles_b, threshold=threshold)

        boundary_nodes = find_overlap_boundary_nodes(
            filtered_combinations, rectangles_a, rectangles_b)

        if (
            not boundary_nodes["first_node_before_overlap"]
            or not boundary_nodes["last_node_after_overlap"]
        ):
            boundary_nodes = {
                "first_node_before_overlap": {
                    "node_a": first_common_node,
                    "node_b": first_common_node,
                },
                "last_node_after_overlap": {
                    "node_a": last_common_node,
                    "node_b": last_common_node,
                },
            }

        api_calls += 1
        start_time = time.time()
        _, overlap_a_dist, overlap_a_time = get_route_data(
            f"{boundary_nodes['first_node_before_overlap']['node_a'][0]},{boundary_nodes['first_node_before_overlap']['node_a'][1]}",
            f"{boundary_nodes['last_node_after_overlap']['node_a'][0]},{boundary_nodes['last_node_after_overlap']['node_a'][1]}",
            method,
            api_key,
            save_api_info=save_api_info
        )
        logging.info(f"Time for overlap_a API call: {time.time() - start_time:.2f} seconds")

        api_calls += 1
        start_time = time.time()
        _, overlap_b_dist, overlap_b_time = get_route_data(
            f"{boundary_nodes['first_node_before_overlap']['node_b'][0]},{boundary_nodes['first_node_before_overlap']['node_b'][1]}",
            f"{boundary_nodes['last_node_after_overlap']['node_b'][0]},{boundary_nodes['last_node_after_overlap']['node_b'][1]}",
            method,
            api_key,
            save_api_info=save_api_info
        )
        logging.info(f"Time for overlap_b API call: {time.time() - start_time:.2f} seconds")

        plot_routes(coordinates_a, coordinates_b, first_common_node, last_common_node, ID, input_dir)

        return (
            SimpleOverlapResult(
                ID=ID,
                OriginAlat=origin_a_lat,
                OriginAlong=origin_a_lon,
                DestinationAlat=destination_a_lat,
                DestinationAlong=destination_a_lon,
                OriginBlat=origin_b_lat,
                OriginBlong=origin_b_lon,
                DestinationBlat=destination_b_lat,
                DestinationBlong=destination_b_lon,
                aDist=total_distance_a,
                aTime=total_time_a,
                bDist=total_distance_b,
                bTime=total_time_b,
                overlapDist=overlap_a_dist,
                overlapTime=overlap_a_time,
            ).model_dump(),
            api_calls,
            0
        )

    except Exception as e:
        if skip_invalid:
            logging.error(f"Error processing row {row}: {str(e)}")
            ID = row.get("ID", "")
            origin_a_lat, origin_a_lon = safe_split(row.get("OriginA", ""))
            destination_a_lat, destination_a_lon = safe_split(row.get("DestinationA", ""))
            origin_b_lat, origin_b_lon = safe_split(row.get("OriginB", ""))
            destination_b_lat, destination_b_lon = safe_split(row.get("DestinationB", ""))

            return (
                SimpleOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=None,
                    aTime=None,
                    bDist=None,
                    bTime=None,
                    overlapDist=None,
                    overlapTime=None,
                ).model_dump(),
                api_calls,
                1
            )

        else:
            raise

def only_overlap_rec(
    csv_file: str,
    input_dir: str,
    api_key: str,
    home_a_lat: str,
    home_a_lon: str,
    work_a_lat: str,
    work_a_lon: str,
    home_b_lat: str,
    home_b_lon: str,
    work_b_lat: str,
    work_b_lon: str,
    id_column: Optional[str] = None,
    output_csv: str = "outputRec.csv",
    threshold: float = 50,
    width: float = 100,
    method: str = "google",
    skip_invalid: bool = True,
    save_api_info: bool = False
) -> tuple:
    """
    Processes routes to compute only the overlapping rectangular segments based on a threshold and width.

    Parameters:
    - csv_file (str): Name of the input CSV file.
    - input_dir (str): Directory where the CSV file is located.
    - api_key (str): Google API key for route requests.
    - home_a_lat (str): Column name for the latitude of home A.
    - home_a_lon (str): Column name for the longitude of home A.
    - work_a_lat (str): Column name for the latitude of work A.
    - work_a_lon (str): Column name for the longitude of work A.
    - home_b_lat (str): Column name for the latitude of home B.
    - home_b_lon (str): Column name for the longitude of home B.
    - work_b_lat (str): Column name for the latitude of work B.
    - work_b_lon (str): Column name for the longitude of work B.
    - id_column (Optional[str]): Column name for the unique ID of each row. If None or not found, IDs are auto-generated as R1, R2, ...
    - output_csv (str): Output path for results.
    - threshold (float): Distance threshold for overlap detection.
    - width (float): Width of the rectangular overlap zone.
    - method (str): Routing method to use ("google" or "graphhopper").
    - skip_invalid (bool): If True, skips rows with invalid input and logs them.
    - save_api_info (bool): If True, saves API response.

    Returns:
    - tuple: (
        results (list): Processed results with overlap metrics only,
        pre_api_error_count (int),
        api_call_count (int),
        post_api_error_count (int)
      )
    """
    # Step 1: Read input CSV
    data, pre_api_error_count = read_csv_file(
        csv_file=csv_file,
        input_dir=input_dir,
        home_a_lat=home_a_lat,
        home_a_lon=home_a_lon,
        work_a_lat=work_a_lat,
        work_a_lon=work_a_lon,
        home_b_lat=home_b_lat,
        home_b_lon=home_b_lon,
        work_b_lat=work_b_lat,
        work_b_lon=work_b_lon,
        id_column=id_column,
        skip_invalid=skip_invalid
    )

    # Step 2: Process rows with keyboard interrupt support
    processed_rows, api_call_count, post_api_error_count = process_rows_multiproc(
        data=data,
        api_key=api_key,
        row_function=process_row_only_overlap_rec,
        extra_args=(width, threshold, method, input_dir),
        skip_invalid=skip_invalid,
        save_api_info=save_api_info
    )

    # Step 3: Write results if any were processed
    if processed_rows:
        fieldnames = list(processed_rows[0].keys())
        write_csv_file(input_dir, processed_rows, fieldnames, output_csv)

    return processed_rows, pre_api_error_count, api_call_count, post_api_error_count

def process_row_route_buffers(row_and_args):
    """
    Processes a single row to compute route buffers and their intersection ratios.

    This function:
    - Retrieves route data for two routes (A and B).
    - Creates buffered polygons around each route using a specified buffer distance.
    - Computes the intersection area between the buffers.
    - Calculates and returns the intersection ratios for both routes.
    - Handles trivial routes where origin equals destination.
    - Plots the routes and their buffers.
    - Optionally logs and skips invalid rows based on `skip_invalid`.

    Args:
        row_and_args (tuple): Contains:
            - row (dict): Dictionary with OriginA, DestinationA, OriginB, DestinationB
            - api_key (str): Google Maps API key
            - buffer_distance (float): Distance in meters for route buffering
            - skip_invalid (bool): Whether to skip and log errors or raise them
            - save_api_info (bool): Whether to save the Google API response
            - input_dir (str): Directory where input files are located
            - method (str): Routing method to use (e.g., "driving", "walking")
        

    Returns:
        tuple:
            - dict: Metrics for the route pair
            - int: Number of API calls made
            - int: 1 if skipped due to error, else 0
    """
    row, api_key, buffer_distance, skip_invalid, save_api_info, input_dir, method = row_and_args
    api_calls = 0

    try:
        ID = row["ID"]
        origin_a, destination_a = row["OriginA"], row["DestinationA"]
        origin_b, destination_b = row["OriginB"], row["DestinationB"]
        # Split and convert to float
        origin_a_lat, origin_a_lon = map(float, map(str.strip, origin_a.split(",")))
        destination_a_lat, destination_a_lon = map(float, map(str.strip, destination_a.split(",")))
        origin_b_lat, origin_b_lon = map(float, map(str.strip, origin_b.split(",")))
        destination_b_lat, destination_b_lon = map(float, map(str.strip, destination_b.split(",")))

        if origin_a == destination_a and origin_b == destination_b:
            return (
                IntersectionRatioResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=0,
                    aTime=0,
                    bDist=0,
                    bTime=0,
                    aIntersecRatio=0.0,
                    bIntersecRatio=0.0,
                ).model_dump(),
                api_calls,
                0
            )

        if origin_a == destination_a and origin_b != destination_b:
            api_calls += 1
            route_b_coords, b_dist, b_time = get_route_data(origin_b, destination_b, method, api_key, save_api_info=save_api_info)
            return (
                IntersectionRatioResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=0,
                    aTime=0,
                    bDist=b_dist,
                    bTime=b_time,
                    aIntersecRatio=0.0,
                    bIntersecRatio=0.0,
                ).model_dump(),
                api_calls,
                0
            )

        if origin_a != destination_a and origin_b == destination_b:
            api_calls += 1
            route_a_coords, a_dist, a_time = get_route_data(origin_a, destination_a, method, api_key, save_api_info=save_api_info)
            return (
                IntersectionRatioResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=a_dist,
                    aTime=a_time,
                    bDist=0,
                    bTime=0,
                    aIntersecRatio=0.0,
                    bIntersecRatio=0.0,
                ).model_dump(),
                api_calls,
                0
            )

        api_calls += 1
        route_a_coords, a_dist, a_time = get_route_data(origin_a, destination_a, method, api_key, save_api_info=save_api_info)

        api_calls += 1
        route_b_coords, b_dist, b_time = get_route_data(origin_b, destination_b, method, api_key, save_api_info=save_api_info)

        if origin_a == origin_b and destination_a == destination_b:
            buffer_a = create_buffered_route(route_a_coords, buffer_distance)
            buffer_b = buffer_a
            plot_routes_and_buffers(route_a_coords, route_b_coords, buffer_a, buffer_b, ID, input_dir)
            return (
                IntersectionRatioResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=a_dist,
                    aTime=a_time,
                    bDist=a_dist,
                    bTime=a_time,
                    aIntersecRatio=1.0,
                    bIntersecRatio=1.0,
                ).model_dump(),
                api_calls,
                0
            )

        buffer_a = create_buffered_route(route_a_coords, buffer_distance)
        buffer_b = create_buffered_route(route_b_coords, buffer_distance)

        start_time = time.time()
        intersection = buffer_a.intersection(buffer_b)
        logging.info(f"Time to compute buffer intersection of A and B: {time.time() - start_time:.6f} seconds")

        plot_routes_and_buffers(route_a_coords, route_b_coords, buffer_a, buffer_b, ID, input_dir)

        if intersection.is_empty:
            return (
                IntersectionRatioResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=a_dist,
                    aTime=a_time,
                    bDist=b_dist,
                    bTime=b_time,
                    aIntersecRatio=0.0,
                    bIntersecRatio=0.0,
                ).model_dump(),
                api_calls,
                0
            )

        intersection_area = intersection.area
        a_area = buffer_a.area
        b_area = buffer_b.area
        a_intersec_ratio = intersection_area / a_area
        b_intersec_ratio = intersection_area / b_area

        return (
            IntersectionRatioResult(
                ID=ID,
                OriginAlat=origin_a_lat,
                OriginAlong=origin_a_lon,
                DestinationAlat=destination_a_lat,
                DestinationAlong=destination_a_lon,
                OriginBlat=origin_b_lat,
                OriginBlong=origin_b_lon,
                DestinationBlat=destination_b_lat,
                DestinationBlong=destination_b_lon,
                aDist=a_dist,
                aTime=a_time,
                bDist=b_dist,
                bTime=b_time,
                aIntersecRatio=a_intersec_ratio,
                bIntersecRatio=b_intersec_ratio,
            ).model_dump(),
            api_calls,
            0
        )

    except Exception as e:
        if skip_invalid:
            logging.error(f"Error processing row {row}: {str(e)}")
            ID = row.get("ID", "")
            origin_a_lat, origin_a_lon = safe_split(row.get("OriginA", ""))
            destination_a_lat, destination_a_lon = safe_split(row.get("DestinationA", ""))
            origin_b_lat, origin_b_lon = safe_split(row.get("OriginB", ""))
            destination_b_lat, destination_b_lon = safe_split(row.get("DestinationB", ""))

            return (
                IntersectionRatioResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=None,
                    aTime=None,
                    bDist=None,
                    bTime=None,
                    aIntersecRatio=None,
                    bIntersecRatio=None,
                ).model_dump(),
                api_calls,
                1
            )

        else:
            raise

def process_routes_with_buffers(
    csv_file: str,
    input_dir: str,
    api_key: str,
    output_csv: str,
    home_a_lat: str,
    home_a_lon: str,
    work_a_lat: str,
    work_a_lon: str,
    home_b_lat: str,
    home_b_lon: str,
    work_b_lat: str,
    work_b_lon: str,
    id_column: Optional[str] = None,
    buffer_distance: float = 100,
    method: str = "google",
    skip_invalid: bool = True,
    save_api_info: bool = False
) -> tuple:
    """
    Processes two routes from a CSV file to compute buffer intersection ratios.

    Parameters:
    - csv_file (str): Name of the input CSV file.
    - input_dir (str): Directory where the CSV file is located.
    - output_csv (str): Output file for writing the results.
    - api_key (str): Google API key for route data.
    - home_a_lat (str): Column name for the latitude of home A.
    - home_a_lon (str): Column name for the longitude of home A.
    - work_a_lat (str): Column name for the latitude of work A.
    - work_a_lon (str): Column name for the longitude of work A.
    - home_b_lat (str): Column name for the latitude of home B.
    - home_b_lon (str): Column name for the longitude of home B.
    - work_b_lat (str): Column name for the latitude of work B.
    - work_b_lon (str): Column name for the longitude of work B.
    - id_column (Optional[str]): Column name for the unique ID of each row. If None or not found, IDs are auto-generated as R1, R2, ...
    - buffer_distance (float): Distance in meters for buffering each route.
    - method (str): Routing method to use ("google" or "graphhopper).
    - skip_invalid (bool): If True, skips invalid rows and logs them instead of halting.
    - save_api_info (bool): If True, saves API response.

    Returns:
    - tuple: (
        results (list of dicts),
        pre_api_error_count (int),
        total_api_calls (int),
        post_api_error_count (int)
    )
    """
    data, pre_api_error_count = read_csv_file(
        csv_file=csv_file,
        input_dir=input_dir,
        home_a_lat=home_a_lat,
        home_a_lon=home_a_lon,
        work_a_lat=work_a_lat,
        work_a_lon=work_a_lon,
        home_b_lat=home_b_lat,
        home_b_lon=home_b_lon,
        work_b_lat=work_b_lat,
        work_b_lon=work_b_lon,
        id_column=id_column,
        skip_invalid=skip_invalid
    )

    args = [(row, api_key, buffer_distance, skip_invalid, save_api_info, input_dir, method) for row in data]
    
    results = []
    total_api_calls = 0
    post_api_error_count = 0
    processed_count = 0

    try:
        with Pool() as pool:
            for result in pool.imap_unordered(process_row_route_buffers, args):
                if result is None:
                    continue
                result_dict, api_calls, api_errors = result
                results.append(result_dict)
                total_api_calls += api_calls
                post_api_error_count += api_errors
                processed_count += 1
                print(f"[INFO] Processed {processed_count} row(s)...")
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Keyboard interrupt received. Writing partial results...")

    if results:
        fieldnames = [
            "ID", "OriginAlat", "OriginAlong", "DestinationAlat", "DestinationAlong", 
            "OriginBlat", "OriginBlong", "DestinationBlat", "DestinationBlong",
            "aDist", "aTime", "bDist", "bTime",
            "aIntersecRatio", "bIntersecRatio",
        ]
        write_csv_file(input_dir, results, fieldnames, output_csv)

    return results, pre_api_error_count, total_api_calls, post_api_error_count

def calculate_precise_travel_segments(
    route_coords: List[List[float]],
    intersections: List[List[float]],
    method: str,
    api_key: str,
    save_api_info: bool = False
) -> Dict[str, float]:
    """
    Calculates travel distances and times for segments of a route before, during,
    and after overlaps using Google Maps Directions API.
    Returns a dictionary with travel segment details.
    All coordinates are in the format [latitude, longitude].
    """

    if len(intersections) < 2:
        print(f"Only {len(intersections)} intersection(s) found, skipping during segment calculation.")
        if len(intersections) == 1:
            start = intersections[0]
            before_data = get_route_data(
                f"{route_coords[0][0]},{route_coords[0][1]}",
                f"{start[0]},{start[1]}",
                method,
                api_key,
                save_api_info=save_api_info
            )
            after_data = get_route_data(
                f"{start[0]},{start[1]}",
                f"{route_coords[-1][0]},{route_coords[-1][1]}",
                method,
                api_key,
                save_api_info=save_api_info
            )
            return {
                "before_distance": before_data[1],
                "before_time": before_data[2],
                "during_distance": 0.0,
                "during_time": 0.0,
                "after_distance": after_data[1],
                "after_time": after_data[2],
            }
        else:
            return {
                "before_distance": 0.0,
                "before_time": 0.0,
                "during_distance": 0.0,
                "during_time": 0.0,
                "after_distance": 0.0,
                "after_time": 0.0,
            }

    start = intersections[0]
    end = intersections[-1]

    before_data = get_route_data(
        f"{route_coords[0][0]},{route_coords[0][1]}",
        f"{start[0]},{start[1]}",
        method,
        api_key,
        save_api_info=save_api_info
    )
    during_data = get_route_data(
        f"{start[0]},{start[1]}",
        f"{end[0]},{end[1]}",
        method,
        api_key,
        save_api_info=save_api_info
    )
    after_data = get_route_data(
        f"{end[0]},{end[1]}",
        f"{route_coords[-1][0]},{route_coords[-1][1]}",
        method,
        api_key,
        save_api_info=save_api_info
    )

    print(f"Before segment: {before_data}")
    print(f"During segment: {during_data}")
    print(f"After segment: {after_data}")

    return {
        "before_distance": before_data[1],
        "before_time": before_data[2],
        "during_distance": during_data[1],
        "during_time": during_data[2],
        "after_distance": after_data[1],
        "after_time": after_data[2],
    }

# The function calculates travel metrics and overlapping segments between two routes based on their closest nodes and shared buffer intersection.
def process_row_closest_nodes(row_and_args):
    """
    Processes a row of route data to compute overlap metrics using buffered intersection and closest nodes.

    This function:
    - Fetches Google Maps API data for two routes (A and B).
    - Computes buffers for both routes and checks for intersection.
    - Identifies nodes within the intersection and computes before/during/after segments for each route.
    - Returns all relevant travel and overlap metrics.

    Args:
        row_and_args (tuple): A tuple containing:
            - row (dict): The input row with origin and destination fields.
            - api_key (str): Google API key.
            - buffer_distance (float): Buffer distance in meters.
            - skip_invalid (bool): Whether to skip rows with errors (default: True).
            - save_api_info (bool): Whether to save API response data (default: False).
            - input_dir (str): Directory for input files.
            - method (str): Routing method to use (e.g., "driving", "walking").

    Returns:
        tuple: (result_dict, api_calls, api_errors)
    """
    api_calls = 0
    try:
        row, api_key, buffer_distance, skip_invalid, save_api_info, input_dir, method = row_and_args
        ID = row["ID"]
        origin_a, destination_a = row["OriginA"], row["DestinationA"]
        origin_b, destination_b = row["OriginB"], row["DestinationB"]
        # Split and convert to float
        origin_a_lat, origin_a_lon = map(float, map(str.strip, origin_a.split(",")))
        destination_a_lat, destination_a_lon = map(float, map(str.strip, destination_a.split(",")))
        origin_b_lat, origin_b_lon = map(float, map(str.strip, origin_b.split(",")))
        destination_b_lat, destination_b_lon = map(float, map(str.strip, destination_b.split(",")))

        if origin_a == destination_a and origin_b == destination_b:
            return (
                DetailedDualOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=0.0,
                    aTime=0.0,
                    bDist=0.0,
                    bTime=0.0,
                    aoverlapDist=0.0,
                    aoverlapTime=0.0,
                    boverlapDist=0.0,
                    boverlapTime=0.0,
                    aBeforeDist=0.0,
                    aBeforeTime=0.0,
                    aAfterDist=0.0,
                    aAfterTime=0.0,
                    bBeforeDist=0.0,
                    bBeforeTime=0.0,
                    bAfterDist=0.0,
                    bAfterTime=0.0
                ).model_dump(),
                api_calls,
                0
            )

        if origin_a == destination_a and origin_b != destination_b:
            api_calls += 1
            coords_b, b_dist, b_time = get_route_data(origin_b, destination_b, method, api_key, save_api_info=save_api_info)
            return (
                DetailedDualOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=0.0,
                    aTime=0.0,
                    bDist=b_dist,
                    bTime=b_time,
                    aoverlapDist=0.0,
                    aoverlapTime=0.0,
                    boverlapDist=0.0,
                    boverlapTime=0.0,
                    aBeforeDist=0.0,
                    aBeforeTime=0.0,
                    aAfterDist=0.0,
                    aAfterTime=0.0,
                    bBeforeDist=0.0,
                    bBeforeTime=0.0,
                    bAfterDist=0.0,
                    bAfterTime=0.0
                ).model_dump(),
                api_calls,
                0
            )

        if origin_a != destination_a and origin_b == destination_b:
            api_calls += 1
            coords_a, a_dist, a_time = get_route_data(origin_a, destination_a, method, api_key, save_api_info=save_api_info)
            return (
                DetailedDualOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=a_dist,
                    aTime=a_time,
                    bDist=0.0,
                    bTime=0.0,
                    aoverlapDist=0.0,
                    aoverlapTime=0.0,
                    boverlapDist=0.0,
                    boverlapTime=0.0,
                    aBeforeDist=0.0,
                    aBeforeTime=0.0,
                    aAfterDist=0.0,
                    aAfterTime=0.0,
                    bBeforeDist=0.0,
                    bBeforeTime=0.0,
                    bAfterDist=0.0,
                    bAfterTime=0.0
                ).model_dump(),
                api_calls,
                0
            )

        if origin_a == origin_b and destination_a == destination_b:
            api_calls += 1
            coords_a, a_dist, a_time = get_route_data(origin_a, destination_a, method, api_key, save_api_info=save_api_info)
            buffer_a = create_buffered_route(coords_a, buffer_distance)
            coords_b = coords_a
            buffer_b = buffer_a
            plot_routes_and_buffers(coords_a, coords_b, buffer_a, buffer_b, ID, input_dir)
            return (
                DetailedDualOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=a_dist,
                    aTime=a_time,
                    bDist=a_dist,
                    bTime=a_time,
                    aoverlapDist=a_dist,
                    aoverlapTime=a_time,
                    boverlapDist=a_dist,
                    boverlapTime=a_time,
                    aBeforeDist=0.0,
                    aBeforeTime=0.0,
                    aAfterDist=0.0,
                    aAfterTime=0.0,
                    bBeforeDist=0.0,
                    bBeforeTime=0.0,
                    bAfterDist=0.0,
                    bAfterTime=0.0
                ).model_dump(),
                api_calls,
                0
            )

        api_calls += 2
        start_time_a = time.time()
        coords_a, a_dist, a_time = get_route_data(origin_a, destination_a, method, api_key, save_api_info=save_api_info)
        logging.info(f"Time to fetch route A from API: {time.time() - start_time_a:.6f} seconds")
        start_time_b = time.time()
        coords_b, b_dist, b_time = get_route_data(origin_b, destination_b, method, api_key, save_api_info=save_api_info)
        logging.info(f"Time to fetch route B from API: {time.time() - start_time_b:.6f} seconds")

        buffer_a = create_buffered_route(coords_a, buffer_distance)
        buffer_b = create_buffered_route(coords_b, buffer_distance)
        intersection_polygon = get_buffer_intersection(buffer_a, buffer_b)

        plot_routes_and_buffers(coords_a, coords_b, buffer_a, buffer_b, ID, input_dir)

        if not intersection_polygon:
            overlap_a = overlap_b = {
                "during_distance": 0.0, "during_time": 0.0,
                "before_distance": 0.0, "before_time": 0.0,
                "after_distance": 0.0, "after_time": 0.0,
            }
        else:
            start_time = time.time()
            nodes_inside_a = [pt for pt in coords_a if Point(pt[1], pt[0]).within(intersection_polygon)]
            logging.info(f"Time to check route A points inside intersection: {time.time() - start_time:.6f} seconds")
            start_time = time.time()
            nodes_inside_b = [pt for pt in coords_b if Point(pt[1], pt[0]).within(intersection_polygon)]
            logging.info(f"Time to check route B points inside intersection: {time.time() - start_time:.6f} seconds")

            if len(nodes_inside_a) >= 2:
                entry_a, exit_a = nodes_inside_a[0], nodes_inside_a[-1]
                api_calls += 1
                overlap_a = calculate_precise_travel_segments(coords_a, [list(entry_a), list(exit_a)], method, api_key, save_api_info=save_api_info)
            else:
                overlap_a = {"during_distance": 0.0, "during_time": 0.0,
                             "before_distance": 0.0, "before_time": 0.0,
                             "after_distance": 0.0, "after_time": 0.0}

            if len(nodes_inside_b) >= 2:
                entry_b, exit_b = nodes_inside_b[0], nodes_inside_b[-1]
                api_calls += 1
                overlap_b = calculate_precise_travel_segments(coords_b, [entry_b, exit_b], method, api_key, save_api_info=save_api_info)
            else:
                overlap_b = {"during_distance": 0.0, "during_time": 0.0,
                             "before_distance": 0.0, "before_time": 0.0,
                             "after_distance": 0.0, "after_time": 0.0}

        return (
            DetailedDualOverlapResult(
                ID=ID,
                OriginAlat=origin_a_lat,
                OriginAlong=origin_a_lon,
                DestinationAlat=destination_a_lat,
                DestinationAlong=destination_a_lon,
                OriginBlat=origin_b_lat,
                OriginBlong=origin_b_lon,
                DestinationBlat=destination_b_lat,
                DestinationBlong=destination_b_lon,
                aDist=a_dist,
                aTime=a_time,
                bDist=b_dist,
                bTime=b_time,
                aoverlapDist=overlap_a["during_distance"],
                aoverlapTime=overlap_a["during_time"],
                boverlapDist=overlap_b["during_distance"],
                boverlapTime=overlap_b["during_time"],
                aBeforeDist=overlap_a["before_distance"],
                aBeforeTime=overlap_a["before_time"],
                aAfterDist=overlap_a["after_distance"],
                aAfterTime=overlap_a["after_time"],
                bBeforeDist=overlap_b["before_distance"],
                bBeforeTime=overlap_b["before_time"],
                bAfterDist=overlap_b["after_distance"],
                bAfterTime=overlap_b["after_time"]
            ).model_dump(),
            api_calls,
            0
        )

    except Exception as e:
        if skip_invalid:
            logging.error(f"Error processing row {row if 'row' in locals() else 'unknown'}: {str(e)}")
            ID = row.get("ID", "")
            origin_a_lat, origin_a_lon = safe_split(row.get("OriginA", ""))
            destination_a_lat, destination_a_lon = safe_split(row.get("DestinationA", ""))
            origin_b_lat, origin_b_lon = safe_split(row.get("OriginB", ""))
            destination_b_lat, destination_b_lon = safe_split(row.get("DestinationB", ""))

            return (
                DetailedDualOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=None,
                    aTime=None,
                    bDist=None,
                    bTime=None,
                    aoverlapDist=None,
                    aoverlapTime=None,
                    boverlapDist=None,
                    boverlapTime=None,
                    aBeforeDist=None,
                    aBeforeTime=None,
                    aAfterDist=None,
                    aAfterTime=None,
                    bBeforeDist=None,
                    bBeforeTime=None,
                    bAfterDist=None,
                    bAfterTime=None,
                ).model_dump(),
                api_calls,
                1
            )
        else:
            raise

def process_routes_with_closest_nodes(
    csv_file: str,
    input_dir: str,
    api_key: str,
    home_a_lat: str,
    home_a_lon: str,
    work_a_lat: str,
    work_a_lon: str,
    home_b_lat: str,
    home_b_lon: str,
    work_b_lat: str,
    work_b_lon: str,
    id_column: Optional[str] = None,
    buffer_distance: float = 100.0,
    method: str = "google", 
    output_csv: str = "output_closest_nodes.csv",
    skip_invalid: bool = True,
    save_api_info: bool = False
) -> tuple:
    """
    Processes two routes using buffered geometries to compute travel overlap details
    based on closest nodes within the intersection.

    Parameters:
    - csv_file (str): Name of the input CSV file.
    - input_dir (str): Directory where the CSV file is located.
    - api_key (str): Google API key.
    - home_a_lat (str): Latitude for Home A.
    - home_a_lon (str): Longitude for Home A.
    - work_a_lat (str): Latitude for Work A.
    - work_a_lon (str): Longitude for Work A.
    - home_b_lat (str): Latitude for Home B.
    - home_b_lon (str): Longitude for Home B.
    - work_b_lat (str): Latitude for Work B.
    - work_b_lon (str): Longitude for Work B.
    - id_column (Optional[str]): Column name for unique IDs in the input CSV.
    - buffer_distance (float): Distance for the route buffer in meters.
    - method (str): Routing method to use ("google" or "graphhopper").
    - output_csv (str): Path to save the output results.
    - skip_invalid (bool): If True, skips invalid input rows and logs them.
    - save_api_info (bool): If True, save API response.

    Returns:
    - tuple: (
        results (list): Processed route rows,
        pre_api_error_count (int): Invalid before routing,
        total_api_calls (int): Number of API calls made,
        post_api_error_count (int): Failures during processing
      )
    """
    data, pre_api_error_count = read_csv_file(
        csv_file=csv_file,
        input_dir=input_dir,
        home_a_lat=home_a_lat,
        home_a_lon=home_a_lon,
        work_a_lat=work_a_lat,
        work_a_lon=work_a_lon,
        home_b_lat=home_b_lat,
        home_b_lon=home_b_lon,
        work_b_lat=work_b_lat,
        work_b_lon=work_b_lon,
        id_column=id_column,
        skip_invalid=skip_invalid
    )

    args_with_flags = [(row, api_key, buffer_distance, skip_invalid, save_api_info, input_dir, method) for row in data]

    results = []
    total_api_calls = 0
    post_api_error_count = 0
    processed_count = 0

    try:
        with Pool() as pool:
            for res in pool.imap_unordered(process_row_closest_nodes, args_with_flags):
                if res is None:
                    continue
                row_result, api_calls, api_errors = res
                results.append(row_result)
                total_api_calls += api_calls
                post_api_error_count += api_errors
                processed_count += 1
                print(f"[INFO] Processed {processed_count} row(s)...")
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Keyboard interrupt received. Writing partial results...")

    if results:
        fieldnames = list(results[0].keys())
        write_csv_file(input_dir=input_dir, results=results, fieldnames=fieldnames, output_file=output_csv)

    return results, pre_api_error_count, total_api_calls, post_api_error_count

def process_row_closest_nodes_simple(row_and_args):
    """
    Processes a single row to calculate overlapping travel distances and times between two routes.

    This simplified version:
    - Fetches coordinates and travel info for Route A and B.
    - Buffers both routes and computes their geometric intersection.
    - Finds the nodes that lie within the intersection polygon.
    - Estimates the overlapping segments' travel distance and time based on entry/exit points.

    Args:
        row_and_args (tuple): Tuple containing:
            - row (dict): Input row with OriginA, DestinationA, OriginB, DestinationB.
            - api_key (str): API key for route requests.
            - buffer_distance (float): Distance for route buffer in meters.
            - skip_invalid (bool): If True, logs and skips invalid rows on error; otherwise raises the error.
            - save_api_info (bool): If True, saves API response data.
            - input_dir (str): Directory for input files.
            - method (str): Routing method to use (e.g., "driving", "walking").

    Returns:
        tuple: (result_dict, api_calls, api_errors)
    """
    api_calls = 0
    try:
        row, api_key, buffer_distance, skip_invalid, save_api_info, input_dir, method = row_and_args
        ID = row["ID"]
        origin_a, destination_a = row["OriginA"], row["DestinationA"]
        origin_b, destination_b = row["OriginB"], row["DestinationB"]

        # Split and convert to float
        origin_a_lat, origin_a_lon = map(float, map(str.strip, origin_a.split(",")))
        destination_a_lat, destination_a_lon = map(float, map(str.strip, destination_a.split(",")))
        origin_b_lat, origin_b_lon = map(float, map(str.strip, origin_b.split(",")))
        destination_b_lat, destination_b_lon = map(float, map(str.strip, destination_b.split(",")))

        if origin_a == destination_a and origin_b == destination_b:
            return (
                SimpleDualOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=0.0,
                    aTime=0.0,
                    bDist=0.0,
                    bTime=0.0,
                    aoverlapDist=0.0,
                    aoverlapTime=0.0,
                    boverlapDist=0.0,
                    boverlapTime=0.0,
                ).model_dump(),
                api_calls,
                0
            )

        if origin_a == destination_a:
            api_calls += 1
            coords_b, b_dist, b_time = get_route_data(origin_b, destination_b, method, api_key, save_api_info=save_api_info)
            return (
                SimpleDualOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=0.0,
                    aTime=0.0,
                    bDist=b_dist,
                    bTime=b_time,
                    aoverlapDist=0.0,
                    aoverlapTime=0.0,
                    boverlapDist=0.0,
                    boverlapTime=0.0,
                ).model_dump(),
                api_calls,
                0
            )

        if origin_b == destination_b:
            api_calls += 1
            coords_a, a_dist, a_time = get_route_data(origin_a, destination_a, method, api_key, save_api_info=save_api_info)
            return (
                SimpleDualOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=a_dist,
                    aTime=a_time,
                    bDist=0.0,
                    bTime=0.0,
                    aoverlapDist=0.0,
                    aoverlapTime=0.0,
                    boverlapDist=0.0,
                    boverlapTime=0.0,
                ).model_dump(),
                api_calls,
                0
            )

        api_calls += 1
        coords_a, a_dist, a_time = get_route_data(origin_a, destination_a, method, api_key, save_api_info=save_api_info)

        api_calls += 1
        coords_b, b_dist, b_time = get_route_data(origin_b, destination_b, method, api_key, save_api_info=save_api_info)

        if origin_a == origin_b and destination_a == destination_b:
            buffer_a = create_buffered_route(coords_a, buffer_distance)
            buffer_b = buffer_a
            plot_routes_and_buffers(coords_a, coords_b, buffer_a, buffer_b, ID, input_dir)
            return (
                SimpleDualOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=a_dist,
                    aTime=a_time,
                    bDist=a_dist,
                    bTime=a_time,
                    aoverlapDist=a_dist,
                    aoverlapTime=a_time,
                    boverlapDist=a_dist,
                    boverlapTime=a_time,
                ).model_dump(),
                api_calls,
                0
            )

        buffer_a = create_buffered_route(coords_a, buffer_distance)
        buffer_b = create_buffered_route(coords_b, buffer_distance)
        intersection_polygon = get_buffer_intersection(buffer_a, buffer_b)

        plot_routes_and_buffers(coords_a, coords_b, buffer_a, buffer_b, ID, input_dir)

        if not intersection_polygon:
            print(f"No intersection for {origin_a} → {destination_a} and {origin_b} → {destination_b}")
            overlap_a_dist = overlap_a_time = overlap_b_dist = overlap_b_time = 0.0
        else:
            nodes_inside_a = [pt for pt in coords_a if Point(pt[1], pt[0]).within(intersection_polygon)]
            nodes_inside_b = [pt for pt in coords_b if Point(pt[1], pt[0]).within(intersection_polygon)]

            if len(nodes_inside_a) >= 2:
                api_calls += 1
                entry_a, exit_a = nodes_inside_a[0], nodes_inside_a[-1]
                segments_a = calculate_precise_travel_segments(coords_a, [entry_a, exit_a], method, api_key, save_api_info=save_api_info)
                overlap_a_dist = segments_a.get("during_distance", 0.0)
                overlap_a_time = segments_a.get("during_time", 0.0)
            else:
                overlap_a_dist = overlap_a_time = 0.0

            if len(nodes_inside_b) >= 2:
                api_calls += 1
                entry_b, exit_b = nodes_inside_b[0], nodes_inside_b[-1]
                segments_b = calculate_precise_travel_segments(coords_b, [entry_b, exit_b], method, api_key, save_api_info=save_api_info)
                overlap_b_dist = segments_b.get("during_distance", 0.0)
                overlap_b_time = segments_b.get("during_time", 0.0)
            else:
                overlap_b_dist = overlap_b_time = 0.0

        return (
            SimpleDualOverlapResult(
                ID=ID,
                OriginAlat=origin_a_lat,
                OriginAlong=origin_a_lon,
                DestinationAlat=destination_a_lat,
                DestinationAlong=destination_a_lon,
                OriginBlat=origin_b_lat,
                OriginBlong=origin_b_lon,
                DestinationBlat=destination_b_lat,
                DestinationBlong=destination_b_lon,
                aDist=a_dist,
                aTime=a_time,
                bDist=b_dist,
                bTime=b_time,
                aoverlapDist=overlap_a_dist,
                aoverlapTime=overlap_a_time,
                boverlapDist=overlap_b_dist,
                boverlapTime=overlap_b_time,
            ).model_dump(),
            api_calls,
            0
        )
    
    except Exception as e:
        if skip_invalid:
            logging.error(f"Error processing row {row}: {str(e)}")
            ID = row.get("ID", "")
            origin_a_lat, origin_a_lon = safe_split(row.get("OriginA", ""))
            destination_a_lat, destination_a_lon = safe_split(row.get("DestinationA", ""))
            origin_b_lat, origin_b_lon = safe_split(row.get("OriginB", ""))
            destination_b_lat, destination_b_lon = safe_split(row.get("DestinationB", ""))
            return (
                SimpleDualOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=None,
                    aTime=None,
                    bDist=None,
                    bTime=None,
                    aoverlapDist=None,
                    aoverlapTime=None,
                    boverlapDist=None,
                    boverlapTime=None,
                ).model_dump(),
                api_calls,
                1
            )
        else:
            raise

def process_routes_with_closest_nodes_simple(
    csv_file: str,
    input_dir: str,
    api_key: str,
    home_a_lat: str,
    home_a_lon: str,
    work_a_lat: str,
    work_a_lon: str,
    home_b_lat: str,
    home_b_lon: str,
    work_b_lat: str,
    work_b_lon: str,
    id_column: Optional[str] = None,
    buffer_distance: float = 100.0,
    method: str = "google",
    output_csv: str = "output_closest_nodes_simple.csv",
    skip_invalid: bool = True,
    save_api_info: bool = False
) -> tuple:
    """
    Computes total and overlapping travel segments for two routes using closest-node
    intersection logic without splitting before/during/after, and writes results to CSV.

    Parameters:
    - csv_file (str): Name of the input CSV file.
    - input_dir (str): Directory containing the input CSV file.
    - api_key (str): Google API key for route data.
    - home_a_lat (str): Latitude for Home A.
    - home_a_lon (str): Longitude for Home A.
    - work_a_lat (str): Latitude for Work A.
    - work_a_lon (str): Longitude for Work A.
    - home_b_lat (str): Latitude for Home B.
    - home_b_lon (str): Longitude for Home B.
    - work_b_lat (str): Latitude for Work B.
    - work_b_lon (str): Longitude for Work B.
    - id_column (Optional[str]): Column name for unique IDs in the input CSV.
    - buffer_distance (float): Distance used for the buffer zone.
    - method (str): Routing method to use ("google" or "graphhopper").
    - output_csv (str): Output name for CSV file with results.
    - skip_invalid (bool): If True, skips rows with invalid coordinate values.
    - save_api_info (bool): If True, saves API response.

    Returns:
    - tuple: (
        results (list): Processed result rows,
        pre_api_error_count (int): Number of errors before API calls,
        total_api_calls (int): Total number of API calls made,
        post_api_error_count (int): Number of errors during/after API calls
      )
    """
    data, pre_api_error_count = read_csv_file(
        csv_file=csv_file,
        input_dir=input_dir,
        home_a_lat=home_a_lat,
        home_a_lon=home_a_lon,
        work_a_lat=work_a_lat,
        work_a_lon=work_a_lon,
        home_b_lat=home_b_lat,
        home_b_lon=home_b_lon,
        work_b_lat=work_b_lat,
        work_b_lon=work_b_lon,
        id_column=id_column,
        skip_invalid=skip_invalid
    )

    args_with_flags = [(row, api_key, buffer_distance, skip_invalid, save_api_info, input_dir, method) for row in data]

    results = []
    total_api_calls = 0
    post_api_error_count = 0
    processed_count = 0

    try:
        with Pool() as pool:
            for r in pool.imap_unordered(process_row_closest_nodes_simple, args_with_flags):
                if r is None:
                    continue
                row_result, api_calls, api_errors = r
                results.append(row_result)
                total_api_calls += api_calls
                post_api_error_count += api_errors
                processed_count += 1
                print(f"[INFO] Processed {processed_count} row(s)...")
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Keyboard interrupt received. Writing partial results...")

    if results:
        fieldnames = list(results[0].keys())
        write_csv_file(input_dir=input_dir, results=results, fieldnames=fieldnames, output_file=output_csv)

    return results, pre_api_error_count, total_api_calls, post_api_error_count

def wrap_row_multiproc_exact(args):
    """
    Wraps a row-processing call for exact intersection calculations using buffered routes.

    This function is designed for use with multiprocessing. It unpacks the arguments and
    passes them to `process_row_exact_intersections`.

    Tracks:
    - The number of API calls made within each row.
    - Whether an error occurred during processing (used for error counts).

    Args:
        args (tuple): Contains:
            - row (dict): A dictionary representing a single CSV row.
            - api_key (str): Google Maps API key.
            - buffer_distance (float): Distance for buffer creation in meters.
            - skip_invalid (bool): If True, logs and skips rows with errors.
            - save_api_info (bool): If True, saves API response.
            - input_dir (str): Directory for saving output files.

    Returns:
        tuple: (result_dict, api_call_count, api_error_flag)
            - result_dict (dict or None): Result of row processing.
            - api_call_count (int): Number of API calls made.
            - api_error_flag (int): 0 if successful, 1 if error occurred and skip_invalid was True.
    """
    row, api_key, buffer_distance, skip_invalid, save_api_info, input_dir, method = args
    result, api_calls, api_errors = process_row_exact_intersections(
        row, api_key, buffer_distance, method, skip_invalid, save_api_info, input_dir
    )
    return result, api_calls, api_errors

def process_row_exact_intersections(
    row: Dict[str, str],
    api_key: str,
    buffer_distance: float,
    method: str,
    skip_invalid: bool = True,
    save_api_info: bool = False,
    input_dir: str = "",
) -> Tuple[Dict[str, Any], int, int]:
    """
    Computes precise overlapping segments between two routes using buffered polygon intersections.

    This function fetches routes, creates buffer zones, finds intersection points, and
    calculates travel metrics. It logs and tracks the number of API calls and whether
    an error was encountered during execution.

    Args:
        row (dict): Dictionary with keys "OriginA", "DestinationA", "OriginB", "DestinationB".
        api_key (str): Google Maps API key.
        buffer_distance (float): Buffer distance in meters to apply to each route.
        method (str): "google" or "graphhopper" to specify routing method.
        skip_invalid (bool): If True, logs and skips errors instead of raising them.
        save_api_info (bool): If True, saves API response.
        input_dir (str): Directory to save output plots and files.

    Returns:
        tuple: (result_dict, api_call_count, api_error_flag)
            - result_dict (dict or None): Computed metrics or None if error.
            - api_call_count (int): Number of API requests made.
            - api_error_flag (int): 0 if success, 1 if handled error.
    """
    api_calls = 0
    try:
        ID = row.get("ID", "")
        origin_a, destination_a = row["OriginA"], row["DestinationA"]
        origin_b, destination_b = row["OriginB"], row["DestinationB"]

        origin_a_lat, origin_a_lon = safe_split(row.get("OriginA", ""))
        destination_a_lat, destination_a_lon = safe_split(row.get("DestinationA", ""))
        origin_b_lat, origin_b_lon = safe_split(row.get("OriginB", ""))
        destination_b_lat, destination_b_lon = safe_split(row.get("DestinationB", ""))

        if origin_a == destination_a and origin_b == destination_b:
            return (
                DetailedDualOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=0.0,
                    aTime=0.0,
                    bDist=0.0,
                    bTime=0.0,
                    aoverlapDist=0.0,
                    aoverlapTime=0.0,
                    boverlapDist=0.0,
                    boverlapTime=0.0,
                    aBeforeDist=0.0,
                    aBeforeTime=0.0,
                    aAfterDist=0.0,
                    aAfterTime=0.0,
                    bBeforeDist=0.0,
                    bBeforeTime=0.0,
                    bAfterDist=0.0,
                    bAfterTime=0.0,
                ).model_dump(),
                api_calls,
                0
            )

        if origin_a == destination_a and origin_b != destination_b:
            api_calls += 1
            coords_b, b_dist, b_time = get_route_data(origin_b, destination_b, method, api_key, save_api_info=save_api_info)
            return (
                DetailedDualOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=0.0,
                    aTime=0.0,
                    bDist=b_dist,
                    bTime=b_time,
                    aoverlapDist=0.0,
                    aoverlapTime=0.0,
                    boverlapDist=0.0,
                    boverlapTime=0.0,
                    aBeforeDist=0.0,
                    aBeforeTime=0.0,
                    aAfterDist=0.0,
                    aAfterTime=0.0,
                    bBeforeDist=0.0,
                    bBeforeTime=0.0,
                    bAfterDist=0.0,
                    bAfterTime=0.0,
                ).model_dump(),
                api_calls,
                0
            )

        if origin_a != destination_a and origin_b == destination_b:
            api_calls += 1
            coords_a, a_dist, a_time = get_route_data(origin_a, destination_a, method, api_key, save_api_info=save_api_info)
            return (
                DetailedDualOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=a_dist,
                    aTime=a_time,
                    bDist=0.0,
                    bTime=0.0,
                    aoverlapDist=0.0,
                    aoverlapTime=0.0,
                    boverlapDist=0.0,
                    boverlapTime=0.0,
                    aBeforeDist=0.0,
                    aBeforeTime=0.0,
                    aAfterDist=0.0,
                    aAfterTime=0.0,
                    bBeforeDist=0.0,
                    bBeforeTime=0.0,
                    bAfterDist=0.0,
                    bAfterTime=0.0,
                ).model_dump(),
                api_calls,
                0
            )
        
        if origin_a == origin_b and destination_a == destination_b:
            api_calls += 1
            coords_a, dist_a, time_a = get_route_data(origin_a, destination_a, method, api_key, save_api_info=save_api_info)
            return (
                DetailedDualOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=dist_a,
                    aTime=time_a,
                    bDist=dist_a,
                    bTime=time_a,
                    aoverlapDist=dist_a,      # Overlap is the full distance of A
                    aoverlapTime=time_a,      # Overlap is the full time of A
                    boverlapDist=dist_a,      # Same for B
                    boverlapTime=time_a,
                    aBeforeDist=0.0,
                    aBeforeTime=0.0,
                    aAfterDist=0.0,
                    aAfterTime=0.0,
                    bBeforeDist=0.0,
                    bBeforeTime=0.0,
                    bAfterDist=0.0,
                    bAfterTime=0.0,
                ).model_dump(),
                api_calls,
                0
            )

        api_calls += 1
        start_time_a = time.time()

        coords_a, a_dist, a_time = get_route_data(origin_a, destination_a, method, api_key, save_api_info=save_api_info)
        logging.info(f"Time to fetch route A from API: {time.time() - start_time_a:.6f} seconds")

        api_calls += 1
        start_time_b = time.time()
        coords_b, b_dist, b_time = get_route_data(origin_b, destination_b, method, api_key, save_api_info=save_api_info)
        logging.info(f"Time to fetch route B from API: {time.time() - start_time_b:.6f} seconds")

        buffer_a = create_buffered_route(coords_a, buffer_distance)
        buffer_b = create_buffered_route(coords_b, buffer_distance)
        intersection_polygon = get_buffer_intersection(buffer_a, buffer_b)

        plot_routes_and_buffers(coords_a, coords_b, buffer_a, buffer_b, ID, input_dir)

        if not intersection_polygon:
            overlap_a = overlap_b = {"during_distance": 0.0, "during_time": 0.0, "before_distance": 0.0, "before_time": 0.0, "after_distance": 0.0, "after_time": 0.0}
        else:
            points_a = get_route_polygon_intersections(coords_a, intersection_polygon)
            points_b = get_route_polygon_intersections(coords_b, intersection_polygon)

            if len(points_a) >= 2:
                api_calls += 1
                entry_a, exit_a = points_a[0], points_a[-1]
                overlap_a = calculate_precise_travel_segments(coords_a, [entry_a, exit_a], method, api_key, save_api_info=save_api_info)
            else:
                overlap_a = {"during_distance": 0.0, "during_time": 0.0, "before_distance": 0.0, "before_time": 0.0, "after_distance": 0.0, "after_time": 0.0}

            if len(points_b) >= 2:
                api_calls += 1
                entry_b, exit_b = points_b[0], points_b[-1]
                overlap_b = calculate_precise_travel_segments(coords_b, [entry_b, exit_b], method, api_key, save_api_info=save_api_info)
            else:
                overlap_b = {"during_distance": 0.0, "during_time": 0.0, "before_distance": 0.0, "before_time": 0.0, "after_distance": 0.0, "after_time": 0.0}

        return (
            DetailedDualOverlapResult(
                ID=ID,
                OriginAlat=origin_a_lat,
                OriginAlong=origin_a_lon,
                DestinationAlat=destination_a_lat,
                DestinationAlong=destination_a_lon,
                OriginBlat=origin_b_lat,
                OriginBlong=origin_b_lon,
                DestinationBlat=destination_b_lat,
                DestinationBlong=destination_b_lon,
                aDist=a_dist,
                aTime=a_time,
                bDist=b_dist,
                bTime=b_time,
                aoverlapDist=overlap_a["during_distance"],
                aoverlapTime=overlap_a["during_time"],
                boverlapDist=overlap_b["during_distance"],
                boverlapTime=overlap_b["during_time"],
                aBeforeDist=overlap_a["before_distance"],
                aBeforeTime=overlap_a["before_time"],
                aAfterDist=overlap_a["after_distance"],
                aAfterTime=overlap_a["after_time"],
                bBeforeDist=overlap_b["before_distance"],
                bBeforeTime=overlap_b["before_time"],
                bAfterDist=overlap_b["after_distance"],
                bAfterTime=overlap_b["after_time"],
            ).model_dump(),
            api_calls,
            0
        )

    except Exception as e:
        if skip_invalid:
            logging.error(f"Error processing row {row}: {str(e)}")
            ID = row.get("ID", "")
            origin_a_lat, origin_a_lon = safe_split(row.get("OriginA", ""))
            destination_a_lat, destination_a_lon = safe_split(row.get("DestinationA", ""))
            origin_b_lat, origin_b_lon = safe_split(row.get("OriginB", ""))
            destination_b_lat, destination_b_lon = safe_split(row.get("DestinationB", ""))

            return (
                DetailedDualOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=None,
                    aTime=None,
                    bDist=None,
                    bTime=None,
                    aoverlapDist=None,
                    aoverlapTime=None,
                    boverlapDist=None,
                    boverlapTime=None,
                    aBeforeDist=None,
                    aBeforeTime=None,
                    aAfterDist=None,
                    aAfterTime=None,
                    bBeforeDist=None,
                    bBeforeTime=None,
                    bAfterDist=None,
                    bAfterTime=None,
                ).model_dump(),
                api_calls,
                1
            )
        else:
            raise

def process_routes_with_exact_intersections(
    csv_file: str,
    input_dir: str,
    api_key: str,
    home_a_lat: str,
    home_a_lon: str,
    work_a_lat: str,
    work_a_lon: str,
    home_b_lat: str,
    home_b_lon: str,
    work_b_lat: str,
    work_b_lon: str,
    id_column: Optional[str] = None,
    buffer_distance: float = 100.0,
    method: str = "google",
    output_csv: str = "output_exact_intersections.csv",
    skip_invalid: bool = True,
    save_api_info: bool = False
) -> tuple:
    """
    Calculates travel metrics for two routes using exact geometric intersections within buffer polygons.

    It applies the processing to each row of the CSV using multiprocessing and collects:
    - The total number of API calls made across all rows.
    - The number of post-API processing errors (e.g., route failure, segment failure).

    Parameters:
        csv_file (str): Name of the input CSV file.
        input_dir (str): Directory containing the input CSV file.
        api_key (str): Google API key for route data.
        home_a_lat (str): Latitude for Home A.
        home_a_lon (str): Longitude for Home A.
        work_a_lat (str): Latitude for Work A.
        work_a_lon (str): Longitude for Work A.
        home_b_lat (str): Latitude for Home B.
        home_b_lon (str): Longitude for Home B.
        work_b_lat (str): Latitude for Work B.
        work_b_lon (str): Longitude for Work B.
        id_column (Optional[str]): Column name for unique IDs in the input CSV.
        buffer_distance (float): Distance for buffer zone around each route.
        method (str): Routing method to use ("google" or "graphhopper").
        output_csv (str): Output CSV file path.
        skip_invalid (bool): If True, skip invalid coordinate rows and log them.
        save_api_info (bool): If True, save API response.

    Returns:
        tuple:
            - results (list): Processed result dictionaries.
            - pre_api_error_count (int): Errors before API calls (e.g., missing coordinates).
            - api_call_count (int): Total number of Google Maps API requests.
            - post_api_error_count (int): Errors during or after API processing.
    """
    data, pre_api_error_count = read_csv_file(
        csv_file=csv_file,
        input_dir=input_dir,
        home_a_lat=home_a_lat,
        home_a_lon=home_a_lon,
        work_a_lat=work_a_lat,
        work_a_lon=work_a_lon,
        home_b_lat=home_b_lat,
        home_b_lon=home_b_lon,
        work_b_lat=work_b_lat,
        work_b_lon=work_b_lon,
        id_column=id_column,
        skip_invalid=skip_invalid
    )

    args_list = [(row, api_key, buffer_distance, skip_invalid, save_api_info, input_dir, method) for row in data]

    results = []
    api_call_count = 0
    post_api_error_count = 0
    processed_count = 0

    try:
        with Pool() as pool:
            for result in pool.imap_unordered(wrap_row_multiproc_exact, args_list):
                if result is None:
                    continue
                row_result, calls, errors = result
                results.append(row_result)
                api_call_count += calls
                post_api_error_count += errors
                processed_count += 1
                print(f"[INFO] Processed {processed_count} row(s)...")

    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Keyboard interrupt received. Writing partial results...")

    if results:
        fieldnames = list(results[0].keys())
        write_csv_file(input_dir=input_dir, results=results, fieldnames=fieldnames, output_file=output_csv)

    return results, pre_api_error_count, api_call_count, post_api_error_count

def wrap_row_multiproc_simple(args):
    """
    Wraps a single row-processing function for multithreading with error handling.

    Args:
        args (tuple): A tuple containing:
            - row (dict): The input row with origin/destination fields.
            - api_key (str): API key for Google Maps routing.
            - buffer_distance (float): Distance for creating buffer polygons around the route.
            - input_dir (str): Directory where input files are located.
            - skip_invalid (bool): If True, log and skip rows that raise exceptions; else re-raise.
            - save_api_info (bool): If True, include and store raw API response data.

    Returns:
        tuple: A tuple of (result_dict, api_calls, api_errors)
    """
    row, api_key, buffer_distance, input_dir, skip_invalid, save_api_info, method = args
    return process_row_exact_intersections_simple(
        (row, api_key, buffer_distance, save_api_info),
        skip_invalid=skip_invalid,
        input_dir=input_dir,
        method=method
    )

def process_row_exact_intersections_simple(row_and_args, skip_invalid=True, input_dir="", method="google") -> Tuple[Dict[str, Any], int, int]:
    """
    Processes a single row to compute total and overlapping travel metrics between two routes
    using exact geometric intersections of buffered route polygons.

    This simplified version:
    - Uses the Google Maps API to fetch coordinates, distance, and time for both routes.
    - Creates buffers around each route and computes the exact polygon intersection.
    - Finds entry/exit points from each route within the intersection polygon.
    - Calculates travel metrics for overlapping segments using those entry/exit points.
    - Handles degenerate and edge cases (identical routes or points).

    Args:
        row_and_args (tuple): Tuple containing:
            - row (dict): Input with "OriginA", "DestinationA", "OriginB", "DestinationB"
            - api_key (str): Google Maps API key
            - buffer_distance (float): Buffer distance in meters
        skip_invalid (bool): If True, logs and skips errors; if False, raises them.
        input_dir (str): Directory to save output plots and files.
        method (str): Routing method, either "google" or "graphhopper".

    Returns:
        tuple: A tuple of (result_dict, api_calls, api_errors)
    """
    api_calls = 0

    try:
        row, api_key, buffer_distance, save_api_info = row_and_args
        ID = row["ID"]
        origin_a, destination_a = row["OriginA"], row["DestinationA"]
        origin_b, destination_b = row["OriginB"], row["DestinationB"]

        origin_a_lat, origin_a_lon = map(float, map(str.strip, origin_a.split(",")))
        destination_a_lat, destination_a_lon = map(float, map(str.strip, destination_a.split(",")))
        origin_b_lat, origin_b_lon = map(float, map(str.strip, origin_b.split(",")))
        destination_b_lat, destination_b_lon = map(float, map(str.strip, destination_b.split(",")))

        if origin_a == destination_a and origin_b == destination_b:
            return (
                SimpleDualOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=0.0,
                    aTime=0.0,
                    bDist=0.0,
                    bTime=0.0,
                    aoverlapDist=0.0,
                    aoverlapTime=0.0,
                    boverlapDist=0.0,
                    boverlapTime=0.0,
                ).model_dump(),
                api_calls,
                0
            )

        if origin_a == destination_a:
            api_calls += 1
            coords_b, b_dist, b_time = get_route_data(origin_b, destination_b, method, api_key, save_api_info=save_api_info)
            return (
                SimpleDualOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=0.0,
                    aTime=0.0,
                    bDist=b_dist,
                    bTime=b_time,
                    aoverlapDist=0.0,
                    aoverlapTime=0.0,
                    boverlapDist=0.0,
                    boverlapTime=0.0,
                ).model_dump(),
                api_calls,
                0
            )

        if origin_b == destination_b:
            api_calls += 1
            coords_a, a_dist, a_time = get_route_data(origin_a, destination_a, method, api_key, save_api_info=save_api_info)
            return (
                SimpleDualOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=a_dist,
                    aTime=a_time,
                    bDist=0.0,
                    bTime=0.0,
                    aoverlapDist=0.0,
                    aoverlapTime=0.0,
                    boverlapDist=0.0,
                    boverlapTime=0.0,
                ).model_dump(),
                api_calls,
                0
            )

        if origin_a == origin_b and destination_a == destination_b:
            api_calls += 1
            coords_a, a_dist, a_time = get_route_data(origin_a, destination_a, method, api_key, save_api_info=save_api_info)
            buffer_a = create_buffered_route(coords_a, buffer_distance)
            buffer_b = buffer_a
            coords_b = coords_a
            plot_routes_and_buffers(coords_a, coords_b, buffer_a, buffer_b, ID, input_dir)
            return (
                SimpleDualOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=a_dist,
                    aTime=a_time,
                    bDist=a_dist,
                    bTime=a_time,
                    aoverlapDist=a_dist,
                    aoverlapTime=a_time,
                    boverlapDist=a_dist,
                    boverlapTime=a_time,
                ).model_dump(),
                api_calls,
                0
            )
        
        api_calls += 2
        coords_a, a_dist, a_time = get_route_data(origin_a, destination_a, method, api_key, save_api_info=save_api_info)
        coords_b, b_dist, b_time = get_route_data(origin_b, destination_b, method, api_key, save_api_info=save_api_info)

        buffer_a = create_buffered_route(coords_a, buffer_distance)
        buffer_b = create_buffered_route(coords_b, buffer_distance)
        intersection_polygon = get_buffer_intersection(buffer_a, buffer_b)

        plot_routes_and_buffers(coords_a, coords_b, buffer_a, buffer_b, ID, input_dir)

        if not intersection_polygon:
            return (
                SimpleDualOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=a_dist,
                    aTime=a_time,
                    bDist=b_dist,
                    bTime=b_time,
                    aoverlapDist=0.0,
                    aoverlapTime=0.0,
                    boverlapDist=0.0,
                    boverlapTime=0.0,
                ).model_dump(),
                api_calls,
                0
            )

        points_a = get_route_polygon_intersections(coords_a, intersection_polygon)
        points_b = get_route_polygon_intersections(coords_b, intersection_polygon)

        if len(points_a) >= 2:
            api_calls += 1
            entry_a, exit_a = points_a[0], points_a[-1]
            segments_a = calculate_precise_travel_segments(coords_a, [entry_a, exit_a], method, api_key, save_api_info=save_api_info)
            overlap_a_dist = segments_a.get("during_distance", 0.0)
            overlap_a_time = segments_a.get("during_time", 0.0)
        else:
            overlap_a_dist = overlap_a_time = 0.0

        if len(points_b) >= 2:
            api_calls += 1
            entry_b, exit_b = points_b[0], points_b[-1]
            segments_b = calculate_precise_travel_segments(coords_b, [entry_b, exit_b], method, api_key, save_api_info=save_api_info)
            overlap_b_dist = segments_b.get("during_distance", 0.0)
            overlap_b_time = segments_b.get("during_time", 0.0)
        else:
            overlap_b_dist = overlap_b_time = 0.0

        return (
            SimpleDualOverlapResult(
                ID=ID,
                OriginAlat=origin_a_lat,
                OriginAlong=origin_a_lon,
                DestinationAlat=destination_a_lat,
                DestinationAlong=destination_a_lon,
                OriginBlat=origin_b_lat,
                OriginBlong=origin_b_lon,
                DestinationBlat=destination_b_lat,
                DestinationBlong=destination_b_lon,
                aDist=a_dist,
                aTime=a_time,
                bDist=b_dist,
                bTime=b_time,
                aoverlapDist=overlap_a_dist,
                aoverlapTime=overlap_a_time,
                boverlapDist=overlap_b_dist,
                boverlapTime=overlap_b_time,
            ).model_dump(),
            api_calls,
            0
        )

    except Exception as e:
        if skip_invalid:
            logging.error(f"Error processing row {row if 'row' in locals() else 'unknown'}: {str(e)}")
            ID = row.get("ID", "")
            origin_a_lat, origin_a_lon = safe_split(row.get("OriginA", ""))
            destination_a_lat, destination_a_lon = safe_split(row.get("DestinationA", ""))
            origin_b_lat, origin_b_lon = safe_split(row.get("OriginB", ""))
            destination_b_lat, destination_b_lon = safe_split(row.get("DestinationB", ""))

            return (
                SimpleDualOverlapResult(
                    ID=ID,
                    OriginAlat=origin_a_lat,
                    OriginAlong=origin_a_lon,
                    DestinationAlat=destination_a_lat,
                    DestinationAlong=destination_a_lon,
                    OriginBlat=origin_b_lat,
                    OriginBlong=origin_b_lon,
                    DestinationBlat=destination_b_lat,
                    DestinationBlong=destination_b_lon,
                    aDist=None,
                    aTime=None,
                    bDist=None,
                    bTime=None,
                    aoverlapDist=None,
                    aoverlapTime=None,
                    boverlapDist=None,
                    boverlapTime=None,
                ).model_dump(),
                api_calls,
                1
            )
        else:
            raise

def process_routes_with_exact_intersections_simple(
    csv_file: str,
    input_dir: str,
    api_key: str,
    home_a_lat: str,
    home_a_lon: str,
    work_a_lat: str,
    work_a_lon: str,
    home_b_lat: str,
    home_b_lon: str,
    work_b_lat: str,
    work_b_lon: str,
    id_column: Optional[str] = None,
    buffer_distance: float = 100.0,
    method: str = "google",
    output_csv: str = "output_exact_intersections_simple.csv",
    skip_invalid: bool = True,
    save_api_info: bool = False
) -> tuple:
    """
    Processes routes to compute total and overlapping segments using exact geometric intersections,
    without splitting into before/during/after segments. Supports optional skipping of invalid rows.

    Parameters:
    - csv_file (str): Path to input CSV file.
    - input_dir (str): Directory containing the input CSV file.
    - api_key (str): Google API key for routing data.
    - home_a_lat (str): Column name for the latitude of home A.
    - home_a_lon (str): Column name for the longitude of home A.
    - work_a_lat (str): Column name for the latitude of work A.
    - work_a_lon (str): Column name for the longitude of work A.
    - home_b_lat (str): Column name for the latitude of home B.
    - home_b_lon (str): Column name for the longitude of home B.
    - work_b_lat (str): Column name for the latitude of work B.
    - work_b_lon (str): Column name for the longitude of work B.
    - id_column (Optional[str]): Column name for the unique ID of each row.
    - buffer_distance (float): Distance for buffering each route.
    - method (str): Routing method, either "google" or "graphhopper".
    - output_csv (str): File path to write the output CSV.
    - skip_invalid (bool): If True, skips invalid coordinate rows and logs them.
    - save_api_info (bool): If True, saves API response.

    Returns:
    - tuple: (results list, pre_api_error_count, api_call_count, post_api_error_count)
    """
    data, pre_api_error_count = read_csv_file(
        csv_file=csv_file,
        input_dir=input_dir,
        home_a_lat=home_a_lat,
        home_a_lon=home_a_lon,
        work_a_lat=work_a_lat,
        work_a_lon=work_a_lon,
        home_b_lat=home_b_lat,
        home_b_lon=home_b_lon,
        work_b_lat=work_b_lat,
        work_b_lon=work_b_lon,
        id_column=id_column,
        skip_invalid=skip_invalid
    )

    args = [(row, api_key, buffer_distance, input_dir, skip_invalid, save_api_info, method) for row in data]

    processed = []
    api_call_count = 0
    api_error_count = 0
    processed_count = 0

    try:
        with Pool() as pool:
            for result in pool.imap_unordered(wrap_row_multiproc_simple, args):
                if result is None:
                    continue
                row_result, row_calls, row_errors = result
                processed.append(row_result)
                api_call_count += row_calls
                api_error_count += row_errors
                processed_count += 1
                print(f"[INFO] Processed {processed_count} row(s)...")

    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Keyboard interrupt received. Writing partial results...")

    if processed:
        fieldnames = list(processed[0].keys())
        write_csv_file(input_dir=input_dir, results=processed, fieldnames=fieldnames, output_file=output_csv)

    return processed, pre_api_error_count, api_call_count, api_error_count

# Function to write txt file for displaying inputs for the package to run.
def write_log(file_path: str, options: dict, input_dir: str) -> None:
    """
    Writes a log file summarizing the inputs used for running the package.

    Args:
        file_path (str): Path of the main CSV result file.
        options (dict): Dictionary of options and their values.
        input_dir (str): Directory where the input files are located.
    Returns:
        None
    """
    # Ensure results folder exists inside the input directory
    results_dir = os.path.join(input_dir, "ResultsCommuto")
    os.makedirs(results_dir, exist_ok=True)
    base_filename = os.path.basename(file_path).replace(".csv", ".log")

    # Save the log file inside the results folder in input_dir
    log_file_path = os.path.join(results_dir, base_filename)

    # Write the log file
    with open(log_file_path, "w", encoding="utf-8") as log_file:
        log_file.write("Options:\n")
        for key, value in options.items():
            log_file.write(f"{key}: {value}\n")
        log_file.write(f"Generated on: {datetime.datetime.now()}\n")

    print(f"Log file saved to: {os.path.abspath(log_file_path)}")

## This is the main function with user interaction.
def Overlap_Function(
    csv_file: Optional[str],
    input_dir: Optional[str],
    api_key: Optional[str],
    home_a_lat: Optional[str],
    home_a_lon: Optional[str],
    work_a_lat: Optional[str],
    work_a_lon: Optional[str],
    home_b_lat: Optional[str],
    home_b_lon: Optional[str],
    work_b_lat: Optional[str],
    work_b_lon: Optional[str],
    id_column: Optional[str] = None,
    threshold: float = 50,
    width: float = 100,
    buffer: float = 100,
    approximation: str = "no",
    commuting_info: str = "no",
    method: str = "google",
    output_file: Optional[str] = None,
    skip_invalid: bool = True,
    save_api_info: bool = True,
    auto_confirm: bool = False
) -> None:
    """
    Main dispatcher function to handle various route overlap and buffer analysis strategies.

    Based on the 'approximation' and 'commuting_info' flags, it routes the execution to one of
    several processing functions that compute route overlaps and buffer intersections, and writes
    results to CSV output files. It also logs options and configurations.

    Parameters:
    - csv_file (str): Path to input CSV file.
    - api_key (str): Google Maps API key.
    - home_a_lat : Column name for the latitude of home A.
    - home_a_lon : Column name for the longitude of home A.
    - work_a_lat : Column name for the latitude of work A.
    - work_a_lon : Column name for the longitude of work A.
    - home_b_lat : Column name for the latitude of home B.
    - home_b_lon : Column name for the longitude of home B.
    - work_b_lat : Column name for the latitude of work B.
    - work_b_lon : Column name for the longitude of work B.
    - id_column : Column name for the unique ID of each row. If None or not found, IDs are auto-generated as R1, R2, ...
    - threshold (float): Distance threshold for overlap (if applicable).
    - width (float): Width used for line buffering (if applicable).
    - buffer (float): Buffer radius in meters.
    - approximation (str): Mode of processing (e.g., "no", "yes", "yes with buffer", etc.).
    - commuting_info (str): Whether commuting detail is needed ("yes" or "no").
    - method (str): Routing method to use, either "google" or "graphhopper".
    - output_file (str): Optional custom filename for results.
    - input_dir (str): Directory for input files if not provided as a full path.
    - skip_invalid (bool): If True, skips invalid coordinates and logs the error; if False, halts on error.
    - save_api_info (bool): If True, saves API response.
    - auto_confirm (bool): If True, skips the user confirmation prompt and proceeds automatically.

    Returns:
    - None
    """
        # Determine input directory
    if input_dir:
        input_dir = os.path.abspath(input_dir)
        csv_path = os.path.join(input_dir, csv_file)
    else:
        if csv_file is not None:
            csv_path = os.path.abspath(csv_file)
            input_dir = os.path.dirname(csv_path)
        else:
            raise ValueError("csv_file must not be None.")

    # Create a 'results' folder inside the input directory
    output_dir = os.path.join(input_dir, "ResultsCommuto")
    os.makedirs(output_dir, exist_ok=True)

    options = {
        "csv_file": csv_file,
        "api_key": "********",
        "threshold": threshold,
        "width": width,
        "buffer": buffer,
        "approximation": approximation,
        "commuting_info": commuting_info,
        "home_a_lat": home_a_lat,
        "home_a_lon": home_a_lon,
        "work_a_lat": work_a_lat,
        "work_a_lon": work_a_lon,
        "home_b_lat": home_b_lat,
        "home_b_lon": home_b_lon,
        "work_b_lat": work_b_lat,
        "work_b_lon": work_b_lon,
        "id_column": id_column,
        "input_dir": input_dir,
        "method": method,
        "skip_invalid": skip_invalid,
        "save_api_info": save_api_info,
    }

    if csv_file is None:
        raise ValueError("csv_file must not be None when calling request_cost_estimation.")
    if method == "google":
        try:
            num_requests, estimated_cost = request_cost_estimation(
                csv_file=csv_file,
                input_dir=input_dir,
                home_a_lat=home_a_lat,
                home_a_lon=home_a_lon,
                work_a_lat=work_a_lat,
                work_a_lon=work_a_lon, 
                home_b_lat=home_b_lat,
                home_b_lon=home_b_lon,
                work_b_lat= work_b_lat,
                work_b_lon=work_b_lon,
                id_column=id_column,
                approximation=approximation,
                commuting_info=commuting_info,
                skip_invalid=skip_invalid
            )
        except Exception as e:
            print(f"[ERROR] Unable to estimate cost: {e}")
            return

        print(f"\n[INFO] Estimated number of API requests: {num_requests}")
        print(f"[INFO] Estimated cost: ${estimated_cost:.2f}")
        print("[NOTICE] Actual cost may be higher or lower depending on Google’s pricing tiers and route pair complexity.\n")
    
    elif method == "graphhopper":
        print("[NOTICE] GraphHopper does not provide cost estimation. Proceeding with the operation...\n")
        num_requests = 0
        estimated_cost = 0.0

    if not auto_confirm:
        user_input = input("Do you want to proceed with this operation? (yes/no): ").strip().lower()
        if user_input != "yes":
            print("[CANCELLED] Operation aborted by the user.")
            return
    else:
        print("[AUTO-CONFIRM] Skipping user prompt and proceeding...\n")

    print("[PROCESSING] Proceeding with route analysis...\n")

    if approximation == "yes":
        if commuting_info == "yes":
            output_file = output_file or generate_unique_filename("outputRec", ".csv")
            results, pre_api_errors, api_calls, post_api_errors = overlap_rec(
                csv_file, input_dir, api_key, 
                home_a_lat, home_a_lon, work_a_lat, work_a_lon, home_b_lat,
                home_b_lon, work_b_lat, work_b_lon, id_column,
                output_csv=output_file, threshold=int(threshold), width=int(width), method=method,
                skip_invalid=skip_invalid, save_api_info=save_api_info)
            options["Pre-API Error Count"] = pre_api_errors
            options["Post-API Error Count"] = post_api_errors
            options["Total API Calls"] = api_calls
            write_log(output_file, options, input_dir)
        elif commuting_info == "no":
            output_file = output_file or generate_unique_filename("outputRec_only_overlap", ".csv")
            results, pre_api_errors, api_calls, post_api_errors = only_overlap_rec(
                csv_file, input_dir, api_key, home_a_lat, home_a_lon, work_a_lat, work_a_lon, home_b_lat,
                home_b_lon, work_b_lat, work_b_lon, id_column,
                output_csv=output_file, threshold=int(threshold), width=int(width), method=method,
                skip_invalid=skip_invalid, save_api_info=save_api_info)
            options["Pre-API Error Count"] = pre_api_errors
            options["Post-API Error Count"] = post_api_errors
            options["Total API Calls"] = api_calls
            write_log(output_file, options, input_dir)

    elif approximation == "no":
        if commuting_info == "yes":
            output_file = output_file or generate_unique_filename("outputRoutes", ".csv")
            results, pre_api_errors, api_calls, post_api_errors = process_routes_with_csv(
                csv_file, input_dir, api_key, home_a_lat, home_a_lon, work_a_lat, work_a_lon, home_b_lat,
                home_b_lon, work_b_lat, work_b_lon, id_column, method=method, output_csv=output_file, 
                skip_invalid=skip_invalid, save_api_info=save_api_info)
            options["Pre-API Error Count"] = pre_api_errors
            options["Post-API Error Count"] = post_api_errors
            options["Total API Calls"] = api_calls
            write_log(output_file, options, input_dir)
        elif commuting_info == "no":
            output_file = output_file or generate_unique_filename("outputRoutes_only_overlap", ".csv")
            print(f"[INFO] Output will be written to: {output_file}")
            results, pre_api_errors, api_calls, post_api_errors = process_routes_only_overlap_with_csv(
                csv_file, input_dir, api_key, home_a_lat, home_a_lon, work_a_lat, work_a_lon, home_b_lat,
                home_b_lon, work_b_lat, work_b_lon, id_column, method=method, output_csv=output_file,
                skip_invalid=skip_invalid, save_api_info=save_api_info)
            options["Pre-API Error Count"] = pre_api_errors
            options["Post-API Error Count"] = post_api_errors
            options["Total API Calls"] = api_calls
            write_log(output_file, options, input_dir)

    elif approximation == "yes with buffer":
        output_file = output_file or generate_unique_filename("buffer_intersection_results", ".csv")
        results, pre_api_errors, api_calls, post_api_errors = process_routes_with_buffers(
            csv_file=csv_file, input_dir=input_dir, api_key=api_key, 
            home_a_lat=home_a_lat, home_a_lon=home_a_lon, work_a_lat=work_a_lat, work_a_lon= work_a_lon, home_b_lat=home_b_lat,
            home_b_lon=home_b_lon, work_b_lat=work_b_lat, work_b_lon=work_b_lon, id_column=id_column, 
            output_csv=output_file, buffer_distance=buffer, method=method,
            skip_invalid=skip_invalid, save_api_info=save_api_info)
        options["Pre-API Error Count"] = pre_api_errors
        options["Post-API Error Count"] = post_api_errors
        options["Total API Calls"] = api_calls
        write_log(output_file, options, input_dir)

    elif approximation == "closer to precision":
        if commuting_info == "yes":
            output_file = output_file or generate_unique_filename("closest_nodes_buffer_results", ".csv")
            results, pre_api_errors, api_calls, post_api_errors = process_routes_with_closest_nodes(
                csv_file=csv_file, input_dir = input_dir, api_key=api_key, 
                home_a_lat=home_a_lat, home_a_lon=home_a_lon, work_a_lat=work_a_lat, work_a_lon=work_a_lon, home_b_lat=home_b_lat,
                home_b_lon=home_b_lon, work_b_lat=work_b_lat, work_b_lon=work_b_lon, id_column=id_column, buffer_distance=buffer, method=method, output_csv=output_file,
                skip_invalid=skip_invalid, save_api_info=save_api_info)
            options["Pre-API Error Count"] = pre_api_errors
            options["Post-API Error Count"] = post_api_errors
            options["Total API Calls"] = api_calls
            write_log(output_file, options, input_dir)
        elif commuting_info == "no":
            output_file = output_file or generate_unique_filename("closest_nodes_buffer_only_overlap", ".csv")
            results, pre_api_errors, api_calls, post_api_errors = process_routes_with_closest_nodes_simple(
                csv_file=csv_file, input_dir=input_dir, api_key=api_key, 
                home_a_lat=home_a_lat, home_a_lon=home_a_lon, work_a_lat=work_a_lat, work_a_lon=work_a_lon, home_b_lat=home_b_lat,
                home_b_lon=home_b_lon, work_b_lat=work_b_lat, work_b_lon=work_b_lon, id_column=id_column, 
                buffer_distance=buffer, method=method, output_csv=output_file,
                skip_invalid=skip_invalid, save_api_info=save_api_info)
            options["Pre-API Error Count"] = pre_api_errors
            options["Post-API Error Count"] = post_api_errors
            options["Total API Calls"] = api_calls
            write_log(output_file, options, input_dir)

    elif approximation == "exact":
        if commuting_info == "yes":
            output_file = output_file or generate_unique_filename("exact_intersection_buffer_results", ".csv")
            if csv_file is None:
                raise ValueError("csv_file must not be None when calling process_routes_with_exact_intersections.")
            results, pre_api_errors, api_calls, post_api_errors = process_routes_with_exact_intersections(
                csv_file=csv_file, input_dir=input_dir, api_key=api_key, home_a_lat=home_a_lat, home_a_lon=home_a_lon, work_a_lat=work_a_lat, work_a_lon=work_a_lon, home_b_lat=home_b_lat,
                home_b_lon=home_b_lon, work_b_lat=work_b_lat, work_b_lon=work_b_lon, id_column=id_column,
                buffer_distance=buffer, method=method, output_csv=output_file,
                skip_invalid=skip_invalid, save_api_info=save_api_info)
            options["Pre-API Error Count"] = pre_api_errors
            options["Post-API Error Count"] = post_api_errors
            options["Total API Calls"] = api_calls
            write_log(output_file, options, input_dir)
        elif commuting_info == "no":
            output_file = output_file or generate_unique_filename("exact_intersection_buffer_only_overlap", ".csv")
            results, pre_api_errors, api_calls, post_api_errors = process_routes_with_exact_intersections_simple(
                csv_file=csv_file, input_dir=input_dir, api_key=api_key, 
                home_a_lat=home_a_lat, home_a_lon=home_a_lon, work_a_lat=work_a_lat, work_a_lon=work_a_lon, home_b_lat=home_b_lat,
                home_b_lon=home_b_lon, work_b_lat=work_b_lat, work_b_lon=work_b_lon, id_column=id_column,
                buffer_distance=buffer, method=method, output_csv=output_file,
                skip_invalid=skip_invalid, save_api_info=save_api_info)
            options["Pre-API Error Count"] = pre_api_errors
            options["Post-API Error Count"] = post_api_errors
            options["Total API Calls"] = api_calls
            write_log(output_file, options, input_dir)

    if save_api_info is True:
        os.makedirs(output_dir, exist_ok=True)  # Ensure the ResultsCommuto folder exists
        cache_path = os.path.join(output_dir, "api_response_cache.pkl")
        with open(cache_path, "wb") as f:
            pickle.dump(api_response_cache, f)

