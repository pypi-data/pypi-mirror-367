from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.endpoints.ironscales.MitigationsIdImpersonationDetailsEndpoint import MitigationsIdImpersonationDetailsEndpoint

class MitigationsIdImpersonationEndpoint(
    IronscalesEndpoint,
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "impersonation", parent_endpoint=parent_endpoint)
        self.details = self._register_child_endpoint(MitigationsIdImpersonationDetailsEndpoint(client, parent_endpoint=self))
