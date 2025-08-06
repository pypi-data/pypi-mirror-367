from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.endpoints.ironscales.IncidentIdDetailsIdEndpoint import IncidentIdDetailsIdEndpoint


class IncidentIdDetailsEndpoint(
    IronscalesEndpoint,
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "details", parent_endpoint=parent_endpoint)

    def id(self, id: int) -> IncidentIdDetailsIdEndpoint:
        """
        Sets the ID for this endpoint and returns an initialized IncidentIdDetailsIdEndpoint object to move down the chain.

        Parameters:
            id (int): The ID to set.
        Returns:
            IncidentIdDetailsIdEndpoint: The initialized IncidentIdDetailsIdEndpoint object.
        """
        child = IncidentIdDetailsIdEndpoint(self.client, parent_endpoint=self)
        child._id = id
        return child
