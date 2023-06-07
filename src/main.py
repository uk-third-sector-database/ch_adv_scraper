"""
This is a short script which scrapes the Companies House
Advanced Search API for all 'third sector' organisations.
It can very easily be re-purposed to scrape other types
of companies!

Author: github.com\crahal
Last Update: 07/06/2023

"""
import os
import csv
import json
import time
import requests
import numpy as np
from tqdm import tqdm
from requests.auth import HTTPBasicAuth


def load_token(path):
    """
    Simple function to load a hidden API token from
    disk: It should live in the `tokens` sub-directory
    :param path:    A filepath to a text file which contains
                    an API on the first line of the file only.
    :return:        The API key read in from the file
    """
    try:
        with open(path, 'r') as file:
            return str(file.readline()).strip()
    except FileNotFoundError:
        print('API Token was not found')


def parse_query(query_json, filepath):
    """
    A simple function to parse a json returned from the API.
    It iterates over three levels of the object; the outter,
    meta-layers (etag and hits), the elements of the items
    which contain general company meta data, and then the nested
    elements of the address. If any field is not present, fill
    with ''.
    :param query_json: A query returned from the API in json format
    :param filepath: A path to the file which is being output
    :return: None
    """
    with open(filepath, 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        for elem in query_json['items']:#
            results = []
            address = elem['registered_office_address']
            for field in [
                "etag",
                "hits"
                ]:
                try:
                    results.append(query_json[field])
                except KeyError:
                    results.append('')
            for field in [
                "company_name",
                "company_number",
                "company_status",
                "company_subtype",
                "company_type",
                "date_of_cessation",
                "date_of_creation",
                "sic_codes",
                "kind"
            ]:
                try:
                    results.append(elem[field])
                except KeyError:
                    results.append('')
            for field in [
                "address_line_1",
                "address_line_2",
                "country",
                "locality",
                "postal_code",
                "region"
            ]:
                try:
                    results.append(address[field])
                except KeyError:
                    results.append('')
            writer.writerow(results)

def get_data(CompanyType, filepath):
    """
    The main scraper which iterates over months and years
    beginning from 1850 to the present day for a specific
    CompanyType. This is necessary because the API only
    allows the return of up to 10,000 entries per query.
    (e.g. query['hits']<10000).

    Note: CICs are a _subtype_, as opposed to a CompanyType,
    and this is handled appropriately with control over the
    params dictionary which gets passed to the GET request.
    :param CompanyType: The type of company (inc CIC)
    :param filepath: The filepath which gets passed to the parser
    :return: None
    """
    size = 5000
    hits = np.inf
    for year in tqdm(range(1750, 2024)):
        for month, day in zip(['01', '02', '03', '04', '05', '06',
                               '07', '08', '09', '10', '11', '12'],
                              ['31', '28', '31', '30', '31', '30',
                               '31', '31', '30', '31', '30', '31']):
            finished_query = False
            pages = 1
            while finished_query is False:
                if CompanyType != 'community-interest-company':
                    pars = {'start_index': str((pages - 1) * size),
                            'size': str(size),
                            'company_type': CompanyType,
                            'incorporated_from': str(year) + '-' + month + '-01',
                            'incorporated_to': str(year) + '-' + month + '-' + day
                    }
                else:
                    pars = {'start_index': str((pages - 1) * size),
                            'size': str(size),
                            'company_subtype': CompanyType,
                            'incorporated_from': str(year) + '-' + month + '-01',
                            'incorporated_to': str(year) + '-' + month + '-' + day
                    }
                if hits > ((pages - 1) * size):
                    query = requests.get(CH_url,
                                         auth=HTTPBasicAuth(APIKey, ''),
                                         params=pars)
                    if query.status_code == 200:
                        query_json = json.loads(query.text)
                        hits = query_json['hits']
                        parse_query(query_json, filepath)
                    elif (query.status_code == 404) or\
                            (query.status_code == 500):
                        finished_query = True
                    elif (int(query.headers['X-Ratelimit-Remain']) == 0) or \
                         (query.status_code == 429):
                        time.sleep(300)
                    else:
                        print("A wild status code appeared:", query.status_code)
                    pages += 1
                else:
                    finished_query = True


def check_file(filepath):
    """
    Check whether an output file exists already, and if it does,
    delete it. This could become a command line argument? It could
    also optionally create the subdirectory where this lives if
    this does not exist!
    :param filepath: Location of outut of scrape
    :return: None
    """
    if os.path.exists(filepath):
        os.remove(filepath)
    header = [
        "etag",
        "hits",
        "company_name",
        "company_number",
        "company_status",
        "company_subtype",
        "company_type",
        "date_of_cessation",
        "date_of_creation",
        "sic_codes",
        "kind",
        "address_line_1",
        "address_line_2",
        "country",
        "locality",
        "postal_code",
        "region"
    ]
    with open(filepath, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)


if __name__ == '__main__':
    name = 'ch_adv_scrape.csv'
    path = os.path.join(os.getcwd(), '..', 'data')
    filepath = os.path.join(path, name)
    check_file(filepath)
    api_key_path = os.path.join(os.getcwd(),
                                '..',
                                'tokens',
                                'ch_apikey')
    APIKey = load_token(api_key_path)
    typelist = [
        'private-limited-guarant-nsc',
        'private-limited-guarant-nsc-limited-exemption',
        'charitable-incorporated-organisation',
        'registered-society-non-jurisdictional',
        'scottish-charitable-incorporated-organisation',
        'industrial-and-provident-society',
        'community-interest-company'
    ]
    CH_api = 'https://api.company-information.service.gov.uk/'
    api_type = 'advanced-search'
    CH_url = CH_api + api_type + '/companies'
    for CompanyType in typelist:
        print('Working on: ', CompanyType)
        get_data(CompanyType, filepath)

    #@TODO We could optionally de-duplicate or compress this here.
