import requests
from typing import Optional, Union, List

class TrakteerApi:
    
    def __init__(self, api_key: str, base_url="https://api.trakteer.id/v1/public"):
        """
        Initialize Trakteer class.

        Args:
            api_key (str): API key provided by Trakteer.
            base_url (str, optional): Base URL of Trakteer API. Defaults to "https://api.trakteer.id/v1/public".

        Attributes:
            api_key (str): API key provided by Trakteer.
            base_url (str): Base URL of Trakteer API.
            headers (dict): Request headers with API key.
        """
        self.api_key = api_key
        self.timeout = 5
        self.base_url = base_url
        self.headers = {
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "key": self.api_key
        }

    def _req(self, url: str) -> dict:

        """
        Make a GET request to the given URL and return the parsed JSON response.

        Args:
            url (str): URL to make the request to.

        Returns:
            dict: Parsed JSON response.

        Raises:
            ValueError: If the API key is invalid or unauthorized access is attempted.
            Exception: If a connection error or timeout occurs.
        """
        try:
            r = requests.get(url, headers=self.headers, timeout=self.timeout)
            response = r.json()
            if response["message"] == "This action is unauthorized.":
                raise ValueError("Invalid API key or unauthorized access.")
            else:
                return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            raise Exception(e)
            
    def get_current_balance(self):
        """        
        Fetches the current balance of the user.

        Returns:
            dict: Parsed JSON response containing the current balance
        """
        url = f"{self.base_url}/current-balance"
        return self._req(url)

    def get_support_history(
        self,
        limit: Optional[int] = 5,
        page: Optional[int] = 1,
        include: Optional[Union[str, List[str]]] = None,
    ) -> dict:
        """
        Fetches the support history of the user.

        Args:
            limit (Optional[int]): Number of records to return (default: 5)
            page (Optional[int]): Page number for pagination (default: 1)
            include (Optional[Union[str, List[str]]]): Extra fields to include. 
                Available: 'is_guest', 'reply_message', 'net_amount', 'updated_at_diff_label'

        Returns:
            dict: Parsed JSON response
        """
        query_params = [f"limit={limit}", f"page={page}"]

        if include:
            if isinstance(include, list):
                include = ','.join(include)
            query_params.append(f"include={include}")

        query_string = "&".join(query_params)
        url = f"{self.base_url}/supports?{query_string}"

        return self._req(url)

    def get_transaction_history(
        self,
        limit: Optional[int] = 5,
        page: Optional[int] = 1,
        include: Optional[Union[str, List[str]]] = None,
    ) -> dict:
        """
        Fetches the transaction history of the user.

        Args:
            limit (Optional[int]): Number of records to return (default: 5)
            page (Optional[int]): Page number for pagination (default: 1)
            include (Optional[Union[str, List[str]]]): Extra fields to include. 
                Available: 'is_guest', 'reply_message', 'net_amount', 'updated_at_diff_label'

        Returns:
            dict: Parsed JSON response
        """
        query_params = [f"limit={limit}", f"page={page}"]

        if include:
            if isinstance(include, list):
                include = ','.join(include)
            query_params.append(f"include={include}")

        query_string = "&".join(query_params)
        url = f"{self.base_url}/transactions?{query_string}"

        return self._req(url)

    def get_quantity_given(
        self,
        email: str
    ) -> dict:
        """
        Fetches the quantity of support given by a supporter based on their email.
        
        Args:
            email (str): The supporter's email address.

        Returns:
            dict: Parsed JSON response from Trakteer API.
        """
        url = f"{self.base_url}/quantity-given"
        data = {"email": email}

        try:
            r = requests.post(url, headers=self.headers, data=data, timeout=5)
            response = r.json()
            if response.get("message") == "This action is unauthorized.":
                raise ValueError("Invalid API key or unauthorized access.")
            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            raise Exception(f"Connection error: {e}")
