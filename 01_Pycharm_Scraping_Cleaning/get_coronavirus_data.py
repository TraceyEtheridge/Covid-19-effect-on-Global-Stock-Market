import pandas as pd
import datetime as dt
import os
import time
from collections import defaultdict

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class CoronavirusData:
    """
    :get daily coronavirus infection data for selected countries
    """

    def __init__(self, logger, config, abs_path):
        self.logger = logger
        self.config = config
        self.abs_path = abs_path
        self.df_country_codes = self.get_country_region_codes()

    def get_country_region_codes(self):
        """
        :Import Country Codes with matching WHO Region Code
        :return: dataframe containing country and region codes use in WHO URL's
        """
        country_codes_file_path = os.path.join(self.abs_path, self.config['inputs']['inputs_dir'],
                                               self.config['inputs']['country_codes_file'])
        df_country_codes = pd.read_csv(country_codes_file_path)

        # Taiwain (TW) and Hong Kong (HK) are grouped as China (CN) on the coronavirus website
        df_country_codes['Country_Code'] = df_country_codes['Country_Code'].replace('TW', 'CN').replace('HK', 'CN')

        # Get unique values to use in URL construction
        self.df_country_codes = df_country_codes[['Country_Code', 'WHO_region']].drop_duplicates()

        return self.df_country_codes

    def get_coronavirus_data(self, country_code, region_code):
        """
        :get daily coronavirus infection data for a single country
        :return: dataframe containing daily coronavirus infections for a single country
        """
        # Open connection and grab page
        corona_url = "https://covid19.who.int/region/" + region_code.lower() + "/country/" + country_code.lower()
        option = Options()
        option.headless = True
        option.add_argument("window-size=1920,1080")
        chromedriver_path = os.path.join(self.abs_path, self.config['chromedriver']['chromedriver_dir'],'chromedriver')
        driver = webdriver.Chrome(chromedriver_path, options=option)
        driver.get(corona_url)
        driver.maximize_window()

        # Find the chart element and get its size and location. Important so we know where to move the cursor
        element_path = '/html/body/div[1]/div[1]/div/div[4]/div[3]/div[2]/div[2]/div'
        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, element_path)))

        element_rect_path = '/html/body/div[1]/div[1]/div/div[4]/div[3]/div[2]/div[2]/div/*[name()="svg"]/*[name()="rect"]'
        element_rec = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, element_rect_path)))
        size_rect = element_rec.size
        width_rect = size_rect['width']

        # Get the first date value pair
        action = webdriver.ActionChains(driver)
        driver.execute_script("arguments[0].scrollIntoView();", element)
        time.sleep(3)
        action.move_to_element_with_offset(element, width_rect - 1, 10).perform()

        date_xpath = '/html/body/div[1]/div[1]/div/div[4]/div[3]/div[2]/div[2]/div/div/div/div[2]/div[1]'
        value_xpath = '/html/body/div[1]/div[1]/div/div[4]/div[3]/div[2]/div[2]/div/div/div/div[2]/div[2]/div[1]/div[1]/span/div/span'

        date = driver.find_element_by_xpath(date_xpath).text
        value = driver.find_element_by_xpath(value_xpath).text

        # Keep the cursor moving left to pick up each date value pair. Note: this will result in many duplicate values
        # that we can remove when performing data cleaning

        corona_dict = defaultdict(list) # required over normal dict because we are polluting the dataset with duplicates
        corona_dict[date].append(value)

        limit = dt.datetime.strptime('04/01/20', '%d/%m/%y')
        #limit = dt.datetime.strptime('1/11/20', '%d/%m/%y') #FOR TESTING PURPOSES - CAN DELETE
        pace = -2

        while True:
            action = webdriver.ActionChains(driver)
            action.move_by_offset(pace, 0).perform()
            date = driver.find_element_by_xpath(date_xpath).text
            value = driver.find_element_by_xpath(value_xpath).text

            if dt.datetime.strptime(date, '%B %d, %Y') < limit:
                break

            # in real life you would skip the value if the date already exists in the dictionary, however in order to
            # pollute the dataset with duplicates for the cleaning stage, we will add extra values in list form against
            # a date.
            if date in corona_dict:
                # pass     # efficient code would pass here but value appended instead
                corona_dict[date].append(value)
            else:
                corona_dict[date].append(value)

        df = pd.DataFrame({'date': corona_dict.keys(), 'daily_cases': corona_dict.values()})
        df['Country'] = country_code

        driver.quit()

        return df

    def get_coronavirus_data_all_countries(self):
        """
        get daily coronavirus infection data for all selected countries
        :return: dataframe containing daily coronavirus infections for selected countries
        """
        df = pd.DataFrame()

        for country, region in zip(self.df_country_codes['Country_Code'], self.df_country_codes['WHO_region']):
            try:
                df_temp = self.get_coronavirus_data(country, region)
                df = df.append(df_temp)
                self.logger.info('{} added to dataframe'.format(country))
            except:
                self.logger.info('{} was not found on website'.format(country))
                pass

        return df
