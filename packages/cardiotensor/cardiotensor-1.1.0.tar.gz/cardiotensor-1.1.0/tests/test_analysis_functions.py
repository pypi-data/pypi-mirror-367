import numpy as np
import pytest
from pathlib import Path

from cardiotensor.analysis.analysis_functions import (
    _calculate_angle_line,
    calculate_intensities,
    find_end_points,
    save_intensity,
)


@pytest.mark.parametrize(
    "p1,p2,expected",
    [
        ((0, 0), (10, 0), 0),
        ((0, 0), (0, 10), 90),
        ((0, 0), (10, 10), 45),
    ],
)
def test_calculate_angle_line(p1, p2, expected):
    assert _calculate_angle_line(p1, p2) == pytest.approx(expected)


def test_calculate_and_save_intensity(tmp_path: Path):
    img = np.ones((10, 10), dtype=np.uint8) * 255
    start_point = (0, 0)
    end_point = (9, 9)

    # Should return a list of intensity profiles
    intensities = calculate_intensities(
        img,
        start_point,
        end_point,
        angle_range=5,
        N_line=10,
    )
    assert isinstance(intensities, list)
    assert all(isinstance(arr, np.ndarray) for arr in intensities)
    assert len(intensities) > 0

    output_file = tmp_path / "intensity.csv"
    save_intensity(intensities, output_file)
    assert output_file.exists()


def test_find_end_points_returns_array():
    start_point = (0, 0)
    end_point = (9, 9)
    points = find_end_points(start_point, end_point, angle_range=10, N_line=5)

    # Should return a NumPy array of shape (N_line, 2)
    assert isinstance(points, np.ndarray)
    assert points.shape == (5, 2)
