import typing
import json
from datetime import datetime, timedelta, timezone

from pyironscales.clients.base_client import IronscalesClient
from pyironscales.config import Config

if typing.TYPE_CHECKING:
    from pyironscales.endpoints.ironscales.CampaignsEndpoint import CampaignsEndpoint
    from pyironscales.endpoints.ironscales.CompanyEndpoint import CompanyEndpoint
    from pyironscales.endpoints.ironscales.EmailsEndpoint import EmailsEndpoint
    from pyironscales.endpoints.ironscales.IncidentEndpoint import IncidentEndpoint
    from pyironscales.endpoints.ironscales.IntegrationsEndpoint import IntegrationsEndpoint
    from pyironscales.endpoints.ironscales.MailboxesEndpoint import MailboxesEndpoint
    from pyironscales.endpoints.ironscales.MitigationEndpoint import MitigationEndpoint
    from pyironscales.endpoints.ironscales.PlanDetailsEndpoint import PlanDetailsEndpoint
    from pyironscales.endpoints.ironscales.SettingsEndpoint import SettingsEndpoint


class IronscalesAPIClient(IronscalesClient):
    """
    Ironscales API client. Handles the connection to the Ironscales API
    and the configuration of all the available endpoints.
    """

    def __init__(
        self,
        privatekey: str,
        scopes: list,
    ) -> None:
        """
        Initializes the client with the given credentials.

        Parameters:
            privatekey (str): Your Ironscales API private key.
        """
        self.privatekey: str = privatekey
        self.scopes: list = json.loads(scopes) if isinstance(json.loads(scopes), list) else [json.loads(scopes)]
        self.token_expiry_time: datetime = datetime.now(tz=timezone.utc)

        # Grab first access token
        self.access_token: str = self._get_access_token()

    # Initializing endpoints
    @property
    def campaigns(self) -> "CampaignsEndpoint":
        from pyironscales.endpoints.ironscales.CampaignsEndpoint import CampaignsEndpoint

        return CampaignsEndpoint(self)

    @property
    def company(self) -> "CompanyEndpoint":
        from pyironscales.endpoints.ironscales.CompanyEndpoint import CompanyEndpoint

        return CompanyEndpoint(self)

    @property
    def emails(self) -> "EmailsEndpoint":
        from pyironscales.endpoints.ironscales.EmailsEndpoint import EmailsEndpoint

        return EmailsEndpoint(self)

    @property
    def incident(self) -> "IncidentEndpoint":
        from pyironscales.endpoints.ironscales.IncidentEndpoint import IncidentEndpoint

        return IncidentEndpoint(self)

    @property
    def integrations(self) -> "IntegrationsEndpoint":
        from pyironscales.endpoints.ironscales.IntegrationsEndpoint import IntegrationsEndpoint

        return IntegrationsEndpoint(self)

    @property
    def mailboxes(self) -> "MailboxesEndpoint":
        from pyironscales.endpoints.ironscales.MailboxesEndpoint import MailboxesEndpoint

        return MailboxesEndpoint(self)

    @property
    def mitigation(self) -> "MitigationEndpoint":
        from pyironscales.endpoints.ironscales.MitigationEndpoint import MitigationEndpoint

        return MitigationEndpoint(self)

    @property
    def plan_details(self) -> "PlanDetailsEndpoint":
        from pyironscales.endpoints.ironscales.PlanDetailsEndpoint import PlanDetailsEndpoint

        return PlanDetailsEndpoint(self)

    @property
    def settings(self) -> "SettingsEndpoint":
        from pyironscales.endpoints.ironscales.SettingsEndpoint import SettingsEndpoint

        return SettingsEndpoint(self)

    def _get_url(self) -> str:
        """
        Generates and returns the URL for the Ironscales API endpoints based on the company url and codebase.
        Logs in an obtains an access token.
        Returns:
            str: API URL.
        """
        return f"https://appapi.ironscales.com/appapi"

    def _get_access_token(self) -> str:
        """
        Performs a request to the ConnectWise Automate API to obtain an access token.
        """
        auth_response = self._make_request(
            "POST",
            f"{self._get_url()}/get-token/",
            data={
            "key": self.privatekey,
            "scopes": self.scopes
                },
            headers={
                "Content-Type": "application/json",
                },
        )
        auth_resp_json = auth_response.json()
        token = auth_resp_json["jwt"]
        expires_in_sec = 43200
        self.token_expiry_time = datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in_sec)
        return token

    def _refresh_access_token_if_necessary(self):
        if datetime.now(tz=timezone.utc) > self.token_expiry_time:
            self.access_token = self._get_access_token()

    def _get_headers(self) -> dict[str, str]:
        """
        Generates and returns the headers required for making API requests. The access token is refreshed if necessary before returning.

        Returns:
            dict[str, str]: Dictionary of headers including Content-Type, Client ID, and Authorization.
        """
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }
