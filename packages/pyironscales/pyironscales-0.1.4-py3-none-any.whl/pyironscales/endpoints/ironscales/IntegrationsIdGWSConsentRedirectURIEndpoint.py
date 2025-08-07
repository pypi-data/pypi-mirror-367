from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IPostable,
)
from pyironscales.models.ironscales import IntegrationsGWSConsentRedirectURL
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class IntegrationsIdGWSConsentRedirectURIEndpoint(
    IronscalesEndpoint,
    IPostable[IntegrationsGWSConsentRedirectURL, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "gws-consent-redirect-uri/", parent_endpoint=parent_endpoint)
        IPostable.__init__(self, IntegrationsGWSConsentRedirectURL)

    def post(self, data: JSON | None = None, params: IronscalesRequestParams | None = None) -> IntegrationsGWSConsentRedirectURL:
        """
        Performs a POST request against the /integrations/{id}/gws-consent-redirect-uri/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            IntegrationsGWSConsentRedirectURL: The parsed IntegrationsGWSConsentRedirectURL data.
        """
        return self._parse_one(IntegrationsGWSConsentRedirectURL, super()._make_request("POST", data=data, params=params).json())
