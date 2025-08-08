
import os
import time
import json
from dotenv import load_dotenv
import requests

from .logger_client import Logger
from .user_client import UserClient
from .course_client import CourseClient
from .endpoint_client import EndpointClient
from .gradebook_client import GradebookClient
from .discussion_client import DiscussionClient

from os import getenv
from requests import Response
from requests_oauthlib import OAuth2Session



load_dotenv()

ORG_DOMAIN = getenv("ORG_DOMAIN")


class TokenManager(object):
    token_file = "data/token_cache.json"
    def __new__(cls):
        obj = super().__new__(cls)
        obj.token = None
        obj.expiry_time = 0
        obj.load_token()
        return obj
    
    def __str__(self) -> str:
        return f"Token = {self.token}. Expiration time = {self.expiry_time}"

    def get_token(self):
        current_time = time.time()
        if not self.token or current_time >= self.expiry_time:
            self.request_new_token()
            self.save_token()
        return self.token

    def request_new_token(self):
        _client_id = os.getenv("APP_KEY")
        _client_secret = os.getenv("SECRET")
        _token_url =f'{ORG_DOMAIN}/learn/api/public/v1/oauth2/token'
        _token_response = requests.post(_token_url, data={
            "grant_type": "client_credentials"},
            auth=(_client_id,_client_secret))
        match _token_response.status_code:
            #TODO: Add other cases
            case 200:
                Logger.info("A new token was generated.")
                self.token = _token_response.json()['access_token']
                _expires_in = _token_response.json()['expires_in']
                self.expiry_time = time.time() + _expires_in - 60  # Subtracting 60 seconds to ensure the token is refreshed a bit before it actually expires
            case _:
                Logger.critical(f"Failed to get a token. {_token_response.text}")
            

    def load_token(self):
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as file:
                data = json.load(file)
                self.token = data.get('token')
                self.expiry_time = data.get('expiry_time', 0)


    def save_token(self):
        data = {
            'token': self.token,
            'expiry_time': self.expiry_time
        }
        with open(self.token_file, 'w') as file:
            json.dump(data, file)


def get_access_token() -> str:
    token_manager = TokenManager()
    return token_manager.get_token()

def get_remaining_calls() -> int:
    """Checks to see if a user is already added to the system. 

    Args:
        username (str): _description_

    Returns:
        int: The number of api calls left.
    """
    get_user = f"{ORG_DOMAIN}/learn/api/public/v1/users/userName:1000001"
    response = requests.get(get_user, headers={'Authorization': 'Bearer ' + get_access_token()})
    remaining_requests = response.headers.get('X-Rate-Limit-Remaining')
    if remaining_requests:
        return remaining_requests
    else:
        raise Exception("X-Rate-Limit-Remaining header not found.")






