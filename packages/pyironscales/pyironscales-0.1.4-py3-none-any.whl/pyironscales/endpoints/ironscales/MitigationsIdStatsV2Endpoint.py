from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IGettable,
)
from pyironscales.models.ironscales import CompanyMitigationStatisticsV2
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)

class MitigationsIdStatsV2Endpoint(
    IronscalesEndpoint,
    IGettable[CompanyMitigationStatisticsV2, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "v2/", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, CompanyMitigationStatisticsV2)

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> CompanyMitigationStatisticsV2:
        """
        Performs a GET request against the /mitigations/{id}/stats/v2/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyMitigationStatisticsV2: The parsed response data.
        """
        return self._parse_one(
            CompanyMitigationStatisticsV2,
            super()._make_request("GET", data=data, params=params).json(),
        )
