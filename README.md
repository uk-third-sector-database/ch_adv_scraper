### Companies House Advanced Search API Scraper
------
![coverage](https://img.shields.io/badge/Purpose-Research-yellow)
[![Generic badge](https://img.shields.io/badge/Python-3.x-red.svg)](https://shields.io/)
[![Generic badge](https://img.shields.io/badge/License-GNU3.0-purple.svg)](https://shields.io/)
[![Generic badge](https://img.shields.io/badge/Maintained-Yes-brightgreen.svg)](https://shields.io/)
[![Generic badge](https://img.shields.io/badge/BuildPassing-Yes-orange.svg)](https://shields.io/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14951542.svg)](https://doi.org/10.5281/zenodo.14951542)


A scraper for the Companies House [Advanced Search API](https://developer-specs.company-information.service.gov.uk/companies-house-public-data-api/reference/search/advanced-company-search), with the specific intention of collecting data on Third Sector Organisations. The open data on this website is sourced from Public Records made available by [Companies House](https://www.gov.uk/government/organisations/companies-house) and licensed under the [Open Government License](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

It should run without any special installations or requirements; tqdm and np are mostly luxuries which improve the quality of life. To install them, a simple `pip install -r requirements.txt` should do the trick. There are various things that can be done to improve the scraper, including but not limited to:

* Logging
* Better error handling of unknown status codes.
* De-duplicate and compress upon completion of the script.
* Dynamically scale up and down the window of the scrape, based on whether the previous period was close to the 10k threshold.

### License
This work is free. You can redistribute it and/or modify it under the terms of the GNU GPL 3.0 license.

### Acknowledgements
We are grateful for funding from the ESRC (project reference: ES/X000524/1).
