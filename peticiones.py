#!/usr/bin/env
#coding=utf-8
from bs4 import BeautifulSoup
from tidylib import tidy_document # http://countergram.com/open-source/pytidylib/docs/index.html
import requests


def get_stations():
        try:
            web = requests.get('http://horarios.renfe.com/cer/hjcer300.jsp?NUCLEO=30&CP=NO&I=s#', timeout=4).text
        except Timeout:
            return None
        else:
            document, errors = tidy_document(web)
            bs = BeautifulSoup(document, 'html.parser')
            estaciones = bs.find('select', {"name":"o"}).findAll('option')
            estaciones_ids = [(option.text.strip().replace(" ", "").lower(), option['value']) for option in estaciones][1:]
            return {key: value for (key, value) in estaciones_ids}

def get_html(org, dst, date):
    try:
        r = requests.post('http://horarios.renfe.com/cer/hjcer310.jsp',
    	                    data = {'nucleo':'30', 'i':'s', 'cp':'NO',
    	                            'o':org, 'd':dst, 'df':date,
    	                            'ho':'00', 'hd':'26', 'TXTInfo':''}, timeout=4).text
    except Timeout:
        return None
    else:
        document, errors = tidy_document(r)
    	return document

if __name__ == "__main__":
	print get_stations()
