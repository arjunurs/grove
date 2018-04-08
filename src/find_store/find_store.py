# -*- coding: utf-8 -*-

import json

import googlemaps
import numpy as np
import pandas as pd


class FindStore:
    def __init__(self, api_key=None):
        self._gmaps = self._create_gmaps_client(api_key)
        self._df = None

    def _create_gmaps_client(self, api_key):
        return googlemaps.Client(api_key)

    def load_data_file(self, data_file):
        self._df = pd.read_csv(data_file, encoding='cp1252')
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
        if not (isinstance(miles, bool) and isinstance(text_output, bool)):
            raise ValueError("miles and text_output are boolean parameters")

        geocode_result = self._gmaps.geocode(location)

        if geocode_result:
            origin_lat = geocode_result[0]["geometry"]["location"]["lat"]
            origin_lng = geocode_result[0]["geometry"]["location"]["lng"]
        else:
            raise ValueError("Invalid location")

        if self._df is not None:
            self._update_distance(origin_lat, origin_lng,
                                  self._df['Latitude'].values, self._df['Longitude'].values,
                                  miles)
        else:
            raise ValueError("Store locations not loaded")

        nearest_stores = self._df[self._df["Distance"] == self._df["Distance"].min()].dropna()

        nearest_stores_lst = []
        for _, row in nearest_stores.iterrows():
            nearest_stores_lst.append(row.to_dict())

        if text_output:
            return self._output_text(nearest_stores_lst)
        else:
            return self._output_json(nearest_stores_lst)

    def _update_distance(self, lat1, lon1, lat2, lon2, miles):
        self._df["Distance"] = self._haversine(lat1, lon1, lat2, lon2, miles)
        return

    def _output_json(self, nearest_stores_lst):
        t = json.dumps(nearest_stores_lst, sort_keys=True, indent=2)
        return t

    def _output_text(self, nearest_stores_lst):
        output = []
        for store in nearest_stores_lst:
            for key, value in store.items():
                output.append(f"{key:<30} {value:>40}")
            output.append("\n")
        return "\n".join(output)
