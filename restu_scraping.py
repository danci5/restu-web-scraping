#!/usr/bin/env python

import logging
import re
import pandas as pd
import os
import json
from grab import Grab

logging.basicConfig(level=logging.DEBUG)
RESTU = 'https://www.restu.cz'
PRAGUE_PAGES = 187
g = Grab()
g.go(RESTU)

def get_names():
    try:
        names = g.doc.select("//*/@data-restaurant")
    except Exception as e:
        print(type(e))
        print(e)
    return names.node_list()
    
def get_refs():
    try:
        refs = g.doc.select("//*[@data-restaurant]/*[@data-name]/@href")
    except Exception as e:
        print(type(e))
        print(e)
    return refs.node_list()

def get_ratings():
    try:
        ratings = g.doc.select("//*[@data-restaurant]//meta[@itemprop='ratingValue']/@content")
    except Exception as e:
        print(type(e))
        print(e)
    return ratings.node_list()

def get_number_of_ratings():
    try:
        number_of_ratings = g.doc.select("//*[@data-restaurant]//meta[@itemprop='ratingCount']/@content")
    except Exception as e:
        print(type(e))
        print(e)
    return number_of_ratings.node_list()

def get_addresses():
    try:
        addresses = g.doc.select("//*[@data-restaurant]//address")
    except Exception as e:
        print(type(e))
        print(e)
    addresses = [node.text_content() for node in addresses.node_list()]
    return addresses

def fill_lat_long(refs, lats, lngs):
    pass

def create_dataset(names, ratings, number_of_ratings, addresses, lats, lngs, urls):
    final_dict = {}
    final_dict['restaurant_name'] = names
    final_dict['url'] = urls
    final_dict['rating'] = ratings
    final_dict['number_of_ratings'] = number_of_ratings
    final_dict['full_address'] = addresses
    # final_dict['lat'] = lats
    # final_dict['lng'] = lngs
    df = pd.DataFrame(data=final_dict)
    return df

def export_dataset(dataframe):
    """Exports dataframe to csv and json file."""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    csv_file = dataframe.to_csv(os.path.join(dir_path, 'restu_prague.csv'), encoding='utf-8')
    out = dataframe.to_json(orient='records')
    with open(os.path.join(dir_path, 'restu_prague.json'), 'w') as json_file:
        json_file.write(out)

def main():    
    g.go('praha/')

    names, refs, ratings, number_of_ratings = [], [], [], []
    lats, lngs, addresses = [], [], []

    for page_number in range(1,PRAGUE_PAGES):
        g.go("?page={}".format(page_number))

        names.extend(get_names())
        refs.extend(get_refs())
        ratings.extend(get_ratings())
        number_of_ratings.extend(get_number_of_ratings())
        addresses.extend(get_addresses())

    # fill_lat_long(refs)
    urls = [RESTU + ref for ref in refs]

    dataframe = create_dataset(names, ratings, number_of_ratings, addresses, lats, lngs, urls)
    dataframe.index.name = 'id'
    dataframe = dataframe[['restaurant_name', 'rating', 'number_of_ratings', 'full_address', 'url']]
    export_dataset(dataframe)

if __name__ == "__main__":
    main()