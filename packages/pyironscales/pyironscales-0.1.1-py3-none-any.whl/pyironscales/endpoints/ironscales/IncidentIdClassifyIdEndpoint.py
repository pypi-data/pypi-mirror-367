from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IPostable,
)
from pyironscales.models.ironscales import IncidentClassify
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class IncidentIdClassifyIdEndpoint(
    IronscalesEndpoint,
    IPostable[IncidentClassify, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "{id}", parent_endpoint=parent_endpoint)
        IPostable.__init__(self, IncidentClassify)

    def post(self, data: JSON | None = None, params: IronscalesRequestParams | None = None) -> IncidentClassify:
        """
        Performs a POST request against the /incident/{id}/classify/{id} endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            IncidentClassify: The parsed Company data.
        """
        return self._parse_one(IncidentClassify, super()._make_request("POST", data=data, params=params).json())
