from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IGettable,
)
from pyironscales.models.ironscales import UnclassifiedIncidentIDs
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class IncidentIdStatusEndpoint(
    IronscalesEndpoint,
    IGettable[UnclassifiedIncidentIDs, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "{id}/", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, UnclassifiedIncidentIDs)

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> UnclassifiedIncidentIDs:
        """
        Performs a GET request against the /incident/{id}/{status}/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            UnclassifiedIncidentIDs: The parsed response data.
        """
        return self._parse_one(
            UnclassifiedIncidentIDs,
            super()._make_request("GET", data=data, params=params).json(),
        )
