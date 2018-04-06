#!/usr/bin/env python

"""Find Store
find_store will locate the nearest store (as the vrow flies) from
store-locations.csv, print the matching store address, as well as
the Distance to that store.

Usage:
  find_store --address="<address>"
  find_store --address="<address>" [--units=(mi|km)] [--output=text|json]
  find_store --zip=<zip>
  find_store --zip=<zip> [--units=(mi|km)] [--output=text|json]

Options:
  --zip=<zip>          Find nearest store to this zip code. If there are multiple best-matches, return the first.
  --address=<address>  Find nearest store to this address. If there are multiple best-matches, return the first.
  --units=(mi|km)      Display units in miles or kilometers [default: mi]
  --output=(text|json) Output in human-readable text, or in JSON (e.g. machine-readable) [default: text]

Example
  find_store --address="1770 Union St, San Francisco, CA 94123"
  find_store --zip=94115 --units=km

"""
import os
import sys

from docopt import docopt
import googlemaps
import pandas as pd
import numpy as np
import json
import settings


class FindStore:
    def __init__(self, api_key=None):
        self.gmaps = self._create_gmaps_client(api_key)
        self.df = None

    def _create_gmaps_client(self, api_key):
        return googlemaps.Client(api_key)

    def load_data_file(self, data_file):
        self.df = pd.read_csv(data_file, encoding='cp1252')
        return

    # https://github.com/mapado/haversine/blob/master/haversine/__init__.py
    @staticmethod
    def _haversine(lat1, lon1, lat2, lon2, miles=True):
        miles_constant = 3959
        lat1, lon1, lat2, lon2 = map(np.deg2rad, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
        c = 2 * np.arcsin(np.sqrt(a))
        mi = miles_constant * c

        if not miles:
            return 1.6 * mi

        return mi

    def find_nearest_store(self, location, miles=True, text_output=True):
        geocode_result = self.gmaps.geocode(location)

        origin_lat = geocode_result[0]["geometry"]["location"]["lat"]
        origin_lng = geocode_result[0]["geometry"]["location"]["lng"]

        if self.df is not None:
            self._update_distance(origin_lat, origin_lng,
                                  self.df['Latitude'].values, self.df['Longitude'].values,
                                  miles)
        else:
            raise ValueError("Store locations not loaded")

        nearest_stores = self.df[self.df["Distance"] == self.df["Distance"].min()].dropna()

        nearest_stores_lst = []
        for _, row in nearest_stores.iterrows():
            nearest_stores_lst.append(row.to_dict())

        if text_output:
            self._output_text(nearest_stores_lst)
        else:
            self._output_json(nearest_stores_lst)
        return

    def _update_distance(self, lat1, lon1, lat2, lon2, miles):
        self.df["Distance"] = self._haversine(lat1, lon1, lat2, lon2, miles)
        return

    def _output_json(self, nearest_stores_lst):
        print(json.dumps(nearest_stores_lst, sort_keys=True, indent=2))
        return

    def _output_text(self, nearest_stores_lst):
        for store in nearest_stores_lst:
            for key, value in store.items():
                print(f"{key:<30} {value:>40}")
            print()
        return


def main():
    arguments = docopt(__doc__, version='Find Store 1.0')

    if arguments["--address"] is not None:
        location = arguments["--address"]
    elif arguments["--zip"] is not None:
        location = arguments["--zip"]

    if arguments["--units"] not in ["km", "mi"]:
        sys.exit("Incorrect units specified")

    if arguments["--output"] is not None and \
            arguments["--output"] not in [None, "text", "json"]:
        sys.exit("Incorrect output specified")

    if arguments["--units"] == "km":
        miles = False
    else:
        miles = True

    if arguments["--output"] == "json":
        text_output = False
    else:
        text_output = True

    fs = FindStore(settings.GOOGLE_API_KEY)
    data_file = os.path.join(os.path.dirname(__file__), 'store-locations.csv')
    fs.load_data_file(data_file)

    fs.find_nearest_store(location, miles, text_output)


if __name__ == '__main__':
    main()
