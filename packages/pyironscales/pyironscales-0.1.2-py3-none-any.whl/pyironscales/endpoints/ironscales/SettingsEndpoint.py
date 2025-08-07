from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.endpoints.ironscales.SettingsIdEndpoint import SettingsIdEndpoint


class SettingsEndpoint(
    IronscalesEndpoint,
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "settings", parent_endpoint=parent_endpoint)

    def id(self, id: int) -> SettingsIdEndpoint:
        """
        Sets the ID for this endpoint and returns an initialized SettingsIdEndpoint object to move down the chain.

        Parameters:
            id (int): The ID to set.
        Returns:
            SettingsIdEndpoint: The initialized SettingsIdEndpoint object.
        """
        child = SettingsIdEndpoint(self.client, parent_endpoint=self)
        child._id = id
        return child
