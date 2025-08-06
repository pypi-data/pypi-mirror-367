from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.endpoints.ironscales.CompanyIdEndpoint import CompanyIdEndpoint
from pyironscales.endpoints.ironscales.CompanyCreateEndpoint import CompanyCreateEndpoint
from pyironscales.endpoints.ironscales.CompanyListEndpoint import CompanyListEndpoint


class CompanyEndpoint(
    IronscalesEndpoint,
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "company", parent_endpoint=parent_endpoint)
        self.create = self._register_child_endpoint(CompanyCreateEndpoint(client, parent_endpoint=self))
        self.list = self._register_child_endpoint(CompanyListEndpoint(client, parent_endpoint=self))

    def id(self, id: int) -> CompanyIdEndpoint:
        """
        Sets the ID for this endpoint and returns an initialized CompanyIdEndpoint object to move down the chain.

        Parameters:
            id (int): The ID to set.
        Returns:
            CompanyIdEndpoint: The initialized CompanyIdEndpoint object.
        """
        child = CompanyIdEndpoint(self.client, parent_endpoint=self)
        child._id = id
        return child
