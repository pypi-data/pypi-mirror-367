from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.endpoints.ironscales.IncidentIdClassifyIdEndpoint import IncidentIdClassifyIdEndpoint


class IncidentIdClassifyEndpoint(
    IronscalesEndpoint,
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "classify", parent_endpoint=parent_endpoint)

    def id(self, id: int) -> IncidentIdClassifyIdEndpoint:
        """
        Sets the ID for this endpoint and returns an initialized IncidentIdClassifyIdEndpoint object to move down the chain.

        Parameters:
            id (int): The ID to set.
        Returns:
            IncidentIdClassifyIdEndpoint: The initialized IncidentIdClassifyIdEndpoint object.
        """
        child = IncidentIdClassifyIdEndpoint(self.client, parent_endpoint=self)
        child._id = id
        return child
