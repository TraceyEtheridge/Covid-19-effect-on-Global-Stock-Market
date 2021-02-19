import os
import logging
import yaml
import pandas as pd

from utils.custom_logging import setup_custom_logger
from get_historical_index_data import HistoricalIndexData
from get_coronavirus_data import CoronavirusData
from clean_historical import CleanHistorical


def prepare_environment(abs_path):
    try:
        config = yaml.safe_load(open(config_path))
    except FileNotFoundError:
        logging.error("Config file does not exist")

    # -------------------------------------
    # Set up logger
    # -------------------------------------
    LOGGING_LEVEL = eval(config['logging_setup']['logging_level'])
    log_file = os.path.join(abs_path, config['logging_setup']['log_directory'],
                            'covid_stock_log.log')

    log = setup_custom_logger('CIP Project', LOGGING_LEVEL, flog=log_file)
    log.newline()

    log.info("log file started")

    return log, config


if __name__ == "__main__":
    # Set up environment
    abs_path_config = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
    config_path = os.path.join(abs_path_config, 'config.yml')
    abs_path = os.path.dirname(os.path.abspath(__file__))
    logger, config = prepare_environment(abs_path)
    path_output_folder = os.path.join(abs_path, config['output']['output_dir'])

    scrape_historical_index_data = True
    scrape_coronavirus_data = True
    clean_historical_index_data = True

    # Scrape historical index data
    if scrape_historical_index_data:
        historical_data = HistoricalIndexData(logger, config)
        logger.info('Initialising historical index data')

        end_date = '25 Nov 2020'
        cut_date = '01 Jan 2020'

        df_indices = historical_data.get_indices_data()
        index_codes = df_indices['Symbol']
        df_historical = historical_data.get_historical_data_all_indices(index_codes, end_date, cut_date)

        df_indices.to_csv(os.path.join(path_output_folder, 'df_indices.csv'), index=False)
        df_historical.to_csv(os.path.join(path_output_folder, 'df_historical.csv'), index=False)
        logger.info('df_indices file saved')
        logger.info('df_historical file saved')

    # Scrape Coronavirus Data
    if scrape_coronavirus_data:
        coronavirus_data = CoronavirusData(logger, config, abs_path)
        logger.info('Initialising coronavirus data')

        df_corona = coronavirus_data.get_coronavirus_data_all_countries()
        df_corona.to_csv(os.path.join(path_output_folder, 'df_corona.csv'), index=False)
        logger.info('df_corona file saved')

    if clean_historical_index_data:
        # Clean Historical Data File
        df_historical = pd.read_csv(os.path.join(path_output_folder, 'df_historical.csv'))
        logger.info('df_historical loaded from file')
        data_cleaner = CleanHistorical(logger, config, df_historical)
        df_historical_cleaned = data_cleaner.clean_historical_index_data()
        df_historical_cleaned.to_csv(os.path.join(path_output_folder, 'df_historical_cleaned.csv'), index=False)
        logger.info('df_historical_cleaned file saved')

    # Coronavirus Data to be cleaned in Tableau
