from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IGettable,
    IPuttable,
    IPaginateable,
)
from pyironscales.models.ironscales import CompanyMailboxes, CompanyMailboxesPutResponse
from pyironscales.responses.paginated_response import PaginatedResponse
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class MailboxesIdListEndpoint(
    IronscalesEndpoint,
    IGettable[CompanyMailboxes, IronscalesRequestParams],
    IPuttable[CompanyMailboxes, IronscalesRequestParams],
    IPaginateable[CompanyMailboxes, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "list/", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, CompanyMailboxes)
        IPuttable.__init__(self, CompanyMailboxes)
        IPaginateable.__init__(self, CompanyMailboxes)

    def paginated(
        self,
        page: int,
        params: IronscalesRequestParams | None = None,
    ) -> PaginatedResponse[CompanyMailboxes]:
        """
        Performs a GET request against the /mailboxes/{id}/list/ endpoint and returns an initialized PaginatedResponse object.

        Parameters:
            page (int): The page number to request.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            PaginatedResponse[CompanyMailboxes]: The initialized PaginatedResponse object.
        """
        if params:
            params["page"] = page
        else:
            params = {"page": page}
        return PaginatedResponse(
            super()._make_request("GET", params=params),
            CompanyMailboxes,
            self,
            "mailboxes",
            page,
            params,
        )

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> CompanyMailboxes:
        """
        Performs a GET request against the /mailboxes/{id}/list/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyMailboxes: The parsed response data.
        """
        return self._parse_many(
            CompanyMailboxes,
            super()._make_request("GET", data=data, params=params).json().get('mailboxes', {}),
        )

    def put(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> CompanyMailboxesPutResponse:
        """
        Performs a PUT request against the /company/{id}/list/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyMailboxesPutResponse: The parsed response data.
        """
        return self._parse_one(
            CompanyMailboxesPutResponse,
            super()._make_request("PUT", data=data, params=params).json(),
        )
