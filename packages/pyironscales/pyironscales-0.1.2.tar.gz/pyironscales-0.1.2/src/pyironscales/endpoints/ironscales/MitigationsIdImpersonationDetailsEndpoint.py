from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IGettable,
    IPostable,
    IPaginateable,
)
from pyironscales.models.ironscales import CompanyImpersonationIncidents
from pyironscales.responses.paginated_response import PaginatedResponse
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)

class MitigationsIdImpersonationDetailsEndpoint(
    IronscalesEndpoint,
    IGettable[CompanyImpersonationIncidents, IronscalesRequestParams],
    IPostable[CompanyImpersonationIncidents, IronscalesRequestParams],
    IPaginateable[CompanyImpersonationIncidents, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "details/", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, CompanyImpersonationIncidents)
        IPostable.__init__(self, CompanyImpersonationIncidents)
        IPaginateable.__init__(self, CompanyImpersonationIncidents)

    def paginated(
        self,
        page: int,
        params: IronscalesRequestParams | None = None,
    ) -> PaginatedResponse[CompanyImpersonationIncidents]:
        """
        Performs a GET request against the /mitigations/{id}/impersonation/details/ endpoint and returns an initialized PaginatedResponse object.

        Parameters:
            page (int): The page number to request.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            PaginatedResponse[CompanyImpersonationIncidents]: The initialized PaginatedResponse object.
        """
        if params:
            params["page"] = page
        else:
            params = {"page": page}
        return PaginatedResponse(
            super()._make_request("GET", params=params),
            CompanyImpersonationIncidents,
            self,
            "incidents",
            page,
            params,
        )

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> CompanyImpersonationIncidents:
        """
        Performs a GET request against the /mitigations/{id}/impersonation/details/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyImpersonationIncidents: The parsed response data.
        """
        return self._parse_many(
            CompanyImpersonationIncidents,
            super()._make_request("GET", data=data, params=params).json().get('incidents', {}),
        )

    def post(self, data: JSON | None = None, params: IronscalesRequestParams | None = None) -> CompanyImpersonationIncidents:
        """
        Performs a POST request against the /mitigations/{id}/details/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyImpersonationIncidents: The parsed CompanyImpersonationIncidents data.
        """
        return self._parse_one(CompanyImpersonationIncidents, super()._make_request("POST", data=data, params=params).json().get('incidents', {}))
