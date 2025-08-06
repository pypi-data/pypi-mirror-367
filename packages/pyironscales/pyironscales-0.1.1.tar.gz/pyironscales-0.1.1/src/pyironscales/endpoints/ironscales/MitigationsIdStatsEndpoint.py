from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.endpoints.ironscales.MitigationsIdStatsEmailsEndpoint import MitigationsIdStatsEmailsEndpoint
from pyironscales.endpoints.ironscales.MitigationsIdStatsMostTargetedDepartmentsEndpoint import MitigationsIdStatsMostTargetedDepartmentsEndpoint
from pyironscales.endpoints.ironscales.MitigationsIdStatsMostTargetedEmployeesEndpoint import MitigationsIdStatsMostTargetedEmployeesEndpoint
from pyironscales.endpoints.ironscales.MitigationsIdStatsV2Endpoint import MitigationsIdStatsV2Endpoint
from pyironscales.interfaces import (
    IGettable,
)
from pyironscales.models.ironscales import CompanyMitigationStatistics
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)

class MitigationsIdStatsEndpoint(
    IronscalesEndpoint,
    IGettable[CompanyMitigationStatistics, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "stats/", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, CompanyMitigationStatistics)
        self.emails = self._register_child_endpoint(MitigationsIdStatsEmailsEndpoint(client, parent_endpoint=self))
        self.most_targeted_departments = self._register_child_endpoint(MitigationsIdStatsMostTargetedDepartmentsEndpoint(client, parent_endpoint=self))
        self.most_targeted_employees = self._register_child_endpoint(MitigationsIdStatsMostTargetedEmployeesEndpoint(client, parent_endpoint=self))
        self.v2 = self._register_child_endpoint(MitigationsIdStatsV2Endpoint(client, parent_endpoint=self))

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> CompanyMitigationStatistics:
        """
        Performs a GET request against the /mitigations/{id}/stats/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyMitigationStatistics: The parsed response data.
        """
        return self._parse_one(
            CompanyMitigationStatistics,
            super()._make_request("GET", data=data, params=params).json(),
        )
