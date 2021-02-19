import pandas as pd
import numpy as np


class CleanHistorical:

    def __init__(self, logger, config, df):
        self.logger = logger
        self.config = config
        self.df = df

    def clean_historical_index_data(self):
        """
        Clean historical index data file
        :return: dataframe containing cleaned historical index data
        """
        self.logger.info('clean historical process initiated')
        df_cleaned = self.df.copy()
        # Remove * from column name
        df_cleaned = df_cleaned.rename(columns={'Close*': 'Close', 'Adj Close**': 'Adj Close'})

        # Convert date column to datetime format
        df_cleaned['Date'] = pd.to_datetime(df_cleaned['Date'])

        # Remove ^ from index codes
        df_cleaned['Index'] = df_cleaned['Index'].str.replace('^', '')

        # Convert numerical value columns to float type
        cols_to_float = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
        for col in cols_to_float:
            df_cleaned[col] = df_cleaned[col].str.replace(',', '').replace('-', np.nan).astype(float)

        return df_cleaned
