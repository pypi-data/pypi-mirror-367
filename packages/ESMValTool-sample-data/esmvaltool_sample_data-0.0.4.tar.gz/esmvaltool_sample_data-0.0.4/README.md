# Sample data for use with ESMValTool

This repository will contain samples of real data for use with [ESMValTool](https://github.com/ESMValGroup/ESMValTool) for automated testing and possibly for demonstration purposes.
The goal is to keep the repository size small (~ 100 MB), so it can be easily downloaded. We strive to include data that adheres well to the CMIP6 standard and can be loaded using simple [iris](https://github.com/SciTools/iris) commands.

At present, the repository contains 44 monthly, and 35 daily timeseries datasets. The specifications can be found in [`datasets.yml`](esmvaltool_sample_data/datasets.yml).

The data are stored using the data reference syntax structure from DKRZ.

## Usage

The functionality of this repository is kept simple.

After installing [iris](https://scitools-iris.readthedocs.io/en/latest/installing.html), this package can be installed with the command:

```bash
pip install ESMValTool_sample_data
```

Data can be loaded using the following command for daily or monthly timeseries data.

```python
import esmvaltool_sample_data

# load monthly air temperature timeseries data
ts_amon_cubes = load_timeseries_cubes(mip_table='Amon')

# load daily air temperature timeseries data
ts_day_cubes = load_timeseries_cubes(mip_table='day')
```

## config-user.yml

If you want to use this dataset in your ESMValTool projects, add the following lines to your `config-user.yml`:

```yaml
rootpath:
  CMIP6:
    - <path_to_repository>/esmvaltool_sample_data/data/timeseries/CMIP6

drs:
  CMIP6: DKRZ
```

If you have installed `esmvaltool_sample_data`, you can find the `rootpath` settings using `python -c 'import esmvaltool_sample_data, yaml; print(yaml.dump(esmvaltool_sample_data.get_rootpaths()))'`

## License

This work is licensed under Apache 2.0 (code) and CC-BY-SA 4.0 (data).
All data files in the directory ([`esmvaltool_sample_data/data/`](esmvaltool_sample_data/data/)) are derived from CMIP6.
The licensing agreements governing CMIP6 data depend on the model but generally conform to CC-BY-SA 4.0, see the [CMIP6 Terms of Use](https://pcmdi.llnl.gov/CMIP6/TermsOfUse) for more detailed information.
The terms of the Apache 2.0 license are available in the LICENSE file, and the terms of the CC-BY-SA 4.0 license in the [`esmvaltool_sample_data/data/LICENSE`](esmvaltool_sample_data/data/LICENSE) file.

## How to contribute

Suggestions/improvements/edits are most welcome. Please read the [contribution guidelines](CONTRIBUTING.md) before creating an issue or a pull request.
