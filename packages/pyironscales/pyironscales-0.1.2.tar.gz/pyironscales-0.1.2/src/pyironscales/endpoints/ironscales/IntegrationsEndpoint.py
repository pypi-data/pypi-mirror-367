from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.endpoints.ironscales.IntegrationsIdEndpoint import IntegrationsIdEndpoint


class IntegrationsEndpoint(
    IronscalesEndpoint,
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "integrations", parent_endpoint=parent_endpoint)

    def id(self, id: int) -> IntegrationsIdEndpoint:
        """
        Sets the ID for this endpoint and returns an initialized IntegrationsIdEndpoint object to move down the chain.

        Parameters:
            id (int): The ID to set.
        Returns:
            IntegrationsIdEndpoint: The initialized IntegrationsIdEndpoint object.
        """
        child = IntegrationsIdEndpoint(self.client, parent_endpoint=self)
        child._id = id
        return child
