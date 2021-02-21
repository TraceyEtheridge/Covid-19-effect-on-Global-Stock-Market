# Covid-19-effect-on-Global-Stock-Market
Analysis of the effect of Covid-19 on the global stock market using web scraping

Analysis created for Masters of Science Assignment at the Univeristy of Applied Science Lucerne - Data Collection Integration and Processing - Dec 2020

Please note, some data collection steps deliberately introduced dirty data as a requirement of the project involved cleaning activities. In real life, these items would have been performed more efficiently and this is noted in the code where applicable.

### Data Sources

List of world indices to scrape  
• Source: https://finance.yahoo.com/world-indices

Historical Indices Values  
• Note: Source for one index is shown below, all indices listed on page above are scraped (where exists)  
• https://finance.yahoo.com/quote/%5EGSPC?p=%5EGSPC   
• Scraped using beautiful soup  

Coronavirus Daily New Infections  
• Note: Source for one country is shown below, all countries with index listed from world indices page are scraped (where exists)  
• https://covid19.who.int/region/euro/country/de  
• Scraped using Selenium  

df_indices_country  
• This is a manually created table required to link the country code of an index to a region code used in the formulation of the country page website addresses on the WHO website.
