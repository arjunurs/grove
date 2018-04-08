# Store Locator

This is a command-line application that uses a tabular dataset for a national retail chain to find the nearest  store to a specified address or zip. The dataset is included in the repo (store-locations.csv).


# Command-line

CLI options supported. (Specification conforms to http://docopt.org/)

```
Find Store
  find_store will locate the nearest store (as the vrow flies) from
  store-locations.csv, print the matching store address, as well as
  the distance to that store.

Usage:
  find_store --address="<address>"
  find_store --address="<address>" [--units=(mi|km)] [--output=text|json]
  find_store --zip=<zip>
  find_store --zip=<zip> [--units=(mi|km)] [--output=text|json]

Options:
  --zip=<zip>          Find nearest store to this zip code. If there are multiple best-matches, return the first.
  --address            Find nearest store to this address. If there are multiple best-matches, return the first.
  --units=(mi|km)      Display units in miles or kilometers [default: mi]
  --output=(text|json) Output in human-readable text, or in JSON (e.g. machine-readable) [default: text]

Example
  find_store --address="1770 Union St, San Francisco, CA 94123"
  find_store --zip=94115 --units=km
```

# Approach

The application loads the dataset for the stores into a pandas dataframe and calculates the [haversine distance](https://en.wikipedia.org/wiki/Haversine_formula) to the address or zip specified in the commandline. The dataframe is then queried based on distance to find the nearest store. The distance can be in miles or kilometer based on the option. The output format can also be specified in the CLI option. 

