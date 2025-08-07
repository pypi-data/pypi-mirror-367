import sys
from pathlib import Path

import numpy as np
from alive_progress import alive_bar

from cardiotensor.utils.DataReader import DataReader
from cardiotensor.utils.downsampling import (
    downsample_vector_volume,
    downsample_volume,
)
from cardiotensor.utils.utils import (
    read_conf_file,
)


def angle_between_vectors(vec1: np.ndarray, vec2: np.ndarray) -> np.ndarray:
    """
    Calculates the element-wise angle between two vector fields.

    Args:
        vec1 (np.ndarray): First vector field with shape (3, z, y, x).
        vec2 (np.ndarray): Second vector field with shape (3, z, y, x).

    Returns:
        np.ndarray: Array of angles (degrees) with shape (z, y, x).
    """
    dot_product = np.sum(vec1 * vec2, axis=0)
    magnitude_vec1 = np.linalg.norm(vec1, axis=0)
    magnitude_vec2 = np.linalg.norm(vec2, axis=0)

    epsilon = 1e-10
    magnitude_vec1 = np.maximum(magnitude_vec1, epsilon)
    magnitude_vec2 = np.maximum(magnitude_vec2, epsilon)

    cos_theta = dot_product / (magnitude_vec1 * magnitude_vec2)
    cos_theta = np.clip(cos_theta, -1.0, 1.0)

    return np.rad2deg(np.arccos(cos_theta))


def find_consecutive_points(
    start_point: tuple[int, int, int],
    vector_field: np.ndarray,
    num_steps: int = 4,
    max_length: float = 10,
    angle_threshold: float = 60,
) -> list[tuple]:
    """
    Finds consecutive points in the direction specified by the vector field.

    Args:
        start_point (Tuple[int, int, int]): Starting point (z, y, x).
        vector_field (np.ndarray): Vector field of shape (3, Z, Y, X).
        num_steps (int): Number of steps to take in the vector direction.
        max_length  (float): Length of each segment.
        angle_threshold (float): Threshold to stop when angle deviation exceeds.

    Returns:
        List[Tuple[float, float, float]]: List of consecutive points.
    """
    consecutive_points = [tuple(float(coord) for coord in start_point)]
    current_point = np.array(start_point, dtype=float)
    direction_vector_tmp = np.array([])

    for _ in range(num_steps):
        z, y, x = map(int, np.round(current_point))

        if (
            0 <= z < vector_field.shape[1]
            and 0 <= y < vector_field.shape[2]
            and 0 <= x < vector_field.shape[3]
        ):
            direction_vector = vector_field[:, z, y, x] * max_length / num_steps
            if np.isnan(direction_vector).any():
                break
            if direction_vector_tmp.any():
                if (
                    angle_between_vectors(direction_vector_tmp, direction_vector)
                    > angle_threshold
                ):
                    break
            # Calculate the next point by moving in the direction of the vector
            next_point = current_point + direction_vector

            # Ensure the point is within bounds
            next_point_int = tuple(map(int, np.round(next_point)))
            if (
                0 <= next_point_int[0] < vector_field.shape[1]
                and 0 <= next_point_int[1] < vector_field.shape[2]
                and 0 <= next_point_int[2] < vector_field.shape[3]
            ):
                if len(next_point) == 3:  # Ensure tuple has exactly three elements
                    consecutive_points.append(tuple(next_point))
                current_point = tuple(map(int, next_point))
            else:
                break  # Stop if we go out of bounds
        else:
            break  # Stop if the current point is out of bounds

        direction_vector_tmp = direction_vector

    return consecutive_points


