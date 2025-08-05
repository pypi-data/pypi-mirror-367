import json
import os
import logging
from typing import Dict, Any, Optional

import msal
import requests

from core.utils.app_config import AppConfig

CACHE_FILE = "token_cache.json"


class Microsoft365Provider:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        conf = AppConfig()
        self.client_id = conf.get("MS_CLIENT_ID")
        self.client_secret = conf.get("MS_CLIENT_SECRET")
        self.tenant_id = conf.get("MS_TENANT_ID")
        self.logger.info(f"MS_CLIENT_ID: {self.client_id}, MS_TENANT_ID: {self.tenant_id}")
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scopes = conf.get("MS_SCOPES", "email").split()
        if not self.scopes:
            self.scopes = ["openid", "profile", "offline_access", "User.Read"]
        self.redirect_uri = conf.get("MS_REDIRECT_URI", "https://quantify.alphasixdemo.com/callback")

        self.cache = self._load_cache()
        self.msal_app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=self.authority,
            token_cache=self.cache
        )

        self.authorization_endpoint = f"{self.authority}/oauth2/v2.0/authorize"
        self.token_endpoint = f"{self.authority}/oauth2/v2.0/token"
        self.userinfo_endpoint = "https://graph.microsoft.com/v1.0/me"

    @staticmethod
    def _load_cache() -> msal.SerializableTokenCache:
        cache = msal.SerializableTokenCache()
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                cache.deserialize(f.read())
        return cache

    def _save_cache(self):
        if self.cache.has_state_changed:
            with open(CACHE_FILE, "w") as f:
                f.write(self.cache.serialize())

    def get_auth_url(self, state: str) -> str:
        return self.msal_app.get_authorization_request_url(
            scopes=self.scopes,
            state=state,
            redirect_uri=self.redirect_uri
        )

    def exchange_code(self, code: str) -> Dict[str, Any]:
        result = self.msal_app.acquire_token_by_authorization_code(
            code,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        self._save_cache()

        if "error" in result:
            self.logger.error(f"MSAL error: {result['error_description']}")
            raise Exception(f"MSAL error: {result['error_description']}")

        return result

    def get_user_info(self, token_response: Dict[str, Any]) -> Dict[str, Any]:
        access_token = token_response.get("access_token")
        if not access_token:
            self.logger.error("No access token in token response")
            return {}
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            resp = requests.get(self.userinfo_endpoint, headers=headers)
            resp.raise_for_status()
            user_data = resp.json()
            return {
                "id": user_data.get("id"),
                "email": user_data.get("mail") or user_data.get("userPrincipalName"),
                "displayName": user_data.get("displayName")
            }
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"User info HTTP error: {e}, Response: {e.response.text}")
            return {}
        except Exception as e:
            self.logger.error(f"User info error: {e}")
            return {}

    def get_access_token(self) -> Optional[Dict[str, Any]]:
        accounts = self.msal_app.get_accounts()
        if accounts:
            self.logger.info("Attempting silent token acquisition")
            result = self.msal_app.acquire_token_silent(self.scopes, account=accounts[0])
            if result and "access_token" in result:
                self.logger.info("Token acquired silently")
                return result

        self.logger.info("Silent acquisition failed, using device code flow")
        flow = self.msal_app.initiate_device_flow(scopes=self.scopes)
        print(f"Please visit {flow['verification_uri']} and enter code: {flow['user_code']}")
        result = self.msal_app.acquire_token_by_device_flow(flow)

        if "access_token" in result:
            self.logger.info("Token acquired via device code flow")
            self._save_cache()
            return result

        self.logger.error(f"Token acquisition failed: {result.get('error_description')}")
        return None

    def make_entra_request(self, input_str: str) -> dict:
        try:
            input_data = json.loads(input_str)
            method = input_data["method"]
            path = input_data["path"]
            query_params = input_data.get("query_params", {})
            body = input_data.get("body", {})
        except (json.JSONDecodeError, KeyError) as e:
            return {"error": str(e)}

        token_response = self.get_access_token()
        if not token_response or "access_token" not in token_response:
            return {"error": "No valid access token"}

        url = f"https://graph.microsoft.com/beta/{path}"
        headers = {
            "Authorization": f"Bearer {token_response['access_token']}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.request(method.upper(), url, headers=headers, params=query_params, json=body)
            response.raise_for_status()
            return response.json() if response.status_code != 204 else {"message": "No content"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "response": getattr(e.response, 'text', '')}

    def logout(self) -> bool:
        try:
            accounts = self.msal_app.get_accounts()
            for account in accounts:
                self.msal_app.remove_account(account)
            self.logger.info("Successfully logged out")
            return True
        except Exception as e:
            self.logger.error(f"Logout error: {e}")
            return False
