import cv2
import networkx as nx
import numpy as np

from scipy.ndimage import distance_transform_edt
from scipy.spatial import cKDTree
from skimage import morphology


def get_skeleton(img):
    """Skeletonize an image.

    Args:
        img (numpy.ndarray): A binary image to be skeletonized.

    Returns:
        numpy.ndarray: The skeletonized image.
    """
    skeleton_img = morphology.skeletonize(img).astype(np.uint8) * 255
    return skeleton_img


def get_skeleton_angle(skeleton_img):
    """Calculate the angle (from verticle line) of the skeleton.

    Args:
        skeleton_img (numpy.ndarray): The skeletonized image.

    Returns:
        float: The angle of the skeleton.
    """
    lines = cv2.HoughLinesP(
        skeleton_img,
        rho=1,
        theta=np.pi / 180,
        threshold=3,
        minLineLength=3,
        maxLineGap=2,
    )

    # If no lines are detected, return NaN values
    if lines is None:
        return np.nan, 0, 0, 0, [], []
    
    # get angle of each line
    angles = []  # Store angles
    lengths = []  # Store total length of lines

    # Calculate angles
    for line in lines:
        x1, y1, x2, y2 = line[0]

        # Avoid division by zero (vertical line case)
        if x2 - x1 == 0:
            angle_with_vertical = 0  # Perfectly vertical line
            length = abs(y2 - y1)

        else:
            theta = np.arctan2(y2 - y1, x2 - x1)  # Angle with horizontal
            theta_deg = np.degrees(theta)  # Convert to degrees
            angle_with_vertical = 90 - abs(theta_deg)  # Angle with vertical
            length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        angles.append(angle_with_vertical)
        lengths.append(length)
    angles = np.array(angles)
    lengths = np.array(lengths)

    # Weighted average
    angle_avg = np.sum(angles * lengths) / np.sum(lengths)
    # get the shallow (60-90), medium (30-60), steep (0-30) angle frequency
    if len(angles) > 0:
        # Define angle masks
        shallow_mask = (angles >= 60) & (angles <= 90)
        medium_mask = (angles >= 30) & (angles < 60)
        steep_mask = (angles >= 0) & (angles < 30)

        # Compute weighted frequencies (as percentages)
        total_weight = np.sum(lengths)
        shallow = np.sum(lengths[shallow_mask]) / total_weight
        medium = np.sum(lengths[medium_mask]) / total_weight
        steep = np.sum(lengths[steep_mask]) / total_weight
    else:
        shallow = medium = steep = 0
    return angle_avg, shallow, medium, steep, angles, lengths


