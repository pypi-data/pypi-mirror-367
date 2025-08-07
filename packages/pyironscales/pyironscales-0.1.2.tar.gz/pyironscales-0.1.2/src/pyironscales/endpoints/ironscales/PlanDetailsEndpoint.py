from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.endpoints.ironscales.PlanDetailsIdEndpoint import PlanDetailsIdEndpoint


class PlanDetailsEndpoint(
    IronscalesEndpoint,
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "plan-details", parent_endpoint=parent_endpoint)

    def id(self, id: int) -> PlanDetailsIdEndpoint:
        """
        Sets the ID for this endpoint and returns an initialized PlanDetailsIdEndpoint object to move down the chain.

        Parameters:
            id (int): The ID to set.
        Returns:
            PlanDetailsIdEndpoint: The initialized PlanDetailsIdEndpoint object.
        """
        child = PlanDetailsIdEndpoint(self.client, parent_endpoint=self)
        child._id = id
        return child
