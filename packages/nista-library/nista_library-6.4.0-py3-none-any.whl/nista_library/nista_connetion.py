"""Nista Connection

Contains all connections possible to nista.io
"""

import datetime
import webbrowser
from typing import Optional

import jwt
import keyring
from oauth2_client.credentials_manager import OAuthError, ServiceInformation
from structlog import get_logger

from nista_library.nista_credential_manager import NistaCredentialManager

log = get_logger()


# pylint: disable=too-many-instance-attributes
class NistaConnection:
    """
    Base class to open connection to nista.io
    :scope: the list of scopes to be requested from the Authentication service
    """

    scope = ["data-api"]

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        workspace_id: str,
        base_url: Optional[str] = None,
        datapoint_base_url: Optional[str] = None,
        authentication_base_url: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        verify_ssl=True,
    ):
        """Create NistaConnection
        :param workspace_id: The ID of the workspace to establish connection
        :param base_url: "https://app.nista.io" if left None
        :param datapoint_base_url: "/api/datapoint" if left None
        :param authentication_base_url: "/api/authentication" if left None
        :param client_id: username for an optional login with OAuth2.0 Client/Secret Authentication
        :param client_secret: secret for an optional login with OAuth2.0 Client/Secret Authentication
        :param verify_ssl: define if the https connection will be checked for security
        """

        if base_url is None:
            base_url = "https://app.nista.io"

        if datapoint_base_url is None:
            datapoint_base_url = base_url + "/api/datapoint"

        if authentication_base_url is None:
            authentication_base_url = base_url + "/api/authentication"

        self.base_url = base_url
        self.datapoint_base_url = datapoint_base_url
        self.authentication_base_url = authentication_base_url
        self.refresh_token: Optional[str] = None
        self.access_token: Optional[str] = None
        self.id_token: Optional[str] = None
        self.workspace_id: str = workspace_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.verify_ssl = verify_ssl

    def __str__(self):
        token_available = self.access_token is not None
        return "nista Connection to" + self.base_url + " has token: " + token_available

    def _get_base_url(self) -> str:
        return self.base_url

    def get_access_token(self) -> str:
        """
        starts authentication or uses refresh tokens to generate an OAuth2.0 Access Token, used for further interaction.
        :raise ValueError: If token can not be generated.
        """
        if self.refresh_token is None:
            # pylint: disable=E1128
            self.refresh_token = self._load_refresh_token()

        if self.refresh_token is not None:
            try:
                log.info("Using stored refresh Token to Login")
                self._refresh_tokens(refresh_token=self.refresh_token)
            except OAuthError:
                log.info("Error using refresh Token, try getting a new one", exc_info=True)
                if self.client_id is not None and self.client_secret is not None:
                    log.info("Client Credentials Flow")
                    self._create_tokens_client_credentials(
                        client_id=self.client_id, client_secret=self.client_secret, scope=self.scope
                    )
                else:
                    log.info("Auth Code Flow")
                    self._create_tokens_code_flow()

        if self.access_token is not None:
            try:
                token = jwt.decode(
                    self.access_token,
                    algorithms=[
                        "RS256",
                    ],
                    options={"verify_signature": False},
                )
                exp = token["exp"]
                exp_date = datetime.datetime.fromtimestamp(exp)
                real_exp_date = exp_date - datetime.timedelta(seconds=3 * 60)
                if real_exp_date > datetime.datetime.now():
                    return self.access_token
            except jwt.ExpiredSignatureError:
                pass

        log.info("Starting First Time Login")
        if self.client_id is not None and self.client_secret is not None:
            log.info("Client Credentials Flow")
            self._create_tokens_client_credentials(
                client_id=self.client_id, client_secret=self.client_secret, scope=self.scope
            )
        else:
            log.info("Auth Code Flow")
            self._create_tokens_code_flow()

        if self.access_token is None:
            raise ValueError("No Token available")

        return self.access_token

    def _get_service_info(
        self, scope: Optional[list] = None, client_id: str = "python", client_secret: Optional[str] = None
    ) -> ServiceInformation:
        if scope is None:
            scope = self.scope

        return ServiceInformation(
            self.authentication_base_url + "/connect/authorize",
            self.authentication_base_url + "/connect/token",
            client_id,
            client_secret,
            scope,
            False,
        )

    def _refresh_tokens(self, refresh_token: str):
        service_information = self._get_service_info()
        manager = NistaCredentialManager(service_information)
        manager.init_with_token(refresh_token)

        self.access_token = manager.access_token
        self.refresh_token = manager.refresh_token
        self.id_token = manager.id_token

        if self.refresh_token is not None:
            self._store_refresh_token(refresh_token=self.refresh_token)

    def _create_tokens_code_flow(self, scope: Optional[list] = None):
        if scope is None:
            scope = self.scope

        scope.append("openid")
        scope.append("profile")
        scope.append("offline_access")

        service_information = self._get_service_info(scope)

        manager = NistaCredentialManager(service_information)
        # manager.init_with_client_credentials()
        redirect_uri = "http://localhost:4200/home"
        url = manager.init_authorize_code_process(redirect_uri=redirect_uri, state="myState")
        log.info("Authentication has been started. Please follow the link to authenticate with your user:", url=url)
        webbrowser.open(url)

        code = manager.wait_and_terminate_authorize_code_process()
        # From this point the http server is opened on 8080 port and wait to receive a single GET request
        # All you need to do is open the url and the process will go on
        # (as long you put the host part of your redirect uri in your host file)
        # when the server gets the request with the code (or error) in its query parameters

        manager.init_with_authorize_code(redirect_uri, code)
        # Here access and refresh token may be used with self.refresh_token
        self.access_token = manager.access_token
        self.refresh_token = manager.refresh_token
        self.id_token = manager.id_token

        if self.refresh_token is not None:
            self._store_refresh_token(refresh_token=self.refresh_token)

    def _create_tokens_client_credentials(self, client_id: str, client_secret: str, scope: Optional[list] = None):
        if scope is None:
            scope = self.scope

        service_information = self._get_service_info(scope, client_id, client_secret)

        manager = NistaCredentialManager(service_information)
        manager.init_with_client_credentials()

        # Here access and refresh token may be used with self.refresh_token
        self.access_token = manager.access_token

        if self.refresh_token is not None:
            self._store_refresh_token(refresh_token=self.refresh_token)

    def _store_refresh_token(self, refresh_token: str):
        pass

    def _load_refresh_token(self) -> Optional[str]:
        return None


