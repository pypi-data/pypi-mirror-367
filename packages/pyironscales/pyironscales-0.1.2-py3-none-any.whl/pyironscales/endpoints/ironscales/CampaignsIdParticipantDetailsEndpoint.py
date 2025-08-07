from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IGettable,
    IPaginateable,
)
from pyironscales.models.ironscales import CampaignParticipants
from pyironscales.responses.paginated_response import PaginatedResponse
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class CampaignsIdParticipantDetailsEndpoint(
    IronscalesEndpoint,
    IGettable[CampaignParticipants, IronscalesRequestParams],
    IPaginateable[CampaignParticipants, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "participant-details", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, CampaignParticipants)
        IPaginateable.__init__(self, CampaignParticipants)

    def paginated(
        self,
        page: int,
        params: IronscalesRequestParams | None = None,
    ) -> PaginatedResponse[CampaignParticipants]:
        """
        Performs a GET request against the /campaigns/{id}/participant-details endpoint and returns an initialized PaginatedResponse object.

        Parameters:
            page (int): The page number to request.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            PaginatedResponse[CampaignParticipants]: The initialized PaginatedResponse object.
        """
        if params:
            params["page"] = page
        else:
            params = {"page": page}
        return PaginatedResponse(
            super()._make_request("GET", params=params),
            CampaignParticipants,
            self,
            "participants",
            page,
            params,
        )

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> CampaignParticipants:
        """
        Performs a GET request against the /campaigns/{id}/participant-details endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            AuthInformation: The parsed response data.
        """
        return self._parse_one(
            CampaignParticipants,
            super()._make_request("GET", data=data, params=params).json().get('participants', {}),
        )
