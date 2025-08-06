import requests
import os

class CompaniesHouseClient:
    """
    A client for interacting with the Companies House API.
    """
    def __init__(self, api_key=None):
        """
        Initializes the Companies House client.

        Args:
            api_key: Your Companies House API key. If not provided, it will
                     look for the COMPANIES_HOUSE_API_KEY environment variable.
        """
        self.api_key = api_key or os.environ.get("COMPANIES_HOUSE_API_KEY")
        if not self.api_key:
            raise ValueError("API key not provided. Please provide it as an argument or set the COMPANIES_HOUSE_API_KEY environment variable.")
        self.base_url = "https://api.company-information.service.gov.uk"

    def _make_request(self, endpoint, params=None):
        """
        Makes a request to the Companies House API.

        Args:
            endpoint: The API endpoint to call.
            params: A dictionary of query parameters.

        Returns:
            A dictionary containing the JSON response from the API.
        """
        url = f"{self.base_url}/{endpoint}"
        auth = (self.api_key, "")
        response = requests.get(url, params=params, auth=auth)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()

    def search_all(self, query):
        """
        Searches for all records in the Companies House API..

        Args:
            query: The search query.

        Returns:
            A dictionary containing the search results.
        """
        return self._make_request("search", params={"q": query})

    def search_companies(self, query):
        """
        Searches for companies.

        Args:
            query: The search query.

        Returns:
            A dictionary containing the search results.
        """
        return self._make_request("search/companies", params={"q": query})

    def get_company_profile(self, company_number):
        """
        Gets the profile of a company.

        Args:
            company_number: The company number.

        Returns:
            A dictionary containing the company profile.
        """
        return self._make_request(f"company/{company_number}")
    
    def get_company_officers(self, company_number):
        """
        Gets the company officers.

        Args:
            company_number: The company number.

        Returns:
            A dictionary containing the company officers.
        """

        return self._make_request(f"company/{company_number}/officers")
    
    def get_company_filing_history(self, filing_history_url):
        """
        Gets the company filing history.

        Args:
            filing_history_url: A final part of the filings url from the company profile record.

        Returns:
            A dictionary containing the filing history.
        """
        return self._make_request(f"{filing_history_url}")
    
    def get_company_registered_office_address(self, company_number):
        """
        Gets the company office address.

        Args:
            company_number: The company number.

        Returns:
            A dictionary containing the company address.
        """
        return self._make_request(f"company/{company_number}/registered-office-address")
    
    def get_company_registers(self, company_number):
        """
        Gets the company registers details.

        Args:
            company_number: The company number.

        Returns:
            A dictionary containing the company registers.
        """
        return self._make_request(f"company/{company_number}/registers")
    
    def get_company_charges(self, company_number):
        """
        Gets the company charges details.

        Args:
            company_number: The company number.

        Returns:
            A dictionary containing the company charges.
        """
        return self._make_request(f"company/{company_number}/charges")
    
    def get_company_insolvency(self, company_number):
        """
        Gets the company insolvancy details.

        Args:
            company_number: The company number.

        Returns:
            A dictionary containing the company insolvancies.
        """
        return self._make_request(f"company/{company_number}/insolvency")
    
    def get_company_exemptions(self, company_number):
        """
        Gets the company exemptions details.

        Args:
            company_number: The company number.

        Returns:
            A dictionary containing the company exemptions.
        """
        return self._make_request(f"company/{company_number}/exemptions")
    
    def get_corporate_officer_disqualifications(self, officer_id):
        """
        Gets the corporate officer disqualifications.

        Args:
            officer_id: The officer
        Returns:
            A dictionary containing the company corporate officer disqualifications.
        """
        return self._make_request(f"disqualified-officers/corporate/{officer_id}")
    
    def get_natural_officer_disqualifications(self, officer_id):
        """
        Gets the natural officer disqualifications.

        Args:
            officer_id: The officer id
        Returns:
            A dictionary containing the company natural officer disqualifications.
        """
        return self._make_request(f"disqualified-officers/natural/{officer_id}")
    
    def get_office_appointments(self, officer_id):
        """
        Gets the officer appointments.

        Args:
            officer_id: The officer id
        Returns:
            A dictionary containing the office appointments.
        """
        return self._make_request(f"officers/{officer_id}/appointments")
    
    def get_company_uk_establishments(self, company_number):
        """
        Gets the company insolvancy details.

        Args:
            company_number: The company number.

        Returns:
            A dictionary containing the company insolvancies.
        """
        return self._make_request(f"company/{company_number}/uk-establishments")


# if __name__ == '__main__':
#     # Example usage:
#     # Make sure to set the COMPANIES_HOUSE_API_KEY environment variable
#     # export COMPANIES_HOUSE_API_KEY="YOUR_API_KEY"


    
#     # r = requests.get('https://api.company-information.service.gov.uk/company/00002065', auth=(keyEncoded, ''))
#     # print(r.text)
#     # print("hello")

#     client = CompaniesHouseClient()

#     # Search for companies
#     search_results = client.search_companies("python")
#     print(search_results)
#     print("Search results:")
#     for item in search_results.get("items", []):
#         print(f"- {item.get('title')}")

#     # Get a company profile (replace with a valid company number)
#     if search_results.get("items"):
#         company_number = search_results["items"][0]["company_number"]
#         company_profile = client.get_company_profile(company_number)
#         print("COMPANY PROFILE")
#         print(company_profile)
#         company_officers =  client.get_company_officers(company_number)
#         print("COMPANY OFFICERS")
#         print(company_officers)
#         print(f"\nCompany profile for {company_profile.get('company_name')}:")
#         print(f"  Company number: {company_profile.get('company_number')}")
#         print(f"  Status: {company_profile.get('company_status')}")
#         print(f"  Creation date: {company_profile.get('date_of_creation')}")
#         company_filing_history = client.get_company_filing_history(company_profile['links'].get('filing_history'))
#         print(company_filing_history)
