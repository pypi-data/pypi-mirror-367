from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IPostable,
)
from pyironscales.models.ironscales import IntegrationsO365ConsentRedirectURLResponse
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class IntegrationsIdO365ConsentRedirectURIEndpoint(
    IronscalesEndpoint,
    IPostable[IntegrationsO365ConsentRedirectURLResponse, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "o365-consent-redirect-uri/", parent_endpoint=parent_endpoint)
        IPostable.__init__(self, IntegrationsO365ConsentRedirectURLResponse)

    def post(self, data: JSON | None = None, params: IronscalesRequestParams | None = None) -> IntegrationsO365ConsentRedirectURLResponse:
        """
        Performs a POST request against the /integrations/{id}/o365-consent-redirect-uri/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            IntegrationsO365ConsentRedirectURLResponse: The parsed IntegrationsO365ConsentRedirectURLResponse data.
        """
        return self._parse_one(IntegrationsO365ConsentRedirectURLResponse, super()._make_request("POST", data=data, params=params).json())
