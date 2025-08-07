from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IPostable,
)
from pyironscales.models.ironscales import IntegrationO365AuthorizeResponse
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class IntegrationsIdO365AuthorizeEndpoint(
    IronscalesEndpoint,
    IPostable[IntegrationO365AuthorizeResponse, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "o365-authorize/", parent_endpoint=parent_endpoint)
        IPostable.__init__(self, IntegrationO365AuthorizeResponse)

    def post(self, data: JSON | None = None, params: IronscalesRequestParams | None = None) -> IntegrationO365AuthorizeResponse:
        """
        Performs a POST request against the /integrations/{id}/o365-authorize/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            IntegrationO365AuthorizeResponse: The parsed IntegrationO365AuthorizeResponse data.
        """
        return self._parse_one(IntegrationO365AuthorizeResponse, super()._make_request("POST", data=data, params=params).json())
