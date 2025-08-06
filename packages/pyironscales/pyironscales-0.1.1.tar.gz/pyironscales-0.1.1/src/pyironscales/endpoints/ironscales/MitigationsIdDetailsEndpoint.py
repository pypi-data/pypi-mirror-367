from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.endpoints.ironscales.MitigationsIdDetailsEndpoint import MitigationsIdDetailsEndpoint
from pyironscales.interfaces import (
    IPostable,
)
from pyironscales.models.ironscales import CompanyMitigationDetails, CompanyMitigationDetailsPostResponse
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)

class IncidentIdDetailsEndpoint(
    IronscalesEndpoint,
    IPostable[CompanyMitigationDetails, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "details/", parent_endpoint=parent_endpoint)
        IPostable.__init__(self, CompanyMitigationDetailsPostResponse)

    def post(self, data: JSON | None = None, params: IronscalesRequestParams | None = None) -> CompanyMitigationDetailsPostResponse:
        """
        Performs a POST request against the /mitigations/{id}/details/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyMitigationDetailsPostResponse: The parsed CompanyMitigationDetailsPostResponse data.
        """
        return self._parse_one(CompanyMitigationDetailsPostResponse, super()._make_request("POST", data=data, params=params).json())
