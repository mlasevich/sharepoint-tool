"""
Sharepoint Authenticator

"""
import functools
import json

import requests


class SharepointAuth:
    """
    Sharepoint Authenticator

    Authenticates with Sharepoint and gets auth token
    """

    def __init__(self, host, client_id, client_secret):
        """
        Initialize Authenticator

        :param host: site host
        :param client_id: authentication client id
        :param client_secret: authentication secret
        """
        self.host = host
        self.client_id = client_id
        self.client_secret = client_secret

    @property
    @functools.lru_cache(maxsize=None)
    def _remote_data(self):
        """ Get login data"""
        res = requests.get(f"https://{self.host}/_vti_bin/client.svc/",
                           headers={'Authorization': 'Bearer'})
        resp = {}
        for item in res.headers.get('WWW-Authenticate', '').split(','):
            parts = item.split('=', 1)
            if len(parts) > 1:
                resp[parts[0]] = parts[1]
        return (resp.get('Bearer realm', None).strip('"'),
                resp.get('client_id', None).strip('"'))

    @property
    @functools.lru_cache(maxsize=None)
    def bearer_realm(self):
        """ Get token Id"""
        bearer_realm, _ = self._remote_data
        return bearer_realm

    @property
    @functools.lru_cache(maxsize=None)
    def app_id(self):
        """ Get token Id"""
        _, app_id = self._remote_data
        return app_id

    @property
    @functools.lru_cache(maxsize=None)
    def resource_id(self):
        """ get resource id"""
        return f"{self.app_id}/{self.host}@{self.bearer_realm}"

    @property
    @functools.lru_cache(maxsize=None)
    def auth_url(self):
        """ Get auth url"""
        return f"https://accounts.accesscontrol.windows.net/" \
               f"{self.bearer_realm}/tokens/OAuth/2"

    @property
    def full_client_id(self):
        """ Get qualified client id"""
        return f"{self.client_id}@{self.bearer_realm}"

    @property
    @functools.lru_cache(maxsize=None)
    def bearer_token(self):
        """ Get bearer token """
        data = {"client_id": self.full_client_id,
                "client_secret": self.client_secret,
                "resource": self.resource_id,
                "grant_type": "client_credentials"}
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        res = requests.post(self.auth_url, data=data, headers=headers)

        bearer_token = json.loads(res.text)
        return bearer_token

    @property
    def access_token(self):
        """ get bearer access token"""
        return self.bearer_token.get("access_token", None)

    @property
    def connected(self):
        """
        Check if we are connected and have access token

        :return: true if we have access token
        """
        return self.access_token is not None
