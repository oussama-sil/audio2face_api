import requests


class HttpClient:

    def __init__(self, api_url: str = "http://localhost:8011"):
        """
        Initializes the HttpClient with the server URL.

        :param server_url: The base URL of the server.
        """
        self.api_url = api_url

    def get(self, api_route):
        """
        Sends a GET request to the specified URL and returns the JSON response.

        :param url: The URL to send the GET request to.
        :return: JSON response from the server.
        """
        url = f"{self.api_url}/{api_route}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()

    def post(self, api_route, payload):
        """
        Sends a POST request to the specified URL with the given payload and returns the JSON response.

        :param url: The URL to send the POST request to.
        :param payload: The data to send in the POST request body.
        :return: JSON response from the server.
        """
        url = f"{self.api_url}/{api_route}"
        response = requests.post(url, json=payload, headers="")
        response.raise_for_status()  # Raise an exception for HTTP errors
        try:
            return response.json()  # Ensure the response is in JSON format
        except requests.JSONDecodeError:
            raise ValueError("Response is not in JSON format")
