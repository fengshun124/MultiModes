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
from time import time

import click

from modules.loader import load_light_curve_data, load_config


def multi_modes(light_curve_df, config_file, output_dir):
    # make a copy of the configuration file in the output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    os.system(f'cp {config_file} {output_dir}')

    print(light_curve_df.head())


@click.command()
@click.option('-c', '--config-file', default='default.cfg',
              type=click.Path(exists=True), help='Path to the configuration file.')
@click.option('-dir', '--data_dir', type=click.Path(exists=True), required=False,
              help='Path to the directory containing light curves. This conflicts with --data-file.')
@click.option('-file', '--data_file', type=click.Path(exists=True), required=False,
              help='Path to the light curve file. This conflicts with --data-dir.')
@click.option('-s', '--skip', is_flag=True, default=False,
              help='Skip the confirmation prompt.')
def main(config_file, data_dir, data_file, skip):
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

    # load configuration file
    multi_modes_config = load_config(config_file)
    output_dir = multi_modes_config['Export']['output_dir']

    # print run information for confirmation
    print(' Multi-Modes Run information '.center(80, '='))
    print('\n' + f' Light Curve Files '.center(80, '-'))
    print(f'{os.path.abspath(os.path.dirname(light_curve_files[0]))}/'
          f'{[os.path.basename(file) for file in light_curve_files]}')
    print('\n' + ' Configuration '.center(80, '-'))
    print(f'config_file: {os.path.abspath(config_file)}')
    print('\n'.join([f'{key}={value}' for key, value in multi_modes_config.items()]))
    print(f'output_dir: {os.path.abspath(output_dir)}')
    print('\n' + '=' * 80)

    if skip:
        print('Skipping confirmation and continuing...')
    else:
        if not click.confirm('Proceed with the above files and configuration?', default=True):
            print('Exiting...')
            return

    # create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f'Created output directory: {output_dir}')

    # process each light curve
    for light_curve_file in light_curve_files:
        start_time = time()
        print(f'Processing light curve: {light_curve_file}')

        # create output directory for each light curve
        light_curve_output_dir = os.path.join(
            output_dir, os.path.basename(light_curve_file).split('.')[0].replace(' ', '_'))
        try:
            multi_modes(
                light_curve_df=load_light_curve_data(light_curve_file, **multi_modes_config['DataColumn']),
                config_file=config_file, output_dir=light_curve_output_dir
            )
        except Exception as e:
            print(f'Error: {e}')

        print(f'Elapsed time: {time() - start_time:.2f} s')


if __name__ == '__main__':
    main()