class BlackboardClient:
    def __init__(self, client_id: str, client_secret: str, api_base_url: str, log_file: str="bbpy.log"):
        if not all([client_id, client_secret, api_base_url]):
            raise ValueError("All parameters must be provided and not empty.")
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url =f'{api_base_url}/learn/api/public/v1/oauth2/token'
        self.api_base_url = api_base_url
        self.token = None
        self.token_file = "data/token.json"
        self.expiry_time = None
        self.logger = Logger(log_file)
        self.endpoints = EndpointClient(self.api_base_url)

        
        # Create a session object to persist settings across requests

        self.session = OAuth2Session(client_id=self.client_id)  # Create OAuth2 session
        self.authenticate()
        self.user = UserClient(self)
        self.course = CourseClient(self)
        self.gradebook = GradebookClient(self)
        self.discussion = DiscussionClient(self)

    def get_base_url(self) -> str:
        return self.api_base_url
    
    def _check_if_authenticated(self):
        """
        Ensure the session is authenticated before making an API call.
        This method is called internally before any API request.
        """
        if not self.token or time.time() > self.expiry_time:
            self.authenticate()
    
    def _send_request(self, method, url, **kwargs) -> Response:
        """
        Internal helper method to send HTTP requests.
        This ensures authentication before making the request.
        """
        self._check_if_authenticated()  # Ensure authentication
        # Make the HTTP request (GET, POST, PUT, PATCH, DELETE)
        _response = self.session.request(method, url, **kwargs)

        return _response
        
    
    def get(self, url, **kwargs):
        """Send a GET request using the authenticated session."""
        return self._send_request('GET', url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        """Send a POST request using the authenticated session."""
        return self._send_request('POST', url, data=data, json=json, **kwargs)

    def put(self, url, data=None, json=None, **kwargs):
        """Send a PUT request using the authenticated session."""
        return self._send_request('PUT', url, data=data, json=json, **kwargs)

    def patch(self, url, data=None, json=None, **kwargs):
        """Send a PATCH request using the authenticated session."""
        return self._send_request('PATCH', url, data=data, json=json, **kwargs)

    def delete(self, url, **kwargs):
        """Send a DELETE request using the authenticated session."""
        return self._send_request('DELETE', url, **kwargs)

    def _load_token(self):
        """
        Load the token from a JSON file if it exists and is valid (not expired).
        """
        if os.path.exists(self.token_file):
            with open(self.token_file, "r") as f:
                token_data = json.load(f)
                self.token = token_data.get("access_token")
                self.expiry_time = token_data.get("expiry_time")
                # If the token is expired, discard it
                if self.expiry_time and time.time() > self.expiry_time:
                    self.logger.info("Token expired, requesting a new one.")
                    self.token = None
                    self.expiry_time = None
                else:
                    self.logger.info("Token loaded from file.")
    def save_token(self):
        """
        Save the token and its expiry time to a JSON file.
        """
        #print(self.expiry_time)
        #print(self.token)
        if self.token and self.expiry_time:
            with open(self.token_file, "w") as f:
                json.dump({
                    "access_token": self.token,
                    "expiry_time": self.expiry_time
                }, f)
            self.logger.info("Token saved to file.")
        else:
            self.logger.info("failed to save file")

    def authenticate(self):
        #print(self.session.token)
        """
        Authenticate using OAuth2 Client Credentials and store the token in the session.
        """
        self._load_token()

        if not self.token:
            self.request_new_token()
        else:
            print("already have a token")

        self.session.headers.update({
            "Authorization": f'Bearer {self.token}',
            "Accept": "application/json"
        })
        
        # If the token is valid, session will automatically include it in headers
        print("Authenticated successfully.")
    
    def request_new_token(self) -> int:
        """
        Request a new OAuth2 token using client credentials flow and store it.
        """

        try:
            # Fetch the OAuth2 token using client credentials flow
            _token_response = self.session.post(
                self.token_url,
                data={
                    "grant_type": "client_credentials"
                },
                auth=(self.client_id, self.client_secret)  # Basic auth as per client credentials flow
            )

            # Check for successful response
            if _token_response.status_code == 200:
                self.logger.info("A new token was generated.")
                self.token = _token_response.json()['access_token']
                _expires_in = _token_response.json()['expires_in']
                self.expiry_time = time.time() + _expires_in - 60  # Subtracting 60 seconds for early refresh
                # Update the session's token in the header
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                self.save_token()
            else:
                self.logger.critical(f"Failed to get a token. {_token_response.text}")

        except Exception as e:
            self.logger.error(f"Error occurred while fetching token: {e}")

    def get_remaining_calls(self) -> int:
        """Get the remaining number of api calls you can call based on your quota

        Returns:
            int: The number of remaining calls
        """
        get_user = f"{self.api_base_url}/learn/api/public/v1/users/userName:1000001"
        response = self.session.get(get_user)
        remaining_requests = response.headers.get('X-Rate-Limit-Remaining')
        if remaining_requests:
            return remaining_requests
        else:
            Logger.error("X-Rate-Limit-Remaining header not found.")
