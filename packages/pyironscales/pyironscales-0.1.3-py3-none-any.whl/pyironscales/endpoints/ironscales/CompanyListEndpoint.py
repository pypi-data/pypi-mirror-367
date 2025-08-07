from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.endpoints.ironscales.CompanyListV2Endpoint import CompanyListV2Endpoint

from pyironscales.interfaces import (
    IGettable,
)
from pyironscales.models.ironscales import PartnerCompany
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class CompanyListEndpoint(
    IronscalesEndpoint,
    IGettable[PartnerCompany, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "list", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, PartnerCompany)
        self.v2 = self._register_child_endpoint(CompanyListV2Endpoint(client, parent_endpoint=self))

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> PartnerCompany:
        """
        Performs a GET request against the /company/list endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            AuthInformation: The parsed response data.
        """
        return self._parse_many(
            PartnerCompany,
            super()._make_request("GET", data=data, params=params).json().get('companies', {}),
        )
