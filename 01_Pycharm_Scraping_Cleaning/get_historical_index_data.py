import pandas as pd
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

class HistoricalIndexData:
    """
    :get historical value of stock indexes
    """

    def __init__(self, logger, config):
        self.config = config
        self.logger = logger

    def get_table_data(self, url):
        """
        :gets data from a table on a webpage
        :return: table and column names
        """

        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'html.parser')
        table = soup.find("table")
        columns = table.find("thead").find_all("th")
        column_names = [c.text for c in columns]

        table_rows = table.find("tbody").find_all("tr")
        table = []
        for r in table_rows:
            td = r.find_all("td")
            row = [tr.string for tr in td]
            table.append(row)

        return table, column_names

    def get_indices_data(self):
        """
        :gets current index codes for stocks classed as top
        world indices per yahoo finance
        :return: dataframe containing index code + summary data
        """
        url = 'https://finance.yahoo.com/world-indices/'
        table, column_names = self.get_table_data(url)
        self.df_indices = pd.DataFrame(table, columns=column_names)
        self.logger.info('df_indices created')

        return self.df_indices

    def get_index_codes(self):
        """
        :creates list of index codes to be used in scraping historical data
        :param df_indices: dataframe containing summary index data
        :return: list containing index code pattern required for yahoo website
        """
        url_codes = []
        for code in self.df_indices['Symbol']:
            if code[0] == '^':
                url_codes.append('%5E' + code)
            else:
                url_codes.append(code)

        self.logger.info('url codes created')

        return url_codes

    def get_historical_data_intermediate(self, url_base, period1, period2, index_code):
        """
        :creates data frame of 100 days of index price data (yahoo limits to 100 table
        rows at a time)
        :param url_base: part of url including index code
        :param period1: start date
        :param period2: end date
        :param index_code: index code
        :return: dataframe of 100 days of index data
        """
        url_date = "period1=" + str(period1) + "&period2=" + str(
            period2) + "&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true"
        url = url_base + url_date

        table, column_names = self.get_table_data(url)

        df = pd.DataFrame(table, columns=column_names)
        df['Index'] = index_code

        return df

    def get_historical_data(self, end_date, cut_date, index_code):
        """
        creates dataframe of historical data for a single index code
        :param end_date: date to get data up to
        :param cut_date: date to get data from
        :param index_code: index code
        :return: dataframe of historical data for an index code
        """
        # First 100 Days and convert date to timestamp required for url
        end_date_dt = datetime.strptime(end_date, '%d %b %Y')
        end_date_dt = end_date_dt + timedelta(hours=1)
        end_date_ts = int(datetime.timestamp(end_date_dt))

        start_date_dt = end_date_dt - timedelta(days=100)
        start_date_ts = int(datetime.timestamp(start_date_dt))

        # beginning date we want to collect data from
        cut_date_dt = datetime.strptime(cut_date, '%d %b %Y')
        cut_date_dt = cut_date_dt + timedelta(hours=1)
        cut_date_ts = int(datetime.timestamp(cut_date_dt))

        # set url
        if index_code[0] == '^':
            url_base = "https://finance.yahoo.com/quote/%5E" + index_code[1:] + "/history?"
        else:
            url_base = "https://finance.yahoo.com/quote/" + index_code + "/history?"

        period1 = start_date_ts
        period2 = end_date_ts

        # get first 100 days historical data
        df = self.get_historical_data_intermediate(url_base, period1, period2, index_code)

        # get rest of data to cut off date
        while period1 > cut_date_ts:
            # Notoe: this causes duplicate entries, in real life we would make period 2 = perod 1 - a day, however
            # to increase possibilities for the data cleaning part of the assignment this has been done on purpose
            period2 = period1
            if (period1 - (100 * 86400)) >= cut_date_ts:  # 100 days times seconds in a day
                period1 = period1 - (100 * 86400)
            else:
                period1 = cut_date_ts

            df_temp = self.get_historical_data_intermediate(url_base, period1, period2, index_code)
            df = df.append(df_temp)

        return df

    def get_historical_data_all_indices(self, index_codes, end_date, cut_date):
        """
        get data for all indices listed
        :param index_codes: list of index codes
        :return: dataframe containing data for all indices in index_codes (where available)
        """
        df = pd.DataFrame()

        for code in index_codes:
            # skip to next index code when a code has no historical data page
            try:
                df_temp = self.get_historical_data(end_date, cut_date, code)
                df = df.append(df_temp)
                self.logger.info('data added for: {}'.format(code))
            except AttributeError:
                self.logger.info('no historical data page for: {}'.format(code))
                pass

        return df
