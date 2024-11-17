import configparser

import pandas as pd
from astropy.table import Table


def import_config(config_file):
    """Import configuration settings from a file."""
    config = configparser.ConfigParser()
    config.read(config_file)

    return config


def import_light_curve_data(data_file):
    """Import light curve data from a file."""

    def _standardise_column_names(df):
        """Standardise column names to lowercase."""
        df.columns = df.columns.str.lower()
        return df

    try:
        if data_file.endswith('.fits'):
            # load FITS file
            try:
                light_curve_df = _standardise_column_names(Table.read(data_file).to_pandas())
            except Exception as e:
                raise ValueError(f'Error loading FITS file as pandas DataFrame: {e}')
        else:
            # load CSV-like file (.csv, .dat, .txt)
            try:
                is_has_headers = pd.read_csv(data_file, nrows=0).columns.size > 0

                if is_has_headers:
                    light_curve_df = _standardise_column_names(pd.read_csv(data_file))
                else:
                    light_curve_df = pd.read_csv(data_file, header=None, names=['time', 'flux'])
                    if len(light_curve_df.columns) != 2:
                        raise ValueError('If the file does not have headers, '
                                         'it must have exactly two columns (time, flux).')
            except Exception as e:
                raise ValueError(f'Error loading CSV-like file as pandas DataFrame: {e}')

        # check if the DataFrame has the required columns
        if 'time' not in light_curve_df.columns or 'flux' not in light_curve_df.columns:
            raise ValueError('Headers must include "time" and "flux".')

        # select only 'time' and 'flux' columns and remove rows with NaN values
        light_curve_abbr_df = light_curve_df[['time', 'flux']].dropna()
        n_row_diff = light_curve_df.shape[0] - light_curve_abbr_df.shape[0]
        if n_row_diff > 0:
            print(f'{n_row_diff} rows with NaN values have been removed.')
        return light_curve_abbr_df

    except ValueError as e:
        raise e
    except Exception as e:
        raise ValueError(f'Unexpected error while processing the file: {e}')