class StaticTokenNistaConnection(NistaConnection):
    """Connection class that uses a static token string to establish connections
    :refresh_token: the token to be used for connecting with nista.io
    """

    def __init__(
        self, workspace_id: str, base_url: Optional[str] = None, refresh_token: Optional[str] = None, verify_ssl=True
    ):
        """
        :param workspace_id: The ID of the workspace to establish connection
        :param base_url: "https://app.nista.io" if left None
        :param refresh_token: the token to be used for connecting with nista.io
        :param verify_ssl: define if the https connection will be checked for security
        """

        super().__init__(workspace_id=workspace_id, base_url=base_url, verify_ssl=verify_ssl)
        self.refresh_token = refresh_token

    def _store_refresh_token(self, refresh_token: str):
        pass

    def _load_refresh_token(self) -> Optional[str]:
        return self.refresh_token


class ReferenceTokenNistaConnection(NistaConnection):
    """Connection class that uses a static token string to establish connections
    :reference_token: the token (PAT) to be used for connecting with nista.io
    """
    def __init__(
        self,
        workspace_id: str,
        reference_token: str,
        base_url: Optional[str] = None,
        verify_ssl=True,
    ):
        """
        :param workspace_id: The ID of the workspace to establish connection
        :param reference_token: the token to be used for connecting with nista.io
        :param base_url: "https://app.nista.io" if left None
        :param verify_ssl: define if the https connection will be checked for security
        """
        super().__init__(
            workspace_id=workspace_id, base_url=base_url, verify_ssl=verify_ssl
        )
        self.reference_token = reference_token

    def _store_refresh_token(self, refresh_token: str):
        pass

    def _load_refresh_token(self) -> Optional[str]:
        return self.refresh_token

    def get_access_token(self) -> str:
        return self.reference_token


class KeyringNistaConnection(NistaConnection):
    """OAuth2.0 Connection which stores received access tokens in a local Keyring.
    :enable_store_refresh_token: switch storage of refreshtoken on/off, in order to just keep access token for a limited period of time
    :service_name: the keyring service name to be used to store access tokens
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        workspace_id: str,
        service_name: str = "nista_library",
        base_url: Optional[str] = None,
        enable_store_refresh_token: bool = True,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        verify_ssl=True,
    ):
        """
        :param workspace_id: The ID of the workspace to establish connection
        :param service_name: the keyring service name to be used to store access tokens, default is "nista_library"
        :param base_url: "https://app.nista.io" if left None
        :param enable_store_refresh_token: switch storage of refreshtoken on/off, in order to just keep access token for a limited period of time
        :param client_id: username for an optional login with OAuth2.0 Client/Secret Authentication
        :param client_secret: secret for an optional login with OAuth2.0 Client/Secret Authentication
        :param verify_ssl: define if the https connection will be checked for security
        """
        super().__init__(
            base_url=base_url,
            workspace_id=workspace_id,
            client_id=client_id,
            client_secret=client_secret,
            verify_ssl=verify_ssl,
        )
        self.enable_store_refresh_token = enable_store_refresh_token
        self.service_name = service_name

    def _get_token_name(self):
        return "__refresh_token__:" + super()._get_base_url()

    def clear_stored_token(self):
        keyring.delete_password(self.service_name, self._get_token_name())

    def _store_refresh_token(self, refresh_token: str):
        if self.enable_store_refresh_token:
            pass

        keyring.set_password(self.service_name, self._get_token_name(), refresh_token)

    def _load_refresh_token(self) -> Optional[str]:
        token = keyring.get_password(self.service_name, self._get_token_name())
        return token
