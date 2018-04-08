import pandas as pd
import pytest
from googlemaps.exceptions import HTTPError, TransportError
from os.path import dirname, abspath, join

import find_store
from find_store import settings


@pytest.fixture(scope="module")
def findstore():
    fs = find_store.FindStore(settings.GOOGLE_API_KEY)
    directory = dirname(dirname(abspath(__file__)))
    data_file = join(directory, 'src/find_store/store-locations.csv')
    fs.load_data_file(data_file)
    return fs


@pytest.fixture()
def no_requests(monkeypatch):
    monkeypatch.delattr("requests.sessions.Session.request")


@pytest.fixture()
def df():
    labels = ['Store Name', 'Store Location', 'Address', 'City',
              'State', 'Zip Code', 'Latitude', 'Longitude', 'County']
    stores = [['store1', 'store1 location',
              'store1 address', 'city', 'CA', '94118',
               37.7820964, -122.4464697, 'county'],
              ['store2', 'store2 location',
              'store2 address', 'city', 'CA', '94118',
               37.7820964, -122.4464697, 'county']]
    return pd.DataFrame.from_records(stores, columns=labels)


def test_no_api_key():
    with pytest.raises(ValueError):
        fs = find_store.FindStore()
        fs.find_nearest_store("94086", miles=True, text_output=True)


def test_invalid_api_key():
    with pytest.raises(ValueError):
        fs = find_store.FindStore('abc')
        fs.find_nearest_store("94086", miles=True, text_output=True)


def test_no_store_data():
    fs = find_store.FindStore(settings.GOOGLE_API_KEY)
    with pytest.raises(ValueError):
        fs.find_nearest_store("94086", miles=True, text_output=True)


def test_valid_location(findstore):
    findstore.find_nearest_store("94086", miles=True, text_output=True)


def test_no_location(findstore):
    with pytest.raises(HTTPError):
        findstore.find_nearest_store(None, miles=True, text_output=True)


def test_invalid_location(findstore):
    with pytest.raises(ValueError):
        findstore.find_nearest_store("*****", miles=True, text_output=True)


def test_invalid_miles_param(findstore):
    with pytest.raises(ValueError):
        findstore.find_nearest_store("94086", "mi", text_output=True)


def test_invalid_output_param(findstore):
    with pytest.raises(ValueError):
        findstore.find_nearest_store("94086", "mi", text_output=True)


def test_text_output(findstore):
    actual_output = findstore.find_nearest_store("94086", miles=True, text_output=True)
    expected_output = """Store Name                                                    Sunnyvale
Store Location                      SEC S Mathilda Ave & W McKinley Ave
Address                                              298 W McKinley Ave
City                                                          Sunnyvale
State                                                                CA
Zip Code                                                     94086-6193
Latitude                                                     37.3737701
Longitude                                                   -122.032323
County                                               Santa Clara County
Distance                                             0.6230898576088666

"""
    assert actual_output == expected_output


def test_json_output(findstore):
    actual_output = findstore.find_nearest_store("94086", miles=True, text_output=False)
    expected_output = """[
  {
    "Address": "298 W McKinley Ave",
    "City": "Sunnyvale",
    "County": "Santa Clara County",
    "Distance": 0.6230898576088666,
    "Latitude": 37.3737701,
    "Longitude": -122.032323,
    "State": "CA",
    "Store Location": "SEC S Mathilda Ave & W McKinley Ave",
    "Store Name": "Sunnyvale",
    "Zip Code": "94086-6193"
  }
]"""
    assert actual_output == expected_output


def test_connection_error(findstore, no_requests):
    with pytest.raises(TransportError):
        findstore.find_nearest_store("94086", miles=True, text_output=False)


def test_multiple_nearest_stores(monkeypatch, df):
    def mockloadfile(data_file):
        return
    fs = find_store.FindStore(settings.GOOGLE_API_KEY)
    monkeypatch.setattr(fs, 'load_data_file', mockloadfile)
    fs.load_data_file("test.csv")
    monkeypatch.setattr(fs, '_df', df)
    actual_output = fs.find_nearest_store("94086", miles=True, text_output=False)
    expected_output = """[
  {
    "Address": "store1 address",
    "City": "city",
    "County": "county",
    "Distance": 36.68501517148529,
    "Latitude": 37.7820964,
    "Longitude": -122.4464697,
    "State": "CA",
    "Store Location": "store1 location",
    "Store Name": "store1",
    "Zip Code": "94118"
  },
  {
    "Address": "store2 address",
    "City": "city",
    "County": "county",
    "Distance": 36.68501517148529,
    "Latitude": 37.7820964,
    "Longitude": -122.4464697,
    "State": "CA",
    "Store Location": "store2 location",
    "Store Name": "store2",
    "Zip Code": "94118"
  }
]"""
    assert actual_output == expected_output


def test_csv_no_exist():
    fs = find_store.FindStore(settings.GOOGLE_API_KEY)
    with pytest.raises(FileNotFoundError):
        fs.load_data_file("non_existent_file.csv")
        fs.find_nearest_store("94086", miles=True, text_output=False)
