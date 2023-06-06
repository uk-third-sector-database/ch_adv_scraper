import os
import csv
import json
import time
import requests
import numpy as np
from tqdm import tqdm
from requests.auth import HTTPBasicAuth


def load_token(path):
    try:
        with open(path, 'r') as file:
            return str(file.readline()).strip()
    except FileNotFoundError:
        print('API Token was not found')


def parse_query(query_json, filepath):
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
    size = 5000
    urlquery = CH_url
    hits = np.inf
    for year in tqdm(range(1900, 2024)):
        for month in ['01', '02', '03', '04', '05', '06',
                      '07', '08', '09', '10', '11', '12']:
            if (month == '01') or (month == '03') or \
               (month == '05') or (month == '07') or \
               (month == '08') or (month == '10'):
                day = '31'
            elif (month == '04') or (month == '06') or \
                 (month == '09') or (month == '11'):
                day = '30'
            else:
                if year % 4 == 0:
                    day = '28'
                else:
                    day = '28'
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
                    query = requests.get(urlquery,
                                         auth=HTTPBasicAuth(APIKey, ''),
                                         params=pars)
                    if query.status_code == 200:
                        query_json = json.loads(query.text)
                        hits = query_json['hits']
                        parse_query(query_json, filepath)
                        if (int(query.headers['X-Ratelimit-Remain']) == 0) or \
                                (query.status_code == 429):
                            print('Rate limit hit! Calls remaining: ', int(query.headers['X-Ratelimit-Remain']))
                            time.sleep(300)
                    elif (query.status_code == 404) or\
                            (query.status_code == 500):
                        finished_query = True
                    else:
                        time.sleep(10)
                        print('Huh? bad return, but shouldnt be :',
                              query.status_code)
                    pages += 1
                else:
                    finished_query = True

def check_file(filepath):
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
    api_key_path = os.path.join(os.getcwd(), '..', 'tokens', 'ch_apikey')
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
    CH_url = 'https://api.company-information.service.gov.uk/advanced-search/companies'
    for CompanyType in typelist:
        print('Working on: ', CompanyType)
        get_data(CompanyType, filepath)
