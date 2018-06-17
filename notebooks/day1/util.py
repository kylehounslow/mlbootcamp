"""
Util functions for MLBootcamp
"""
import os
import re
import time
import glob
import shutil
import zipfile
import urllib.request
import pandas as pd

non_decimal = re.compile(r'[^\d.]+') # regex for removing non-decimal characters from string
def parse_beds(string):
    strings = string.lower().split(', ')
    num_beds = None
    for s in strings:
        if "bd" in s:
            try:
                num_beds = float(non_decimal.sub('', s))
            except Exception as e:
                pass
        # treat studio as 0 bedrooms
        elif "studio" in s.lower():
            num_beds = 0
        return num_beds

def parse_bath(string):
    strings = string.lower().split(', ')
    num_bath = None
    for s in strings:
        if "ba" in s:
            try:
                num_bath = float(non_decimal.sub('', s))
            except Exception as e:
                pass
            finally:
                return num_bath
def parse_sqft(string):
    strings = string.lower().split(', ')
    sqft = None
    for s in strings:
        if "ft" in s:
            try:
                sqft = float(non_decimal.sub('', s))
            except Exception as e:
                pass
            finally:
                return sqft

def parse_property_type(string):
    # property types mapping
    property_types = {'Condo For Sale': 'condo', 
                      'House For Sale': 'house', 
                      'Apartment For Sale': 'apartment', 
                      'New Construction': 'new',
                      'Foreclosure': 'foreclosure', 
                       'Lot/Land For Sale': 'lot', 
                      'Coming Soon': 'coming', 
                      'Co-op For Sale': 'coop',
                      'Auction': 'auction', 
                      'For Sale by Owner': None, 
                      'Townhouse For Sale': 'townhouse'}
    try:
        property_type = property_types[string]
    except KeyError as e:
        print(e)
        property_type = None
    finally:
        return property_type

def download_extract_data(data_dir: str):
    """
    Download zipfile and extract its contents to data_dir
    Args:
        data_dir: extract data here
    """
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    data_save_path = os.path.join(data_dir, 'data.zip')
    data_download_url = 'https://github.com/kylehounslow/datasets/raw/master/mlbootcamp/sf_housing.zip'
    print('downloading data...')
    urllib.request.urlretrieve(data_download_url, data_save_path)
    print('extracting data to {data_dir}...'.format(data_dir=data_dir))
    data_zip = zipfile.ZipFile(data_save_path)
    data_zip.extractall(data_dir)
    data_zip.close()
    print('Done.')

def load_data_to_dataframe(data_dir: str) -> pd.DataFrame:
    """
    Load all .csv files from data_dir and concatenate them into a single DataFrame.  
    Args:
        data_dir: path to data directory
    Returns:
        pd.DataFrame: all data from files in data_dir
    Notes:
        All duplicate rows will be discarded
    """
    all_csvs = []
    # load the csv files from all scraping runs
    csv_filenames = os.path.join(data_dir, '**/*.csv')
    print('loading data {csv_filenames}'.format(csv_filenames=csv_filenames))
    for filename in glob.glob(csv_filenames):
        all_csvs.append(pd.read_csv(filename))
    # combine all dataframes together and drop any duplicate entries
    df = pd.concat(all_csvs, ignore_index=True).drop_duplicates()
    print("Found a total of {count} data points".format(count=len(df)))
    # save this combined dataframe as csv for safe keeping
    df.to_csv(os.path.join(data_dir, 'all_data.csv'), index=False)
    return df

def format_price(price: str):
    """
    Remove all non-numerical values from price column
    Args:
        price: string representation of price
    Returns:
        price_num: floating point representation of price
    """
    price = str(price)
    multiply_factor = 1
    if 'M' in price:
        multiply_factor = 1e6
    elif 'K' in price:
        multiply_factor = 1e3
    non_decimal = re.compile(r'[^0-9\.]')
    price_num = None
    try:
        price_num = float(non_decimal.sub('', price))*multiply_factor
    except Exception as e:
#         print(f'error converting \"{price}\": {e}')
        pass
    finally:
        return price_num
def load_sf_housing_dataset():
    """
    Download, extract, and format the housing dataset.
    Returns:
        pd.DataFrame: formatted dataset
    """
    data_dir = './tmp'
    download_extract_data(data_dir=data_dir)
    df = load_data_to_dataframe(data_dir=data_dir)
    df['price'] = df.price.apply(format_price)
    df['bed'] = df['facts and features'].apply(parse_beds)
    df['bath'] = df['facts and features'].apply(parse_bath)
    df['sqft'] = df['facts and features'].apply(parse_sqft)
    df['property_type'] = df['title'].apply(parse_property_type)
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
    return df
    