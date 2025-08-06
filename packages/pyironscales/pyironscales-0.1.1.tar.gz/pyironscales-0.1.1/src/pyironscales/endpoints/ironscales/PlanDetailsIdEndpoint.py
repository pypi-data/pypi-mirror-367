from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IGettable,
)
from pyironscales.models.ironscales import CompanyLicense
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class PlanDetailsIdEndpoint(
    IronscalesEndpoint,
    IGettable[CompanyLicense, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "{id}", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, CompanyLicense)

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> CompanyLicense:
        """
        Performs a GET request against the /emails/{id} endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyLicense: The parsed response data.
        """
        return self._parse_one(
            CompanyLicense,
            super()._make_request("GET", data=data, params=params).json(),
        )
