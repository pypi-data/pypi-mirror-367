from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.endpoints.ironscales.MailboxesIdEndpoint import MailboxesIdEndpoint


class MailboxesEndpoint(
    IronscalesEndpoint,
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "mailboxes", parent_endpoint=parent_endpoint)

    def id(self, id: int) -> MailboxesIdEndpoint:
        """
        Sets the ID for this endpoint and returns an initialized MailboxesIdEndpoint object to move down the chain.

        Parameters:
            id (int): The ID to set.
        Returns:
            MailboxesIdEndpoint: The initialized MailboxesIdEndpoint object.
        """
        child = MailboxesIdEndpoint(self.client, parent_endpoint=self)
        child._id = id
        return child
