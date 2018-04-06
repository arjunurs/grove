import pytest
import find_store
import settings


@pytest.fixture(scope="module")
def findstore():
    return find_store.FindStore(settings.GOOGLE_API_KEY)


def test_no_api_key():
    with pytest.raises(ValueError):
        fs = find_store.FindStore()
        fs.find_nearest_store("94086", miles=True, text_output=True)


def test_invalid_api_key():
    with pytest.raises(ValueError):
        fs = find_store.FindStore('abc')
        fs.find_nearest_store("94086", miles=True, text_output=True)


def test_no_store_data(findstore):
    with pytest.raises(ValueError):
        findstore.find_nearest_store("94086", miles=True, text_output=True)
