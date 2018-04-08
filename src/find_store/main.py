# -*- coding: utf-8 -*-
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

from find_store import settings
from find_store import FindStore


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

    print(fs.find_nearest_store(location, miles, text_output))

    return 0


if __name__ == '__main__':
    status = main()
    sys.exit(status)

