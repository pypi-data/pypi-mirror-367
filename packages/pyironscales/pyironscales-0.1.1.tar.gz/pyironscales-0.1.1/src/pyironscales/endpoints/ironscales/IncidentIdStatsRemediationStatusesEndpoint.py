from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IGettable,
)
from pyironscales.models.ironscales import RemediationStatusesStats
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class IncidentIdStatsRemediationStatusesEndpoint(
    IronscalesEndpoint,
    IGettable[RemediationStatusesStats, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "*", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, RemediationStatusesStats)

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> RemediationStatusesStats:
        """
        Performs a GET request against the /incident/{id}/stats/remediation-statuses endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            RemediationStatusesStats: The parsed response data.
        """
        return self._parse_one(
            RemediationStatusesStats,
            super()._make_request("GET", data=data, params=params).json(),
        )
