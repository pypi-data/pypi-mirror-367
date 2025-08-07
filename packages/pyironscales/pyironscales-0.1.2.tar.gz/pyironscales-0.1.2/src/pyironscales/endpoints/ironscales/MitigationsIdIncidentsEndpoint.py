from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.endpoints.ironscales.MitigationsIdIncidentsDetailsEndpoint import MitigationsIdIncidentsDetailsEndpoint

class MitigationsIdIncidentsEndpoint(
    IronscalesEndpoint,
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "incidents", parent_endpoint=parent_endpoint)
        self.details = self._register_child_endpoint(MitigationsIdIncidentsDetailsEndpoint(client, parent_endpoint=self))
