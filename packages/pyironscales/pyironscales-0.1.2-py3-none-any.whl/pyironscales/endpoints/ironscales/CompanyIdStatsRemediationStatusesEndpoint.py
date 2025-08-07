from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint

from pyironscales.interfaces import (
    IGettable,
)
from pyironscales.models.ironscales import CompanyStatsRemediationStatuses
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class CompanyIdStatsRemediationStatusesEndpoint(
    IronscalesEndpoint,
    IGettable[CompanyStatsRemediationStatuses, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "remediation-statuses/", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, CompanyStatsRemediationStatuses)

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> CompanyStatsRemediationStatuses:
        """
        Performs a GET request against the /company/{id}/stats/remediation-statuses/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyStatsRemediationStatuses: The parsed response data.
        """
        return self._parse_one(
            CompanyStatsRemediationStatuses,
            super()._make_request("GET", data=data, params=params).json(),
        )
