from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IPostable,
)
from pyironscales.models.ironscales import CompanyManifest
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class CompanyIdManifestEndpoint(
    IronscalesEndpoint,
    IPostable[CompanyManifest, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "manifest/", parent_endpoint=parent_endpoint)
        IPostable.__init__(self, CompanyManifest)

    def post(self, data: JSON | None = None, params: IronscalesRequestParams | None = None) -> CompanyManifest:
        """
        Performs a POST request against the /company/{id}/manifest/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyManifest: The parsed Company data.
        """
        return self._parse_one(CompanyManifest, super()._make_request("POST", data=data, params=params).json())
