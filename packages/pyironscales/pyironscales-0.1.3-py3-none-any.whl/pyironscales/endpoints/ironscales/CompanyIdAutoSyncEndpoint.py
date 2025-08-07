from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.endpoints.ironscales.CompanyIdAutoSyncGroupsEndpoint import CompanyIdAutoSyncGroupsEndpoint
from pyironscales.endpoints.ironscales.CompanyIdAutoSyncMailboxesEndpoint import CompanyIdAutoSyncMailboxesEndpoint
from pyironscales.interfaces import (
    IGettable,
    IPostable,
    IDeleteable
)
from pyironscales.models.ironscales import CompanyAutoSyncStatus
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class CompanyIdAutoSyncEndpoint(
    IronscalesEndpoint,
    IGettable[CompanyAutoSyncStatus, IronscalesRequestParams],
    IPostable[CompanyAutoSyncStatus, IronscalesRequestParams],
    IDeleteable[IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "auto-sync/", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, CompanyAutoSyncStatus)
        IPostable.__init__(self, CompanyAutoSyncStatus)
        IDeleteable.__init__(self, CompanyAutoSyncStatus)
        self.groups = self._register_child_endpoint(CompanyIdAutoSyncGroupsEndpoint(client, parent_endpoint=self))
        self.mailboxes = self._register_child_endpoint(CompanyIdAutoSyncMailboxesEndpoint(client, parent_endpoint=self))

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> CompanyAutoSyncStatus:
        """
        Performs a GET request against the /company/{id}/auto-sync/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyAutoSyncStatus: The parsed response data.
        """
        return self._parse_one(
            CompanyAutoSyncStatus,
            super()._make_request("GET", data=data, params=params).json(),
        )

    def post(self, data: JSON | None = None, params: IronscalesRequestParams | None = None) -> CompanyAutoSyncStatus:
        """
        Performs a POST request against the /company/{id}/auto-sync/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyAutoSyncStatus: The parsed Company data.
        """
        return self._parse_one(CompanyAutoSyncStatus, super()._make_request("POST", data=data, params=params).json())

    def delete(self, data: JSON | None = None, params: IronscalesRequestParams | None = None) -> CompanyAutoSyncStatus:
        """
        Performs a DELETE request against the /company/{id}/auto-sync/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyAutoSyncStatus: The parsed response data.
        """
        return self._parse_one(CompanyAutoSyncStatus, super()._make_request("DELETE", data=data, params=params).json())
