from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.endpoints.ironscales.CampaignsIdEndpoint import CampaignsIdEndpoint


class CampaignsEndpoint(
    IronscalesEndpoint,
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "campaigns", parent_endpoint=parent_endpoint)

    def id(self, id: int) -> CampaignsIdEndpoint:
        """
        Sets the ID for this endpoint and returns an initialized CampaignsIdEndpoint object to move down the chain.

        Parameters:
            id (int): The ID to set.
        Returns:
            CampaignsIdEndpoint: The initialized CampaignsIdEndpoint object.
        """
        child = CampaignsIdEndpoint(self.client, parent_endpoint=self)
        child._id = id
        return child