def write_am_file(
    consecutive_points_list: list[list[tuple[float, float, float]]],
    HA_angle: list[float],
    z_angle: list[float],
    file_path: str = "output.am",
) -> None:
    """
    Writes an .am file with start and end vertices for each element in `consecutive_points_list`.

    Args:
        consecutive_points_list (List[List[Tuple[float, float, float]]]): Nested list containing points (x, y, z).
        HA_angle (List[float]): List of helix angles for each point.
        z_angle (List[float]): List of z-axis angles for each point.
        file_path (str): Path to the output file. Defaults to "output.am".
    """

    N_point = sum(len(segment) for segment in consecutive_points_list)

    with open(file_path, "w") as f:
        f.write("# AmiraMesh 3D ASCII 3.0\n\n\n")
        f.write(f"define VERTEX {len(consecutive_points_list) * 2}\n")
        f.write(f"define EDGE {len(consecutive_points_list)}\n")
        f.write(f"define POINT {N_point}\n")
        f.write('\nParameters {\n    ContentType "HxSpatialGraph"\n}\n\n')
        f.write("VERTEX { float[3] VertexCoordinates } @1\n")
        f.write("EDGE { int[2] EdgeConnectivity } @2\n")
        f.write("EDGE { int NumEdgePoints } @3\n")
        f.write("POINT { float[3] EdgePointCoordinates } @4\n")
        f.write("POINT { float thickness } @5\n")
        f.write("POINT { float HA_angle } @6\n")
        f.write("POINT { float z_angle } @7\n")
        f.write("\n# Data section follows\n")

        # Write vertex data
        f.write("@1\n")
        for segment in consecutive_points_list:
            if len(segment) >= 2:
                start, end = segment[0], segment[-1]
                f.write(f"{start[0]} {start[1]} {start[2]}\n")
                f.write(f"{end[0]} {end[1]} {end[2]}\n")

        # Write edges
        f.write("\n@2\n")
        for i in range(len(consecutive_points_list)):
            f.write(f"{i * 2} {i * 2 + 1}\n")

        # Write the number of points per edge
        f.write("\n@3\n")
        for segment in consecutive_points_list:
            f.write(f"{len(segment)}\n")

        # Write edge point coordinates
        f.write("\n@4\n")
        for segment in consecutive_points_list:
            for point in segment:
                f.write(f"{point[0]} {point[1]} {point[2]}\n")

        # Write thickness
        f.write("\n@5\n")
        for segment in consecutive_points_list:
            f.write("1.0\n" * len(segment))

        # Write helix angles
        f.write("\n@6\n")
        for angle in HA_angle:
            f.write(f"{angle}\n")

        # Write z-axis angles
        f.write("\n@7\n")
        for angle in z_angle:
            f.write(f"{angle}\n")

    print(f"Amira file written to {file_path}")


