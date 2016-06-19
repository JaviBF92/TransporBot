#!/usr/bin/python

from bs4 import BeautifulSoup
from tidylib import tidy_document # http://countergram.com/open-source/pytidylib/docs/index.html
import requests

def get_stations():
    web = requests.get('http://horarios.renfe.com/cer/hjcer300.jsp?NUCLEO=30&CP=NO&I=s#').text
    document, errors = tidy_document(web)
    bs = BeautifulSoup(document, 'html.parser')
    estaciones = bs.find('select', {"name":"o"}).findAll('option')
    estaciones_ids = [(option.text.strip().replace(" ", "").lower(), option['value']) for option in estaciones][1:]
    return {key: value for (key, value) in estaciones_ids}

if __name__ == "__main__":
	print get_stations()
