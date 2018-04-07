from googlemaps.exceptions import HTTPError, TransportError
from os.path import dirname, abspath, join
from pytest_mock

import pytest

import find_store
import settings


@pytest.fixture(scope="module")
def findstore():
    fs = find_store.FindStore(settings.GOOGLE_API_KEY)
    directory = dirname(dirname(abspath(__file__)))
    data_file = join(directory, 'src/store-locations.csv')
    fs.load_data_file(data_file)
    return fs


@pytest.fixture()
def no_requests(monkeypatch):
    monkeypatch.delattr("requests.sessions.Session.request")


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

