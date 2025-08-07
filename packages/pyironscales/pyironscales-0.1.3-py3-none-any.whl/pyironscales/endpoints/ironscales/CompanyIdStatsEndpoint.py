from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IGettable,
)
from pyironscales.models.ironscales import CompanyStatisticsAndLicense
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class CompanyIdStatsEndpoint(
    IronscalesEndpoint,
    IGettable[CompanyStatisticsAndLicense, IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "stats/", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, CompanyStatisticsAndLicense)

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> CompanyStatisticsAndLicense:
        """
        Performs a GET request against the /company/{id}/stats/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyStatisticsAndLicense: The parsed response data.
        """
        return self._parse_one(
            CompanyStatisticsAndLicense,
            super()._make_request("GET", data=data, params=params).json(),
        )
