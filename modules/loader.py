import configparser

import pandas as pd
from astropy.table import Table


def load_config(config_file: str) -> dict:
    """Import configuration settings from a file."""
    config = configparser.ConfigParser()
    config.read(config_file)

    default_config = {
        'Calculation': {
            'max_iter_n': 100,
            'os_ratio': 4,
            'max_freq': 100,
        },
        'StoppingCriteria': {
            # stopping criteria, default to be 'SNR'
            'stop': 'SNR',
            # minimum signal-to-noise ratio (SNR)
            'min_snr': 4.0,
            # maximum false alarm probability (FAP)
            'max_fap': .01,
        },
        'DataColumn': {
            # column names for time and flux in the light curve data
            'time_col_name': 'time',
            'flux_col_name': 'flux',
        },
        'Export': {
            # output directory for the results
            'output_dir': './output',
            # save the periodogram every n iterations
            'save_periodogram_interval': 10,
            # save the
        },
    }

    # use default values if the configuration file does not have the required keys
    final_config = {}
    for section, params in default_config.items():
        final_config[section] = {}
        if config.has_section(section):
            for key, default in params.items():
                if config.has_option(section, key):
                    if isinstance(default, int):
                        value = config.getint(section, key)
                    elif isinstance(default, float):
                        value = config.getfloat(section, key)
                    else:
                        value = config.get(section, key)
                    # convert to the type of the default value
                    if isinstance(default, int):
                        value = config.getint(section, key)
                    elif isinstance(default, float):
                        value = config.getfloat(section, key)
                    final_config[section][key] = value
                else:
                    final_config[section][key] = default
                    print(f'Using default value for {section}.{key} in the configuration.')
        else:
            final_config[section] = params
            print(f'Using default values for {section} in the configuration.')

    return final_config


def load_light_curve_data(
        data_file: str, time_col_name: str = 'time', flux_col_name: str = 'flux'
) -> pd.DataFrame:
    """Import light curve data from a file."""
    try:
        if data_file.endswith('.fits'):
            # load FITS file
            try:
                light_curve_df = Table.read(data_file).to_pandas()
            except Exception as e:
                raise ValueError(f'Error loading FITS file as pandas DataFrame: {e}')
        else:
            # load CSV-like file (.csv, .dat, .txt)
            try:
                is_has_headers = pd.read_csv(data_file, nrows=0).columns.size > 0

                if is_has_headers:
                    light_curve_df = pd.read_csv(data_file)
                else:
                    light_curve_df = pd.read_csv(data_file, header=None, names=[time_col_name, flux_col_name])
                    if len(light_curve_df.columns) != 2:
                        raise ValueError('If the file does not have headers, '
                                         'it must have exactly 2 columns for "TIME" and "FLUX".')
            except Exception as e:
                raise ValueError(f'Error loading CSV-like file as pandas DataFrame: {e}')

        # check if the DataFrame has the required columns
        if time_col_name not in light_curve_df.columns or flux_col_name not in light_curve_df.columns:
            raise ValueError(f'Headers must include "{time_col_name}" and "{flux_col_name}".')

        # select only 'time' and 'flux' columns and remove rows with NaN values
        light_curve_abbr_df = light_curve_df[[time_col_name, flux_col_name]].dropna().sort_values(by=time_col_name)
        n_row_diff = light_curve_df.shape[0] - light_curve_abbr_df.shape[0]
        if n_row_diff > 0:
            print(f'{n_row_diff} rows with NaN values have been removed.')
        # update column naming to 'time' and 'flux' for consistency
        return light_curve_abbr_df.rename(columns={time_col_name: 'time', flux_col_name: 'flux'})

    except ValueError as e:
        raise e
    except Exception as e:
        raise ValueError(f'Unexpected error while processing the file: {e}')
