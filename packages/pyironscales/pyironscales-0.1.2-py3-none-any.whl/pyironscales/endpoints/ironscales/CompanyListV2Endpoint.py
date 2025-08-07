from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IGettable,
    IPaginateable,
)
from pyironscales.models.ironscales import PartnerCompanyV2
from pyironscales.responses.paginated_response import PaginatedResponse
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class CompanyListV2Endpoint(
    IronscalesEndpoint,
    IGettable[PartnerCompanyV2, IronscalesRequestParams],
    IPaginateable[PartnerCompanyV2, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "v2/", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, PartnerCompanyV2)
        IPaginateable.__init__(self, PartnerCompanyV2)

    def paginated(
        self,
        page: int,
        params: IronscalesRequestParams | None = None,
    ) -> PaginatedResponse[PartnerCompanyV2]:
        """
        Performs a GET request against the /company/list/v2/ endpoint and returns an initialized PaginatedResponse object.

        Parameters:
            page (int): The page number to request.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            PaginatedResponse[PartnerCompanyV2]: The initialized PaginatedResponse object.
        """
        if params:
            params["page"] = page
        else:
            params = {"page": page}
        return PaginatedResponse(
            super()._make_request("GET", params=params),
            PartnerCompanyV2,
            self,
            "data",
            page,
            params,
        )

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> PartnerCompanyV2:
        """
        Performs a GET request against the /company/list/v2/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            PartnerCompanyV2: The parsed response data.
        """
        return self._parse_many(
            PartnerCompanyV2,
            super()._make_request("GET", data=data, params=params).json().get('data', {}),
        )
