from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IGettable,
)
from pyironscales.models.ironscales import CompanyEmailStatistics
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)

class MitigationsIdStatsEmailsEndpoint(
    IronscalesEndpoint,
    IGettable[CompanyEmailStatistics, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "emails/", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, CompanyEmailStatistics)

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> CompanyEmailStatistics:
        """
        Performs a GET request against the /mitigations/{id}/stats/emails/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyMitigationStatistics: The parsed response data.
        """
        return self._parse_one(
            CompanyEmailStatistics,
            super()._make_request("GET", data=data, params=params).json(),
        )
