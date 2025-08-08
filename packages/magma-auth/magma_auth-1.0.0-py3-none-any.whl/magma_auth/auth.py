# Standard library imports
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Self

# Third party imports
import requests
from magma_database import config
from requests import RequestException

# Project imports
from magma_auth.const import URL_LOGIN, URL_LOGIN_STAKEHOLDER
from magma_auth.encryptor import Encryptor
from magma_auth.utils import decode_token, validate_token

database_location = config["DATABASE_LOCATION"]
headers = {"Content-Type": "application/json"}


class Auth:
    def __init__(self):
        self.expired_at = None
        self.success = False
        self.encryptor = Encryptor()
        self._token = None
        self._token_file_location = os.path.join(database_location, ".token")
        self._credential_location = os.path.join(database_location, ".credential")

    @property
    def token(self) -> str | None:
        if self._token is not None:
            return self.encryptor.hybrid_decrypt()

        if os.path.exists(self._token_file_location):
            with open(self._token_file_location, "r") as f:
                self.encryptor.encrypted_package = json.loads(f.read())

            token = self.encryptor.hybrid_decrypt()
            decoded = decode_token(token)
            self.expired_at = decoded["expired_at"]

            # Remove expired token
            now = datetime.now(timezone.utc)
            if bool(now > self.expired_at):
                try:
                    os.remove(self._token_file_location)
                except Exception as e:
                    raise Exception(f"Error deleting {self._token_file_location}: {e}")

            self.success = True
            return token

        print(f"Token not found. Try login() first.")
        return None

    def login(
        self,
        username: str,
        password: str,
        ttl: int = 3,
        overwrite: bool = True,
        verbose: bool = False,
    ) -> bool:
        """Login using username and password of MAGMA Indonesia

        Args:
            username (str): username of MAGMA Indonesia
            password (str): password of MAGMA Indonesia
            ttl (int, optional): TTL of token as a day. Defaults to 3 day.
            overwrite (bool, optional): overwrite existing credentials. Defaults to True.
            verbose (bool, optional): verbose mode. Defaults to False.

        Returns:
            bool: True if login was successful

        Raises:
            RequestException: If authentication fails
        """
        payload = json.dumps({"username": username, "password": password, "ttl": ttl})

        try:
            response: dict = requests.request(
                "POST", URL_LOGIN, headers=headers, data=payload
            ).json()

            if not response["success"]:
                print(f"Wrong username or password.")
                return False

            self.success = self.save_token(response["token"], revalidate=False)
            self.expired_at = datetime.now() + timedelta(days=ttl)
            self.expired_at = self.expired_at.astimezone(timezone.utc)

            with open(self._token_file_location, "w") as f:
                f.write(json.dumps(self.encryptor.encrypted_package))

            # Save credential
            if overwrite:
                encryptor = Encryptor()
                encryptor.text = payload
                encrypted_payload = encryptor.hybrid_encrypt()

                with open(self._credential_location, "w") as f:
                    f.write(encrypted_payload)

            if verbose:
                print("Logged in successfully.")

            return True
        except RequestException as e:
            raise RequestException(f"Cannot login to MAGMA at the moment. \n{e}")

    def renew(
        self,
        username: str = "username",
        password: str = "password",
        ttl: int = 3,
        verbose: bool = False,
    ) -> bool:
        """Renew token using saved credential.
        Make sure you already have logged in once before.

        Args:
            username (str): Field username of MAGMA Indonesia
            password (str): Field password of MAGMA Indonesia
            ttl (int, optional): TTL of token as a day. Defaults to 3 day.
            verbose (bool, optional): verbose mode. Defaults to False.

        Returns:
            Self: self
        """
        if not os.path.exists(self._credential_location):
            print("Credential not found. Please login first.")
            return False

        try:
            encryptor = Encryptor()
            with open(self._credential_location, "r") as f:
                encryptor.encrypted_package = json.loads(f.read())

            payload = json.loads(encryptor.hybrid_decrypt())
            if self.login(
                payload[username],
                payload[password],
                ttl,
                overwrite=False,
                verbose=verbose,
            ):
                return True

            return False
        except RuntimeError as e:
            print(f"Failed to login using auto method. Try using login method. \n{e}")
            return False

    def save_token(self, token: str, revalidate: bool = True) -> bool:
        """Save token to file.

        Args:
            token (str): token to save
            revalidate (bool, optional): revalidate token. Defaults to True.

        Returns:
            bool: True if save was successful
        """
        token_is_valid = validate_token(token) if revalidate else True

        if token_is_valid:
            self.encryptor.text = token
            self._token: str = self.encryptor.hybrid_encrypt()
            with open(self._token_file_location, "w") as f:
                f.write(json.dumps(self.encryptor.encrypted_package))

            self.success = True
            decoded = decode_token(token)
            self.expired_at = decoded["expired_at"]

            return True

        return False