def amira_writer(
    conf_file_path: str,
    start_index: int | None = None,
    end_index: int | None = None,
    bin_factor: int | None = None,
    num_ini_points: int = 20000,
    num_steps: int = 1000000,
    max_length: float = 20.0,
    angle_threshold: float = 60.0,
    segment_min_length_threshold: int = 10,
) -> None:
    """
    Processes a 3D vector field and generates an AmiraMesh (.am) file.

    Args:
        conf_file_path (Path): Path to the configuration file.
        start_index (Optional[int]): Starting index for processing. Defaults to 0.
        end_index (Optional[int]): Ending index for processing. Defaults to the end of the volume.
        bin_factor (Optional[int]): Downsampling factor. If specified, downsampling will be applied.
        num_ini_points (int): Number of initial random points to sample. Defaults to 20000.
        num_steps (int): Maximum number of steps for tracing each vector. Defaults to 1000000.
        max_length  (float): Length of each segment along the vector direction. Defaults to 20.0.
        angle_threshold (float): Maximum allowable angle between consecutive vectors. Defaults to 60.0.
        segment_min_length_threshold (int): Minimum length of segments to retain. Defaults to 30.

    Returns:
        None
    """
    if start_index is None:
        start_index = 0

    try:
        params = read_conf_file(conf_file_path)
    except Exception as e:
        print(f"⚠️  Error reading parameter file '{conf_file_path}': {e}")
        sys.exit(1)

    # Extracting parameters safely using .get() with defaults where necessary
    VOLUME_PATH = params.get("IMAGES_PATH", "")
    OUTPUT_DIR = params.get("OUTPUT_PATH", "./output")
    OUTPUT_FORMAT = params.get("OUTPUT_FORMAT", "jp2")
    VOXEL_SIZE = params.get("VOXEL_SIZE", 1)

    OUTPUT_DIR = Path(OUTPUT_DIR)

    data_reader_volume = DataReader(VOLUME_PATH)

    if end_index is None:
        end_index = data_reader_volume.shape[0]

    output_npy = OUTPUT_DIR / "eigen_vec"
    output_HA = OUTPUT_DIR / "HA"

    if not list(output_npy.glob("*.npy")):
        print(f"⚠️  No eigen vector files found in {output_npy}.")
        print("Steps to resolve:")
        print("1. Ensure the 'VECTORS' option is enabled in your .conf file.")
        print("2. Run the orientation computation step to generate these files.")
        print("3. Verify the output directory for the expected .npy files.")
        sys.exit("Exiting due to missing eigen vector files.")

    if bin_factor:
        downsample_vector_volume(output_npy, bin_factor, OUTPUT_DIR)
        output_npy = OUTPUT_DIR / f"bin{bin_factor}/eigen_vec"

        downsample_volume(output_HA, bin_factor, OUTPUT_DIR, OUTPUT_FORMAT)
        output_HA = OUTPUT_DIR / f"bin{bin_factor}/HA"

        start_index = int(start_index / bin_factor)
        end_index = int(end_index / bin_factor)

    # npy_list = sorted(list(output_npy.glob("*.npy")))

    data_reader_vector = DataReader(output_npy)
    vector_field = data_reader_vector.load_volume(
        start_index=start_index, end_index=end_index
    )

    # vector_field = load_volume(npy_list, start_index=start_index, end_index=end_index)
    vector_field = np.moveaxis(vector_field, 0, 1)

    print("\nAlign vectors in same direction")
    # Flip the vectors where the z-component is negative
    vector_field[:, vector_field[0] > 0] *= -1

    print("Mask creation")
    mask_volume = (~np.isnan(vector_field).any(axis=0)).astype(np.uint8)
    # mask_volume = np.where(HA_volume == 0, 0, 1)

    print("\nCreation of random points")
    valid_indices = np.argwhere(mask_volume == 1)

    if len(valid_indices) < num_ini_points:
        print(
            "Not enough points with mask value 1. Adjust the number of points or check mask_volume."
        )
        sys.exit("Exiting due to insufficient valid points in the mask.")
    else:
        random_points = valid_indices[
            np.random.choice(valid_indices.shape[0], num_ini_points, replace=False)
        ]

    consecutive_points_list = []
    with alive_bar(len(random_points), title="Processing Points") as bar:
        for point in random_points:
            point = tuple(int(x) for x in point)
            consecutive_points = find_consecutive_points(
                point,
                vector_field,
                num_steps=num_steps,
                max_length=max_length,
                angle_threshold=angle_threshold,
            )
            consecutive_points = [
                (point[0] + start_index, point[1], point[2])
                for point in consecutive_points
            ]

            if len(consecutive_points) >= segment_min_length_threshold:
                consecutive_points_list.append(consecutive_points)
            bar()

    data_reader_HA = DataReader(output_HA)
    HA_volume = data_reader_HA.load_volume(start_index=start_index, end_index=end_index)
    # HA_volume = HA_volume *90/255 - 90

    print(f"{len(consecutive_points_list)}")

    HA_angle = []
    for point_list in consecutive_points_list:
        for point in point_list:
            HA_angle.append(
                float(
                    HA_volume[int(point[0] - start_index), int(point[1]), int(point[2])]
                )
            )

    z_angle = []
    for point_list in consecutive_points_list:
        for point in point_list:
            vector = vector_field[
                :, int(point[0] - start_index), int(point[1]), int(point[2])
            ]

            # Calculate the angle in radians
            theta = np.arccos(abs(vector[0]) / np.linalg.norm(vector))

            # Convert the angle to degrees if needed
            theta_degrees = np.degrees(theta)
            z_angle.append(theta_degrees)

    if bin_factor:
        VOXEL_SIZE *= bin_factor

    print(f"Voxel size: {VOXEL_SIZE}um")

    # Multiply each element by pixel size
    consecutive_points_list = scale_points(consecutive_points_list, VOXEL_SIZE)

    # Reorder each point in each list from (z, y, x) to (x, y, z)
    consecutive_points_list = [
        [(point[2], point[1], point[0]) for point in point_list]
        for point_list in consecutive_points_list
    ]

    write_am_file(
        consecutive_points_list, HA_angle, z_angle, file_path=OUTPUT_DIR / "output.am"
    )


