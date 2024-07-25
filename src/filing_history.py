"""
This script scrapes the Companies House API for filing history
for an input (from file) list of company numbers, searching
for changes in address.

"""


import requests
import json
from requests.auth import HTTPBasicAuth
from main import load_token
import os,csv,time
from tqdm import tqdm

def fetch_filing_history(api_key, company_number):
    url = f"https://api.company-information.service.gov.uk/company/{company_number}/filing-history"
    retry_count = 0
    max_retries = 10
    
    while retry_count < max_retries:
        try:

            response = requests.get(url, auth=HTTPBasicAuth(api_key, ''))
            response.raise_for_status()
            if response.status_code == 200:
                return response.json()
            
            elif response.status_code == 429:
                print("Rate limit exceeded. Waiting before retrying...")

                retry_after = response.headers.get('Retry-After')
                if retry_after:
                    wait_time = int(retry_after)
                else:
                    wait_time = 60  
                print(f"Waiting for {wait_time} seconds before retrying.")
                time.sleep(wait_time)
                retry_count += 1
            
        except requests.exceptions.HTTPError as http_err:
            if response.status_code != 429:
                print(f"HTTP error occurred: {http_err}")
                break  
            
        except Exception as err:
            if 'response' in locals() and response.status_code != 429:
                print(f"Other error occurred: {err}")
                break  


    raise Exception("Max retries exceeded")


def find_address_changes(filing_history):
    address_changes = []
    for item in filing_history.get('items', []):
        if 'change-registered-office-address' in item.get('description', '').lower():
            change_date = item['description_values'].get('change_date', 'N/A')
            old_address = item['description_values'].get('old_address', 'N/A')
            new_address = item['description_values'].get('new_address', 'N/A')
            address_changes.append({
                'change_date': change_date,
                'old_address': old_address,
                'new_address': new_address
            })
    return address_changes


def main(api_key, all_company_numbers):
    ofile_rows = []

    for company_number in tqdm(all_company_numbers, desc=f'processing {len(all_company_numbers)} companies'):
        try:
            filing_history = fetch_filing_history(api_key, company_number)
        except Exception as e:
            print(f'Exception for companyid {company_number}: {e}')

        if filing_history:
            address_changes = find_address_changes(filing_history)
            for change in address_changes:
                change['companyid'] = company_number
                ofile_rows.append(change)

    return ofile_rows

if __name__=='__main__':
    api_key_path = os.path.join(os.getcwd(),
                            'tokens',
                            'ch_apikey')
    APIKey = load_token(api_key_path)
    
    company_numbers = []
    infile='../tso-analysis/CICs_with_address_change.csv'
    with open(infile, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            company_numbers.append(row[0])

    print(f'{len(company_numbers)} loaded from {infile}')
    o = main(APIKey, company_numbers)

    ofile = 'ch_adv_scrape_filing.csv'
    with open(ofile, mode='w', newline='') as file:
        writer = csv.DictWriter(file,fieldnames=['companyid','change_date','old_address','new_address'])
        writer.writeheader()
        for item in o:
            writer.writerow(item)

    print(f'{len(o)} rows written to {ofile}')