from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IGettable,
    IPuttable,
    IDeleteable,
)
from pyironscales.models.ironscales import CompanyLicensedDomains, CompanyLicensedDomainsPutResponse
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class PlanDetailsDomainsIdEndpoint(
    IronscalesEndpoint,
    IGettable[CompanyLicensedDomains, IronscalesRequestParams],
    IPuttable[CompanyLicensedDomains, IronscalesRequestParams],
    IDeleteable[IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "{id}/", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, CompanyLicensedDomains)

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> CompanyLicensedDomains:
        """
        Performs a GET request against the /plan-details/domains/{id}/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyLicensedDomains: The parsed response data.
        """
        return self._parse_one(
            CompanyLicensedDomains,
            super()._make_request("GET", data=data, params=params).json(),
        )

    def post(self, data: JSON | None = None, params: IronscalesRequestParams | None = None) -> CompanyLicensedDomainsPutResponse:
        """
        Performs a POST request against the /plan-details/domains/{id}/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyLicensedDomainsPutResponse: The parsed Company data.
        """
        return self._parse_one(CompanyLicensedDomainsPutResponse, super()._make_request("POST", data=data, params=params).json())

    def delete(self, data: JSON | None = None, params: IronscalesRequestParams | None = None) -> CompanyLicensedDomains:
        """
        Performs a DELETE request against the /plan-details/domains/{id}/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            CompanyLicensedDomains: The parsed response data.
        """
        return self._parse_one(CompanyLicensedDomains, super()._make_request("DELETE", data=data, params=params).json())
