from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IPostable,
)
from pyironscales.models.ironscales import IntegrationDisableIntegration
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class IntegrationsIdDisableIntegrationEndpoint(
    IronscalesEndpoint,
    IPostable[IntegrationDisableIntegration, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "manifest/", parent_endpoint=parent_endpoint)
        IPostable.__init__(self, IntegrationDisableIntegration)

    def post(self, data: JSON | None = None, params: IronscalesRequestParams | None = None) -> IntegrationDisableIntegration:
        """
        Performs a POST request against the /integrations/{id}/disable-integration/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            IntegrationDisableIntegration: The parsed Company data.
        """
        return self._parse_one(IntegrationDisableIntegration, super()._make_request("POST", data=data, params=params).json())
