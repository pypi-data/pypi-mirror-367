from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IGettable,
    IPostable,
    IPuttable,
)
from pyironscales.models.ironscales import CompanyFeaturesStates
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class CompanyIdFeaturesEndpoint(
    IronscalesEndpoint,
    IGettable[CompanyFeaturesStates, IronscalesRequestParams],
    IPostable[CompanyFeaturesStates, IronscalesRequestParams],
    IPuttable[CompanyFeaturesStates, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "features/", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, CompanyFeaturesStates)
        IPostable.__init__(self, CompanyFeaturesStates)
        IPuttable.__init__(self, CompanyFeaturesStates)

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> CompanyFeaturesStates:
        """
        Performs a GET request against the /company/{id}/features/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyFeaturesStates: The parsed response data.
        """
        return self._parse_one(
            CompanyFeaturesStates,
            super()._make_request("GET", data=data, params=params).json(),
        )

    def post(self, data: JSON | None = None, params: IronscalesRequestParams | None = None) -> CompanyFeaturesStates:
        """
        Performs a POST request against the /company/{id}/features/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyAutoSyncStatus: The parsed Company data.
        """
        return self._parse_one(CompanyFeaturesStates, super()._make_request("POST", data=data, params=params).json())

    def put(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> CompanyFeaturesStates:
        """
        Performs a PUT request against the /company/{id} endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyFeaturesStates: The parsed response data.
        """
        return self._parse_one(
            CompanyFeaturesStates,
            super()._make_request("PUT", data=data, params=params).json(),
        )
