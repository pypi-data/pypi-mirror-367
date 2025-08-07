from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IGettable,
    IPaginateable,
)
from pyironscales.models.ironscales import ScanbackIncidents
from pyironscales.responses.paginated_response import PaginatedResponse
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class IncidentIdScanbackListEndpoint(
    IronscalesEndpoint,
    IGettable[ScanbackIncidents, IronscalesRequestParams],
    IPaginateable[ScanbackIncidents, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "scanback-list/", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, ScanbackIncidents)
        IPaginateable.__init__(self, ScanbackIncidents)

    def paginated(
        self,
        page: int,
        params: IronscalesRequestParams | None = None,
    ) -> PaginatedResponse[ScanbackIncidents]:
        """
        Performs a GET request against the /incident/{id}/scanback-list/ endpoint and returns an initialized PaginatedResponse object.

        Parameters:
            page (int): The page number to request.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            PaginatedResponse[ScanbackIncidents]: The initialized PaginatedResponse object.
        """
        if params:
            params["page"] = page
        else:
            params = {"page": page}
        return PaginatedResponse(
            super()._make_request("GET", params=params),
            ScanbackIncidents,
            self,
            "incidents",
            page,
            params,
        )

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> ScanbackIncidents:
        """
        Performs a GET request against the /incident/{id}/scanback-list/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            ScanbackIncidents: The parsed response data.
        """
        return self._parse_many(
            ScanbackIncidents,
            super()._make_request("GET", data=data, params=params).json().get('incidents', {}),
        )
