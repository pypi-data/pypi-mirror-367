from pathlib import Path

import cf_units
import iris

base_dir = Path(__file__).parent

VERBOSE = False

# This ignore list is used to help with debugging only
# for a more permanent solution, add
# problematic datasets the `ignore` section in `../datasets.yml`.
ignore_list = [
    # 'CMIP6/CMIP/AWI/AWI-ESM-1-1-LR/historical/r1i1p1f1/Amon/ta/gn/v20200212',
]


def strip_attributes(cube: 'iris.Cube') -> None:
    """Remove attributes in-place that cause issues with merging and
    concatenation."""
    for attr in ['creation_date', 'tracking_id', 'history']:
        if attr in cube.attributes:
            cube.attributes.pop(attr)


def simplify_time(cube: 'iris.Cube') -> None:
    """Simplifies the time coordinate in-place."""
    coord = cube.coord('time')
    coord.convert_units(
        cf_units.Unit('days since 1850-1-1 00:00:00',
                      calendar=coord.units.calendar))


def load_cubes_from_input_dirs(input_dirs: list) -> 'iris.Cube':
    """Generator that loads all *.nc files from each input dir into a cube."""
    for i, input_dir in enumerate(sorted(input_dirs)):
        if VERBOSE:
            print(f'Loading #{i:02d}:', input_dir)

        files = input_dir.glob('*.nc')
        cubes = iris.load(str(file) for file in files)
        for cube in cubes:
            strip_attributes(cube)
            simplify_time(cube)

        cube = cubes.concatenate_cube()

        if VERBOSE:
            print(f'    {cube.shape=} {cube.data.min()=} {cube.data.max()=}')
            print(f'    {cube.coord("time").units.calendar=}')

        yield cube


def filter_ignored_datasets(dirs, root):
    """Filter datasets defined in the global `ignore` list."""
    for drc in dirs:
        test_drc = str(drc.relative_to(root))
        if test_drc not in ignore_list:
            yield drc
        elif VERBOSE:
            print('Ignored:', test_drc)


def load_timeseries_cubes(mip_table: str = 'Amon') -> list:
    """Returns a list of iris cubes with timeseries data.

    The data are: ta / Amon / historical / r1i1p1f1, any grid, 1950 - onwards.
    All dimensions were reduced to a few steps except for the time dimension.

    Parameters
    ----------
    mip_table: str
        select monthly (`Amon`, default) or daily (`day`) data.

    Returns
    -------
    cubes: list
        list of iris.cube.Cube
    """

    timeseries_dir = base_dir / 'data' / 'timeseries'

    paths = timeseries_dir.glob(f'**/{mip_table}/**/*.nc')
    input_dirs = list(set(path.parent for path in paths))

    input_dirs = list(filter_ignored_datasets(input_dirs, timeseries_dir))

    cubes = load_cubes_from_input_dirs(input_dirs)

    return list(cubes)


def get_rootpaths() -> dict:
    """Return a dict with rootpaths to update the user config in ESMValTool."""
    rootpath = {
        'rootpath': {
            'CMIP6': [
                str(base_dir / 'data' / 'timeseries' / 'CMIP6'),
            ]
        },
        'drs': {
            'CMIP6': 'default',
        },
    }

    return rootpath


if __name__ == '__main__':
    VERBOSE = True

    for mip_table in (
            'Amon',
            'day',
    ):
        print()
        print(f'Loading `{mip_table}`')
        ts = load_timeseries_cubes(mip_table)

        first_cube = ts[0]
        for i, cube in enumerate(ts):
            cube.regrid(grid=first_cube, scheme=iris.analysis.Linear())

            print(i, cube.data.min(), cube.data.max())

        # breakpoint()
