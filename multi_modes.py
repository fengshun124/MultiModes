"""
MultiModes extracts significant frequencies from variable stars.
It calculates the Lomb-Scargle periodogram,
and performs a non-linear simultaneous fit using a multi-sine function.
The stop criterion can be either the FAP or SNR, based on the analysis type.

@author: David Pamos Ortega (UGR)
@supervisors: Dr. Juan Carlos Suárez Yanes (UGR) & Dr. Antonio García Hernández (UGR)
@expert contributor: Dr. Javier Pascual Granado (IAA)
"""
import os.path

import click
from tqdm.auto import tqdm

from modules.load import import_light_curve_data


@click.command()
@click.option('--config-file', default='default.cfg',
              type=click.Path(exists=True), help='Path to the configuration file.')
@click.option('--data_dir', type=click.Path(exists=True), required=False,
              help='Path to the directory containing light curves. This conflicts with --data-file.')
@click.option('--data_file', type=click.Path(exists=True), required=False,
              help='Path to the light curve file. This conflicts with --data-dir.')
@click.option('--output_dir', type=click.Path(exists=False), default='./output',
              help='Path to the output directory.')
@click.option('-s', '--skip', is_flag=True, default=False,
              help='Skip the confirmation prompt.')
def main(config_file, data_dir, data_file, output_dir, skip):
    """Process light curve data."""
    # initialise light curve file list
    if not data_dir and not data_file:
        data_choice = click.prompt('No data source provided. '
                                   'Do you want to import light curves from a directory or a file?',
                                   type=click.Choice(['directory', 'file'], case_sensitive=False))
        if data_choice == 'directory':
            data_dir = click.prompt('Enter the path to the directory containing light curves',
                                    type=click.Path(exists=True))
        else:
            data_file = click.prompt('Enter the path to the light curve file',
                                     type=click.Path(exists=True))
    elif data_dir and data_file:
        raise click.UsageError('Cannot use --data-dir and --data-file together.')

    # collect light curve files
    if data_dir:
        light_curve_files = [os.path.join(data_dir, file) for file in os.listdir(data_dir)
                             if file.endswith(('.fits', '.csv', '.dat', '.txt'))]
    else:
        light_curve_files = [data_file]

    print(f'light_curve_files: '
          f'{os.path.abspath(os.path.dirname(light_curve_files[0]))}/'
          f'{[os.path.basename(file) for file in light_curve_files]}')
    print(f'config_file: {os.path.abspath(config_file)}')
    print(f'output_dir: {os.path.abspath(output_dir)}')

    if skip:
        print('Skipping confirmation and continuing...')
    else:
        if not click.confirm('Do you want to continue?', default=True):
            print('Aborted.')
            return

    for light_curve_file in tqdm(light_curve_files):
        try:
            light_curve_df = import_light_curve_data(light_curve_file)
            print(light_curve_df)
        except Exception as e:
            print(f'Error: {e}')


if __name__ == '__main__':
    main()
