from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IPostable,
)
from pyironscales.models.ironscales import PartnerCompany
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class CompanyCreateEndpoint(
    IronscalesEndpoint,
    IPostable[PartnerCompany, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "create", parent_endpoint=parent_endpoint)
        IPostable.__init__(self, PartnerCompany)

    def post(self, data: JSON | None = None, params: IronscalesRequestParams | None = None) -> PartnerCompany:
        """
        Performs a POST request against the /company/create endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            Survey: The parsed Company data.
        """
        return self._parse_one(PartnerCompany, super()._make_request("POST", data=data, params=params).json())
