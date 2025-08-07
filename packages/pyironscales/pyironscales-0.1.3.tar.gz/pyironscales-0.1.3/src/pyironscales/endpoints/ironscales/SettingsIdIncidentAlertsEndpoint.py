from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IGettable,
    IPostable,
    IPuttable,
    IDeleteable,
)
from pyironscales.models.ironscales import CompanyNotificationSettings
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)

class SettingsIdChallengedAlertsEndpoint(
    IronscalesEndpoint,
    IGettable[CompanyNotificationSettings, IronscalesRequestParams],
    IPostable[CompanyNotificationSettings, IronscalesRequestParams],
    IPuttable[CompanyNotificationSettings, IronscalesRequestParams],
    IDeleteable[IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "incident-alerts/", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, CompanyNotificationSettings)
        IPuttable.__init__(self, CompanyNotificationSettings)

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> CompanyNotificationSettings:
        """
        Performs a GET request against the /settings/{id}/incident-alerts/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyNotificationSettings: The parsed response data.
        """
        return self._parse_one(
            CompanyNotificationSettings,
            super()._make_request("GET", data=data, params=params).json(),
        )

    def post(self, data: JSON | None = None, params: IronscalesRequestParams | None = None) -> CompanyNotificationSettings:
        """
        Performs a POST request against the /settings/{id}/incident-alerts/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyNotificationSettings: The parsed Company data.
        """
        return self._parse_one(CompanyNotificationSettings, super()._make_request("POST", data=data, params=params).json())

    def put(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> CompanyNotificationSettings:
        """
        Performs a PUT request against the /settings/{id}/incident-alerts/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyNotificationSettings: The parsed response data.
        """
        return self._parse_one(
            CompanyNotificationSettings,
            super()._make_request("PUT", data=data, params=params).json(),
        )

    def delete(self, data: JSON | None = None, params: IronscalesRequestParams | None = None) -> CompanyNotificationSettings:
        """
        Performs a DELETE request against the /settings/{id}/incident-alerts/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyNotificationSettings: The parsed response data.
        """
        return self._parse_one(CompanyNotificationSettings, super()._make_request("DELETE", data=data, params=params).json())
