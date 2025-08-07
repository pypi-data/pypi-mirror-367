from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IGettable,
    IPaginateable,
)
from pyironscales.models.ironscales import UserCampaignPerformance
from pyironscales.responses.paginated_response import PaginatedResponse
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class MailboxesIdUserCampaignsPerformanceEndpoint(
    IronscalesEndpoint,
    IGettable[UserCampaignPerformance, IronscalesRequestParams],
    IPaginateable[UserCampaignPerformance, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "user-campaigns-performance/", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, UserCampaignPerformance)
        IPaginateable.__init__(self, UserCampaignPerformance)

    def paginated(
        self,
        page: int,
        params: IronscalesRequestParams | None = None,
    ) -> PaginatedResponse[UserCampaignPerformance]:
        """
        Performs a GET request against the /mailboxes/{id}/user-campaigns-performance/ endpoint and returns an initialized PaginatedResponse object.

        Parameters:
            page (int): The page number to request.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            PaginatedResponse[UserCampaignPerformance]: The initialized PaginatedResponse object.
        """
        if params:
            params["page"] = page
        else:
            params = {"page": page}
        return PaginatedResponse(
            super()._make_request("GET", params=params),
            UserCampaignPerformance,
            self,
            "data",
            page,
            params,
        )

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> UserCampaignPerformance:
        """
        Performs a GET request against the /mailboxes/{id}/user-campaigns-performance/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            UserCampaignPerformance: The parsed response data.
        """
        return self._parse_many(
            UserCampaignPerformance,
            super()._make_request("GET", data=data, params=params).json().get('data', {}),
        )
