from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.endpoints.ironscales.IncidentIdEndpoint import IncidentIdEndpoint


class IncidentEndpoint(
    IronscalesEndpoint,
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "incident", parent_endpoint=parent_endpoint)

    def id(self, id: int) -> IncidentIdEndpoint:
        """
        Sets the ID for this endpoint and returns an initialized IncidentIdEndpoint object to move down the chain.

        Parameters:
            id (int): The ID to set.
        Returns:
            IncidentIdEndpoint: The initialized IncidentIdEndpoint object.
        """
        child = IncidentIdEndpoint(self.client, parent_endpoint=self)
        child._id = id
        return child
