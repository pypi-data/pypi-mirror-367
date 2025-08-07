from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IGettable,
)
from pyironscales.models.ironscales import CompanyAutoSyncGroups
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class CompanyIdAutoSyncGroupsEndpoint(
    IronscalesEndpoint,
    IGettable[CompanyAutoSyncGroups, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "groups/", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, CompanyAutoSyncGroups)

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> CompanyAutoSyncGroups:
        """
        Performs a GET request against the /company/{id}/auto-sync/groups/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyAutoSyncGroups: The parsed response data.
        """
        return self._parse_many(
            CompanyAutoSyncGroups,
            super()._make_request("GET", data=data, params=params).json().get('groups', {}),
        )
