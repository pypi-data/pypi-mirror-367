from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IGettable,
    IPaginateable,
)
from pyironscales.models.ironscales import EscalatedEmails
from pyironscales.responses.paginated_response import PaginatedResponse
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class EmailsIdEndpoint(
    IronscalesEndpoint,
    IGettable[EscalatedEmails, IronscalesRequestParams],
    IPaginateable[EscalatedEmails, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "{id}", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, EscalatedEmails)
        IPaginateable.__init__(self, EscalatedEmails)

    def paginated(
        self,
        page: int,
        params: IronscalesRequestParams | None = None,
    ) -> PaginatedResponse[EscalatedEmails]:
        """
        Performs a GET request against the /incident/{id}/list/ endpoint and returns an initialized PaginatedResponse object.

        Parameters:
            page (int): The page number to request.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            PaginatedResponse[EscalatedEmails]: The initialized PaginatedResponse object.
        """
        if params:
            params["page"] = page
        else:
            params = {"page": page}
        return PaginatedResponse(
            super()._make_request("GET", params=params),
            EscalatedEmails,
            self,
            "emails",
            page,
            params,
        )

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> EscalatedEmails:
        """
        Performs a GET request against the /emails/{id} endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            EscalatedEmails: The parsed response data.
        """
        return self._parse_many(
            EscalatedEmails,
            super()._make_request("GET", data=data, params=params).json().get('emails', {}),
        )
