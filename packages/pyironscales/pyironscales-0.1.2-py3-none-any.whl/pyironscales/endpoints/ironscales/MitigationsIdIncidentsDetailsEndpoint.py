from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IGettable,
    IPaginateable,
)
from pyironscales.models.ironscales import IncidentDetails
from pyironscales.responses.paginated_response import PaginatedResponse
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)

class MitigationsIdIncidentsDetailsEndpoint(
    IronscalesEndpoint,
    IGettable[IncidentDetails, IronscalesRequestParams],
    IPaginateable[IncidentDetails, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "details/", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, IncidentDetails)
        IPaginateable.__init__(self, IncidentDetails)

    def paginated(
        self,
        page: int,
        params: IronscalesRequestParams | None = None,
    ) -> PaginatedResponse[IncidentDetails]:
        """
        Performs a GET request against the /mitigations/{id}/incidents/details/ endpoint and returns an initialized PaginatedResponse object.

        Parameters:
            page (int): The page number to request.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            PaginatedResponse[IncidentDetails]: The initialized PaginatedResponse object.
        """
        if params:
            params["page"] = page
        else:
            params = {"page": page}
        return PaginatedResponse(
            super()._make_request("GET", params=params),
            IncidentDetails,
            self,
            "incidents",
            page,
            params,
        )

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> IncidentDetails:
        """
        Performs a GET request against the /mitigations/{id}/incidents/details/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            IncidentDetails: The parsed response data.
        """
        return self._parse_many(
            IncidentDetails,
            super()._make_request("GET", data=data, params=params).json().get('incidents', {}),
        )
