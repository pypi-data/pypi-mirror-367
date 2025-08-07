from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IGettable,
)
from pyironscales.models.ironscales import MostTargetedEmployees
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)

class MitigationsIdStatsMostTargetedEmployeesEndpoint(
    IronscalesEndpoint,
    IGettable[MostTargetedEmployees, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "most-targeted-employees/", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, MostTargetedEmployees)

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> MostTargetedEmployees:
        """
        Performs a GET request against the /mitigations/{id}/stats/most-targeted-employees/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            MostTargetedEmployees: The parsed response data.
        """
        return self._parse_one(
            MostTargetedEmployees,
            super()._make_request("GET", data=data, params=params).json(),
        )
