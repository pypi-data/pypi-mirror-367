from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IGettable,
    IPostable,
    IPuttable,
    IDeleteable,
)
from pyironscales.models.ironscales import ChallengedAlerts
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)

class SettingsIdChallengedAlertsEndpoint(
    IronscalesEndpoint,
    IGettable[ChallengedAlerts, IronscalesRequestParams],
    IPostable[ChallengedAlerts, IronscalesRequestParams],
    IPuttable[ChallengedAlerts, IronscalesRequestParams],
    IDeleteable[IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "challenged-alerts/", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, ChallengedAlerts)
        IPuttable.__init__(self, ChallengedAlerts)

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> ChallengedAlerts:
        """
        Performs a GET request against the /settings/{id}/challenged-alerts/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            ChallengedAlerts: The parsed response data.
        """
        return self._parse_one(
            ChallengedAlerts,
            super()._make_request("GET", data=data, params=params).json(),
        )

    def post(self, data: JSON | None = None, params: IronscalesRequestParams | None = None) -> ChallengedAlerts:
        """
        Performs a POST request against the /settings/{id}/challenged-alerts/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            ChallengedAlerts: The parsed Company data.
        """
        return self._parse_one(ChallengedAlerts, super()._make_request("POST", data=data, params=params).json())

    def put(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> ChallengedAlerts:
        """
        Performs a PUT request against the /settings/{id}/challenged-alerts/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            ChallengedAlerts: The parsed response data.
        """
        return self._parse_one(
            ChallengedAlerts,
            super()._make_request("PUT", data=data, params=params).json(),
        )

    def delete(self, data: JSON | None = None, params: IronscalesRequestParams | None = None) -> ChallengedAlerts:
        """
        Performs a DELETE request against the /settings/{id}/challenged-alerts/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            ChallengedAlerts: The parsed response data.
        """
        return self._parse_one(ChallengedAlerts, super()._make_request("DELETE", data=data, params=params).json())
