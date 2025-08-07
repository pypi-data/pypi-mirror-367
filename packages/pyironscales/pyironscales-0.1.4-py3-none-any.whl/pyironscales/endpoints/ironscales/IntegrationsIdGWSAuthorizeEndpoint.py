from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IPostable,
)
from pyironscales.models.ironscales import IntegrationGWSAuthorizeResponse
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class IntegrationsIdGWSAuthorizeEndpoint(
    IronscalesEndpoint,
    IPostable[IntegrationGWSAuthorizeResponse, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "gws-authorize/", parent_endpoint=parent_endpoint)
        IPostable.__init__(self, IntegrationGWSAuthorizeResponse)

    def post(self, data: JSON | None = None, params: IronscalesRequestParams | None = None) -> IntegrationGWSAuthorizeResponse:
        """
        Performs a POST request against the /integrations/{id}/gws-authorize/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            IntegrationGWSAuthorizeResponse: The parsed IntegrationGWSAuthorizeResponse data.
        """
        return self._parse_one(IntegrationGWSAuthorizeResponse, super()._make_request("POST", data=data, params=params).json())
