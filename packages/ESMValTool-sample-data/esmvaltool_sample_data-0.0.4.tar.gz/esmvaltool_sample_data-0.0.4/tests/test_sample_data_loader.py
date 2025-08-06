import iris
import pytest

from esmvaltool_sample_data import load_timeseries_cubes


@pytest.mark.parametrize("mip_table", [
    'amon',
    'day',
])
def test_load_timeseries_cubes(mip_table):
    """Load data and check if the types are OK."""
    cubes = load_timeseries_cubes(mip_table)
    assert isinstance(cubes, list)
    assert all(isinstance(cube, iris.cube.Cube) for cube in cubes)

    for cube in cubes:
        assert cube.data.min() > -2e16
        assert cube.data.max() < 2e16