def get_root_info(skeleton_img):
    """Get root information from a skeletonized image.

    Args:
        skeleton_img (numpy.ndarray): The skeletonized binary image.

    Returns:
        G: networkx.Graph: The graph representation of the skeleton.
        roots_info (list): A list containing information about the seed location,
            primary root skeleton location, and lateral roots skeleton location.
    """
    # Get coordinates of white pixels (skeleton pixels)
    points = np.column_stack(np.where(skeleton_img > 0))

    # Return early if no skeleton found
    if len(points) == 0:
        roots_info = {
            "seed_plant_idx": None,
            "seed_plant": None,
            "seed_idx": None,
            "seed_point": None,
            "lateral_num": 0,
            "end_idx": [],
            "end_points": np.array([]),
            "all_endpoints": [],
            "longest_path_idx": [],
            "primary_points": np.array([]),
            "lateral_path_idx": [],
            "lateral_points": np.array([]),
        }
        return nx.Graph(), roots_info

    # Create KD-Tree for fast neighbor search
    tree = cKDTree(points)

    # Define connection distance (usually sqrt(2) for 8-connected)
    distance_threshold = np.sqrt(2) + 0.1  # add small tolerance

    # Find neighbors
    pairs = tree.query_pairs(r=distance_threshold)

    # Build graph from pairs
    G = nx.Graph()
    G.add_nodes_from(range(len(points)))
    G.add_edges_from(pairs)

    longest_length = 0
    longest_path = None
    lateral_num = 0
    seed_plant_idx = None
    seed_plant = None

    for subgraph_nodes in nx.connected_components(G):
        subgraph = G.subgraph(subgraph_nodes)
        # Get endpoints in this subgraph
        endpoints = [node for node, deg in subgraph.degree() if deg == 1]

        if not endpoints:
            continue

        endpoint_coords = np.array([points[node] for node in endpoints])

        # Select the seed point (e.g., smallest x-value)
        seed_idx = endpoints[np.argmin(endpoint_coords[:, 0])]
        seed_point = points[seed_idx]

        # Remove seed from endpoints if desired
        endpoints_wo_seed_idx = [node for node in endpoints if node != seed_idx]
        end_points = points[endpoints_wo_seed_idx]
        lateral_num += len(endpoints_wo_seed_idx)

        for tip_idx in endpoints_wo_seed_idx:
            try:
                path = nx.shortest_path(G, source=seed_idx, target=tip_idx)
                if len(path) > longest_length:
                    longest_length = len(path)
                    longest_path = path
                    seed_plant_idx = seed_idx
                    seed_plant = points[seed_idx]
            except nx.NetworkXNoPath:
                continue

    # get primary root and lateral roots points
    if longest_path is not None:
        primary_points = points[longest_path]
        # Get all indices
        all_indices = np.arange(len(points))

        # Get the indices that are not in longest_path
        lateral_indices = np.setdiff1d(all_indices, longest_path)

        # Now get lateral points
        lateral_points = points[lateral_indices]
    else:
        primary_points = None
        lateral_indices = None
        lateral_points = None

    # Store the info
    roots_info = {
        "seed_plant_idx": seed_plant_idx,
        "seed_plant": seed_plant,
        "seed_idx": seed_idx,
        "seed_point": seed_point,
        "lateral_num": lateral_num - 1,  # exclude the primary tip
        "end_idx": endpoints_wo_seed_idx,
        "end_points": end_points,
        "all_endpoints": endpoints,
        "longest_path_idx": longest_path,
        "primary_points": primary_points,
        "lateral_path_idx": lateral_indices,
        "lateral_points": lateral_points,
    }

    return G, roots_info


def get_skeleton_lengths(skeleton_img, G=None, roots_info=None):
    """Calculate the lengths of the skeleton.

    Args:
        skeleton_img (numpy.ndarray): The skeletonized binary image.

    Returns:
        tuple: A tuple containing the length of the skeleton (float), pixel count (int), and total length using networkx (float).
    """
    if G is None or roots_info is None:
        G, roots_info = get_root_info(skeleton_img)

    # Get coordinates of white pixels (skeleton pixels)
    coords = np.argwhere(skeleton_img > 0)
    coords_map = np.zeros((skeleton_img.shape[0], skeleton_img.shape[1]), dtype=int)
    coords_map[skeleton_img > 0] = np.arange(len(coords))

    # Compute total length: sum of Euclidean distances for all edges
    edge_array = np.array([np.linalg.norm(coords[i] - coords[j]) for i, j in G.edges()])
    total_length = edge_array.sum()

    # get primary root (longest path) length
    if roots_info["primary_points"] is not None:
        distances = np.sqrt(
            np.sum(np.diff(roots_info["primary_points"], axis=0) ** 2, axis=1)
        )
        primary_root_length = np.sum(distances)

    else:
        primary_root_length = None

    # get lateral root length
    if primary_root_length is not None:
        lateral_root_length = total_length - primary_root_length
    else:
        lateral_root_length = total_length

    # get lateral root number
    lateral_root_number = roots_info["lateral_num"]

    # get average lateral root length
    average_lateral_root_length = lateral_root_length / lateral_root_number

    return (
        total_length,
        primary_root_length,
        lateral_root_length,
        lateral_root_number,
        average_lateral_root_length,
    )


def get_diameter(img, skeleton_img=None):
    """Calculate the diameter of the root system.

    Args:
        img (numpy.ndarray): The binary image of the root system.
        skeleton_img (numpy.ndarray, optional): The skeletonized image. If not provided, it will be computed.

    Returns:
        float: The diameter of the root system.
    """
    if skeleton_img is None:
        skeleton_img = get_skeleton(img)

    # Distance transform
    distance_map = distance_transform_edt(img)

    # Get diameters at skeleton points
    diameters = (
        distance_map[skeleton_img == np.max(skeleton_img)] * 2
    )  # diameter = 2 * radius

    # analyze
    mean_diameter = np.nanmean(diameters)
    median_diameter = np.nanmedian(diameters)
    max_diameter = np.nanmax(diameters)

    return mean_diameter, median_diameter, max_diameter, diameters
