from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IGettable,
)
from pyironscales.models.ironscales import MostTargetedDepartments
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)

class MitigationsIdStatsMostTargetedDepartmentsEndpoint(
    IronscalesEndpoint,
    IGettable[MostTargetedDepartments, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "most-targeted-departments/", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, MostTargetedDepartments)

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> MostTargetedDepartments:
        """
        Performs a GET request against the /mitigations/{id}/stats/most-targeted-departments/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            MostTargetedDepartments: The parsed response data.
        """
        return self._parse_one(
            MostTargetedDepartments,
            super()._make_request("GET", data=data, params=params).json(),
        )