class AuthExternal(Auth):
    def __init__(self):
        super().__init__()
        self._token_file_location = os.path.join(database_location, ".x-token")
        self._credential_location = os.path.join(database_location, ".x-credential")

    def login(
        self,
        app_id: str,
        secret_key: str,
        overwrite: bool = True,
        verbose: bool = False,
        **kwargs,
    ) -> bool:
        """Login using username and password of MAGMA Indonesia

        Args:
            app_id (str): APP ID Stakeholder of MAGMA Indonesia
            secret_key (str): Secret Key of App ID of MAGMA Indonesia
            overwrite (bool, optional): overwrite existing credentials. Defaults to True.
            verbose (bool, optional): verbose mode. Defaults to False.
            kwargs (dict, optional): additional arguments passed to requests.request. Defaults to None.

        Returns:
            bool: True if login was successful

        Raises:
            RequestException: If authentication fails
        """
        payload = json.dumps({"app_id": app_id, "secret_key": secret_key})

        try:
            response: dict = requests.request(
                "POST", URL_LOGIN_STAKEHOLDER, headers=headers, data=payload
            ).json()

            if "message" in response.keys():
                print(f"Wrong app_id or secret_key.")
                return False

            self.success = self.save_token(response["token"], revalidate=False)
            self.expired_at = datetime.strptime(
                response["expired_at"],
                "%Y-%m-%d %H:%M:%S",
            )

            # Save credential
            if overwrite:
                encryptor = Encryptor()
                encryptor.text = payload
                encrypted_payload = encryptor.hybrid_encrypt()

                with open(self._credential_location, "w") as f:
                    f.write(encrypted_payload)

            if verbose:
                print("Logged in successfully.")

            return True
        except RequestException as e:
            raise RequestException(f"Cannot login to MAGMA at the moment. \n{e}")

    def renew(
        self,
        username: str = "app_id",
        password: str = "secret_key",
        verbose: bool = False,
        **kwargs,
    ) -> bool:
        """Renew token using saved credential.
        Make sure you already have logged in once before.

        Args:
            username (str): Field username of MAGMA Indonesia
            password (str): Field password of MAGMA Indonesia
            verbose (bool, optional): verbose mode. Defaults to False.
            kwargs (dict, optional): additional arguments passed to requests.request. Defaults to None.

        Returns:
            Self: self
        """
        if not os.path.exists(self._credential_location):
            print("Credential not found. Please login first.")
            return False

        try:
            encryptor = Encryptor()
            with open(self._credential_location, "r") as f:
                encryptor.encrypted_package = json.loads(f.read())

            payload = json.loads(encryptor.hybrid_decrypt())
            if self.login(
                payload[username],
                payload[password],
                overwrite=False,
                verbose=verbose,
            ):
                return True

            return False
        except RuntimeError as e:
            print(f"Failed to login using auto method. Try using login method. \n{e}")
            return False