def scale_points(
    consecutive_points: list[list[tuple[float, float, float]]],
    pixel_size: float,
) -> list[list[tuple[float, float, float]]]:
    """
    Scales each coordinate in a list of points by the specified pixel size.

    Args:
        consecutive_points (List[List[Tuple[float, float, float]]]): Nested list where each sublist contains tuples representing points (x, y, z).
        pixel_size (float): The scaling factor for each coordinate (e.g., pixel size in micrometers).

    Returns:
        List[List[Tuple[float, float, float]]]: A new list with each point's coordinates scaled by pixel_size.
    """
    scaled_points = []

    for point_list in consecutive_points:
        scaled_point_list = [
            (point[0] * pixel_size, point[1] * pixel_size, point[2] * pixel_size)
            for point in point_list
        ]
        scaled_points.append(scaled_point_list)

    return scaled_points


def amira_writer(
    conf_file_path: str,
    start_index: int | None = None,
    end_index: int | None = None,
    bin_factor: int | None = None,
    num_ini_points: int = 20000,
    num_steps: int = 1000000,
    max_length: float = 20.0,
    angle_threshold: float = 60.0,
    segment_min_length_threshold: int = 10,
) -> None:
    import fury
    import numpy as np
    from dipy.data import fetch_bundles_2_subjects, read_bundles_2_subjects
    from dipy.tracking.streamline import length, transform_streamlines

    # Set to True to open interactive windows (one per visualization).
    interactive = True

    # 1. Download and load bundle data & FA map for subject "subj_1"
    fetch_bundles_2_subjects()
    dix = read_bundles_2_subjects(
        subj_id="subj_1", metrics=["fa"], bundles=["cg.left", "cst.right"]
    )

    fa = dix["fa"]
    affine = dix["affine"]
    bundle = dix["cg.left"]

    # Transform bundle from world to native image coordinates
    bundle_native = transform_streamlines(bundle, np.linalg.inv(affine))

    # Common scene setup
    scene = fury.window.Scene()
    camera_params = {
        "position": (-176.42, 118.52, 128.20),
        "focal_point": (113.30, 128.31, 76.56),
        "view_up": (0.18, 0.00, 0.98),
    }
    scene.set_camera(**camera_params)

    # =============================================================================
    # 1) Show every streamline with an orientation color (default line coloring)
    # =============================================================================
    stream_actor = fury.actor.line(bundle_native)
    scene.add(stream_actor)

    if interactive:
        fury.window.show(scene, size=(600, 600), reset_camera=False)
    fury.window.record(scene=scene, out_path="bundle1.png", size=(600, 600))

    # =============================================================================
    # 2) Show every point with a value from a volume (FA) using default colormap
    # =============================================================================
    scene.clear()
    scene.set_camera(**camera_params)

    # Pass FA as the array of scalar values per point
    stream_actor2 = fury.actor.line(bundle_native, fa, linewidth=0.1)
    bar = fury.actor.scalar_bar()
    scene.add(stream_actor2)
    scene.add(bar)

    if interactive:
        fury.window.show(scene, size=(600, 600), reset_camera=False)
    fury.window.record(scene=scene, out_path="bundle2.png", size=(600, 600))

    # =============================================================================
    # 3) Show every point with a value from FA using a custom colormap (white->red)
    # =============================================================================
    scene.clear()
    scene.set_camera(**camera_params)

    hue = (0.0, 0.0)  # red only
    saturation = (0.0, 1.0)  # white to red
    lut_cmap = fury.actor.colormap_lookup_table(
        hue_range=hue, saturation_range=saturation
    )
    stream_actor3 = fury.actor.line(
        bundle_native, fa, linewidth=0.1, lookup_colormap=lut_cmap
    )
    bar2 = fury.actor.scalar_bar(lut_cmap)
    scene.add(stream_actor3)
    scene.add(bar2)

    if interactive:
        fury.window.show(scene, size=(600, 600), reset_camera=False)
    fury.window.record(scene=scene, out_path="bundle3.png", size=(600, 600))

    # =============================================================================
    # 4) Show every bundle with a specific color (orange)
    # =============================================================================
    scene.clear()
    scene.set_camera(**camera_params)

    orange = (1.0, 0.5, 0.0)
    stream_actor4 = fury.actor.line(bundle_native, orange, linewidth=0.1)
    scene.add(stream_actor4)

    if interactive:
        fury.window.show(scene, size=(600, 600), reset_camera=False)
    fury.window.record(scene=scene, out_path="bundle4.png", size=(600, 600))

    # =============================================================================
    # 5) Show every streamline of a bundle with a different color based on length
    # =============================================================================
    scene.clear()
    scene.set_camera(**camera_params)

    lengths = length(bundle_native)
    hue = (0.5, 0.5)  # blue only
    saturation = (0.0, 1.0)  # black to white
    lut_cmap_len = fury.actor.colormap_lookup_table(
        scale_range=(lengths.min(), lengths.max()),
        hue_range=hue,
        saturation_range=saturation,
    )
    stream_actor5 = fury.actor.line(
        bundle_native, lengths, linewidth=0.1, lookup_colormap=lut_cmap_len
    )
    bar3 = fury.actor.scalar_bar(lut_cmap_len)
    scene.add(stream_actor5)
    scene.add(bar3)

    if interactive:
        fury.window.show(scene, size=(600, 600), reset_camera=False)
    fury.window.record(scene=scene, out_path="bundle5.png", size=(600, 600))

    # =============================================================================
    # 6) Show every point of every streamline with a distinct random color
    # =============================================================================
    scene.clear()
    scene.set_camera(**camera_params)

    # Generate a random RGB color per point (stacked to match bundle_native shape)
    colors = [np.random.rand(*streamline.shape) for streamline in bundle_native]
    # Concatenate into a single array of shape (N_points_total, 3)
    concatenated_colors = np.vstack(colors)
    stream_actor6 = fury.actor.line(bundle_native, concatenated_colors, linewidth=0.2)
    scene.add(stream_actor6)

    if interactive:
        fury.window.show(scene, size=(600, 600), reset_camera=False)
    fury.window.record(scene=scene, out_path="bundle6.png", size=(600, 600))

    # =============================================================================
    # 7) Add depth cues to streamline rendering (lines shrink with distance)
    # =============================================================================
    scene.clear()
    scene.set_camera(**camera_params)

    stream_actor7 = fury.actor.line(bundle_native, linewidth=0.5, depth_cue=True)
    scene.add(stream_actor7)

    if interactive:
        fury.window.show(scene, size=(600, 600), reset_camera=False)
    fury.window.record(scene=scene, out_path="bundle7.png", size=(600, 600))

    # =============================================================================
    # 8) Render streamlines as fake tubes (shaded lines)
    # =============================================================================
    scene.clear()
    scene.set_camera(**camera_params)

    stream_actor8 = fury.actor.line(bundle_native, linewidth=3, fake_tube=True)
    scene.add(stream_actor8)

    if interactive:
        fury.window.show(scene, size=(600, 600), reset_camera=False)
    fury.window.record(scene=scene, out_path="bundle8.png", size=(600, 600))

    # =============================================================================
    # 9) Combine depth cues with fake tubes
    # =============================================================================
    scene.clear()
    scene.set_camera(**camera_params)

    stream_actor9 = fury.actor.line(
        bundle_native, linewidth=3, depth_cue=True, fake_tube=True
    )
    scene.add(stream_actor9)

    if interactive:
        fury.window.show(scene, size=(600, 600), reset_camera=False)
    fury.window.record(scene=scene, out_path="bundle9.png", size=(600, 600))

    # =============================================================================
    # 10) Render streamlines as tubes (true 3D tubes)
    # =============================================================================
    scene.clear()
    scene.set_camera(**camera_params)

    stream_actor10 = fury.actor.streamtube(bundle_native, linewidth=0.5)
    scene.add(stream_actor10)

    if interactive:
        fury.window.show(scene, size=(600, 600), reset_camera=False)
    fury.window.record(scene=scene, out_path="bundle10.png", size=(600, 600))


