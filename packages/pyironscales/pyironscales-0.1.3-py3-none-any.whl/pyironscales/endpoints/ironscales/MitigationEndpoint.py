from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.endpoints.ironscales.MitigationIdEndpoint import MitigationIdEndpoint


class MitigationEndpoint(
    IronscalesEndpoint,
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "mitigations", parent_endpoint=parent_endpoint)

    def id(self, id: int) -> MitigationIdEndpoint:
        """
        Sets the ID for this endpoint and returns an initialized MitigationIdEndpoint object to move down the chain.

        Parameters:
            id (int): The ID to set.
        Returns:
            MitigationIdEndpoint: The initialized MitigationIdEndpoint object.
        """
        child = MitigationIdEndpoint(self.client, parent_endpoint=self)
        child._id = id
        return child
