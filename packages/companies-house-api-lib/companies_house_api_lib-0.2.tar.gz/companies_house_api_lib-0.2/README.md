# Companies House API Library

A Python client for interacting with the Companies House API.

[![PyPI version](https://badge.fury.io/py/companies-house-api-lib.svg)](https://badge.fury.io/py/companies-house-api-lib)

## Installation

This library is available on PyPI and can be installed with pip:

```bash
pip install companies-house-api-lib
```

## Usage

To use the client, you need to have a Companies House API key. You can get one from the [Companies House developer portal](https://developer.company-information.service.gov.uk/).

Once you have your key, you can either pass it to the client directly or set it as an environment variable named `COMPANIES_HOUSE_API_KEY`.

```python
from companieshouse import CompaniesHouseClient

# Option 1: Pass the key directly
client = CompaniesHouseClient(api_key="YOUR_API_KEY")

# Option 2: Use an environment variable
# export COMPANIES_HOUSE_API_KEY="YOUR_API_KEY"
client = CompaniesHouseClient()

# Search for companies
search_results = client.search_companies("python")
print(search_results)

# Get a company profile
if search_results.get("items"):
    company_number = search_results["items"][0]["company_number"]
    company_profile = client.get_company_profile(company_number)
    print(company_profile)
```

## Testing

A test file (`test_library.py`) is included in this repository. To run the tests, you will need to have your Companies House API key set as an environment variable.

```bash
export COMPANIES_HOUSE_API_KEY="YOUR_API_KEY"
python test_library.py
```

## Available API Calls

Here is a list of the available API calls in this library:

*   `search_all(query)`: Searches for all records in the Companies House API.
*   `search_companies(query)`: Searches for companies.
*   `get_company_profile(company_number)`: Gets the profile of a company.
*   `get_company_officers(company_number)`: Gets the company officers.
*   `get_company_filing_history(filing_history_url)`: Gets the company filing history.
*   `get_company_registered_office_address(company_number)`: Gets the company office address.
*   `get_company_registers(company_number)`: Gets the company registers details.
*   `get_company_charges(company_number)`: Gets the company charges details.
*   `get_company_insolvency(company_number)`: Gets the company insolvancy details.
*   `get_company_exemptions(company_number)`: Gets the company exemptions details.
*   `get_corporate_officer_disqualifications(officer_id)`: Gets the corporate officer disqualifications.
*   `get_natural_officer_disqualifications(officer_id)`: Gets the natural officer disqualifications.
*   `get_office_appointments(officer_id)`: Gets the officer appointments.
*   `get_company_uk_establishments(company_number)`: Gets the company insolvancy details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.