from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.endpoints.ironscales.EmailsIdEndpoint import EmailsIdEndpoint


class EmailsEndpoint(
    IronscalesEndpoint,
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "emails", parent_endpoint=parent_endpoint)

    def id(self, id: int) -> EmailsIdEndpoint:
        """
        Sets the ID for this endpoint and returns an initialized EmailsIdEndpoint object to move down the chain.

        Parameters:
            id (int): The ID to set.
        Returns:
            EmailsIdEndpoint: The initialized EmailsIdEndpoint object.
        """
        child = EmailsIdEndpoint(self.client, parent_endpoint=self)
        child._id = id
        return child
