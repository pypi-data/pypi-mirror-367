from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.interfaces import (
    IGettable,
    IPuttable,
    IDeleteable,
)
from pyironscales.models.ironscales import PartnerCompany
from pyironscales.endpoints.ironscales.CompanyId911EmailEndpoint import CompanyId911EmailEndpoint
from pyironscales.endpoints.ironscales.CompanyIdAutoSyncEndpoint import CompanyIdAutoSyncEndpoint
from pyironscales.endpoints.ironscales.CompanyIdFeaturesEndpoint import CompanyIdFeaturesEndpoint
from pyironscales.endpoints.ironscales.CompanyIdManifestEndpoint import CompanyIdManifestEndpoint
from pyironscales.endpoints.ironscales.CompanyIdStatsEndpoint import CompanyIdStatsEndpoint
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class CompanyIdEndpoint(
    IronscalesEndpoint,
    IGettable[PartnerCompany, IronscalesRequestParams],
    IPuttable[PartnerCompany, IronscalesRequestParams],
    IDeleteable[IronscalesRequestParams],
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "{id}", parent_endpoint=parent_endpoint)
        IGettable.__init__(self, PartnerCompany)
        IPuttable.__init__(self, PartnerCompany)
        IDeleteable.__init__(self, PartnerCompany)
        self._911_email = self._register_child_endpoint(CompanyId911EmailEndpoint(client, parent_endpoint=self))
        self.auto_sync = self._register_child_endpoint(CompanyIdAutoSyncEndpoint(client, parent_endpoint=self))
        self.features = self._register_child_endpoint(CompanyIdFeaturesEndpoint(client, parent_endpoint=self))
        self.manifest = self._register_child_endpoint(CompanyIdManifestEndpoint(client, parent_endpoint=self))
        self.stats = self._register_child_endpoint(CompanyIdStatsEndpoint(client, parent_endpoint=self))

    def get(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> PartnerCompany:
        """
        Performs a GET request against the /company/{id} endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            AuthInformation: The parsed response data.
        """
        return self._parse_one(
            PartnerCompany,
            super()._make_request("GET", data=data, params=params).json(),
        )

    def put(
        self,
        data: JSON | None = None,
        params: IronscalesRequestParams | None = None,
    ) -> PartnerCompany:
        """
        Performs a PUT request against the /company/{id} endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            PartnerCompany: The parsed response data.
        """
        return self._parse_one(
            PartnerCompany,
            super()._make_request("PUT", data=data, params=params).json(),
        )

    def delete(self, data: JSON | None = None, params: IronscalesRequestParams | None = None) -> PartnerCompany:
        """
        Performs a DELETE request against the /company/{id}/ endpoint.

        Parameters:
            data (dict[str, Any]): The data to send in the request body.
            params (dict[str, int | str]): The parameters to send in the request query string.
        Returns:
            PartnerCompany: The parsed response data.
        """
        return self._parse_one(PartnerCompany, super()._make_request("DELETE", data=data, params=params).json())