def amira_writer(
    conf_file_path: str,
    start_index: int | None = None,
    end_index: int | None = None,
    bin_factor: int | None = None,
    num_ini_points: int = 20000,
    num_steps: int = 1000000,
    max_length: float = 20.0,
    angle_threshold: float = 60.0,
    segment_min_length_threshold: int = 10,
) -> None:
    import fury
    import numpy as np
    from dipy.data import fetch_bundles_2_subjects, read_bundles_2_subjects
    from dipy.tracking.streamline import transform_streamlines

    # Set to True if you want an interactive FURY window.
    interactive = True

    # 1. Download and load bundle data & FA map for subject "subj_1"
    fetch_bundles_2_subjects()
    dix = read_bundles_2_subjects(
        subj_id="subj_1", metrics=["fa"], bundles=["cg.left", "cst.right"]
    )

    fa = dix["fa"]
    affine = dix["affine"]
    bundle = dix["cg.left"]

    # Transform bundle from world to native image coordinates
    bundle_native = transform_streamlines(bundle, np.linalg.inv(affine))

    # Common scene setup (you can re‐use these params later if you want a consistent camera)
    camera_params = {
        "position": (-176.42, 118.52, 128.20),
        "focal_point": (113.30, 128.31, 76.56),
        "view_up": (0.18, 0.00, 0.98),
    }

    # =============================================================================
    # PART A: (unchanged) Your existing vector‐field → AMIRA‐.am logic goes here
    # =============================================================================
    if start_index is None:
        start_index = 0

    try:
        params = read_conf_file(conf_file_path)
    except Exception as e:
        print(f"⚠️  Error reading parameter file '{conf_file_path}': {e}")
        sys.exit(1)

    # Extract parameters
    VOLUME_PATH = params.get("IMAGES_PATH", "")
    OUTPUT_DIR = Path(params.get("OUTPUT_PATH", "./output"))
    OUTPUT_FORMAT = params.get("OUTPUT_FORMAT", "jp2")
    VOXEL_SIZE = params.get("VOXEL_SIZE", 1)

    data_reader_volume = DataReader(VOLUME_PATH)

    if end_index is None:
        end_index = data_reader_volume.shape[0]

    output_npy = OUTPUT_DIR / "eigen_vec"
    output_HA = OUTPUT_DIR / "HA"

    if not list(output_npy.glob("*.npy")):
        print(f"⚠️  No eigen vector files found in {output_npy}.")
        sys.exit("Exiting due to missing eigen vector files.")

    if bin_factor:
        downsample_vector_volume(output_npy, bin_factor, OUTPUT_DIR)
        output_npy = OUTPUT_DIR / f"bin{bin_factor}/eigen_vec"

        downsample_volume(output_HA, bin_factor, OUTPUT_DIR, OUTPUT_FORMAT)
        output_HA = OUTPUT_DIR / f"bin{bin_factor}/HA"

        start_index = int(start_index / bin_factor)
        end_index = int(end_index / bin_factor)

    data_reader_vector = DataReader(output_npy)
    vector_field = data_reader_vector.load_volume(
        start_index=start_index, end_index=end_index
    )
    vector_field = np.moveaxis(vector_field, 0, 1)

    # Align vectors so that all point “forward” in Z
    vector_field[:, vector_field[0] > 0] *= -1

    # Create a mask where vectors are not NaN
    mask_volume = (~np.isnan(vector_field).any(axis=0)).astype(np.uint8)

    # Sample random “seed” points in mask
    valid_indices = np.argwhere(mask_volume == 1)
    if len(valid_indices) < num_ini_points:
        sys.exit("Exiting: not enough valid mask points.")
    random_points = valid_indices[
        np.random.choice(valid_indices.shape[0], num_ini_points, replace=False)
    ]

    consecutive_points_list: list[list[tuple[float, float, float]]] = []
    with alive_bar(len(random_points), title="Processing Points") as bar:
        for point in random_points:
            pt = tuple(int(x) for x in point)
            consecutive_points = find_consecutive_points(
                pt,
                vector_field,
                num_steps=num_steps,
                max_length=max_length,
                angle_threshold=angle_threshold,
            )
            # Shift back up by start_index along Z
            consecutive_points = [
                (p[0] + start_index, p[1], p[2]) for p in consecutive_points
            ]
            if len(consecutive_points) >= segment_min_length_threshold:
                consecutive_points_list.append(consecutive_points)
            bar()

    data_reader_HA = DataReader(output_HA)
    HA_volume = data_reader_HA.load_volume(start_index=start_index, end_index=end_index)

    HA_angle: list[float] = []
    for seg in consecutive_points_list:
        for z, y, x in seg:
            HA_angle.append(float(HA_volume[int(z - start_index), int(y), int(x)]))

    z_angle: list[float] = []
    for seg in consecutive_points_list:
        for z, y, x in seg:
            vec = vector_field[:, int(z - start_index), int(y), int(x)]
            theta = np.arccos(abs(vec[0]) / np.linalg.norm(vec))
            z_angle.append(np.degrees(theta))

    if bin_factor:
        VOXEL_SIZE *= bin_factor

    # Scale by voxel size (µm) and reorder to (x,y,z)
    consecutive_points_list = scale_points(consecutive_points_list, VOXEL_SIZE)
    consecutive_points_list = [
        [(pt[2], pt[1], pt[0]) for pt in seg] for seg in consecutive_points_list
    ]

    # =============================================================================
    # PART B: Plot your streamlines, coloring each vertex by its HA_angle
    # =============================================================================

    # 1. Convert each segment into a NumPy array of shape (N_points, 3)
    streamlines = [np.asarray(seg, dtype=np.float32) for seg in consecutive_points_list]

    # 2. HA_angle is already a flat list, one angle per‐vertex (in the same order as streamlines)
    HA_array = np.asarray(HA_angle, dtype=np.float32)

    # 3. Create a lookup table (LUT) spanning the HA range (e.g. –90° to +90° or your actual min/max)
    lut_ha = fury.actor.colormap_lookup_table(
        scale_range=(float(HA_array.min()), float(HA_array.max())),
        hue_range=(0.0, 0.7),  # for example: map low HA→red, high HA→blue
        saturation_range=(0.5, 1.0),  # adjust as you like
    )

    # 4. Build a FURY scene and reuse the same camera params:
    scene = fury.window.Scene()
    scene.set_camera(
        position=camera_params["position"],
        focal_point=camera_params["focal_point"],
        view_up=camera_params["view_up"],
    )

    # 5. Create a “line” actor, passing HA_array so that FURY colors each vertex by its HA
    line_actor = fury.actor.line(
        streamlines,
        HA_array,  # per‐vertex scalar array → colormap index
        linewidth=0.5,
        lookup_colormap=lut_ha,
    )
    scalar_bar = fury.actor.scalar_bar(lut_ha)

    scene.add(line_actor)
    scene.add(scalar_bar)

    scene.reset_camera()
    scene.camera_info()

    # 6. Show or record
    if interactive:
        fury.window.show(scene, size=(800, 800), reset_camera=False)
    else:
        fury.window.record(
            scene=scene, out_path="my_streamlines_by_HA.png", size=(800, 800)
        )
