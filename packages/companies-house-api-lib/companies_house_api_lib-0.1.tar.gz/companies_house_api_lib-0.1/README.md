# Companies House API Library

A Python client for interacting with the Companies House API.

## Installation

```bash
pip install companies-house-api-lib
```

## Usage

```python
from companieshouse import CompaniesHouseClient

# Make sure to set the COMPANIES_HOUSE_API_KEY environment variable
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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
