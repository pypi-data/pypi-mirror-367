from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.endpoints.ironscales.PlanDetailsDomainsIdEndpoint import PlanDetailsDomainsIdEndpoint

class CompanyListEndpoint(
    IronscalesEndpoint,
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "list", parent_endpoint=parent_endpoint)

    def id(self, id: int) -> PlanDetailsDomainsIdEndpoint:
        """
        Sets the ID for this endpoint and returns an initialized PlanDetailsDomainsIdEndpoint object to move down the chain.

        Parameters:
            id (int): The ID to set.
        Returns:
            PlanDetailsDomainsIdEndpoint: The initialized PlanDetailsDomainsIdEndpoint object.
        """
        child = PlanDetailsDomainsIdEndpoint(self.client, parent_endpoint=self)
        child._id = id
        return child
