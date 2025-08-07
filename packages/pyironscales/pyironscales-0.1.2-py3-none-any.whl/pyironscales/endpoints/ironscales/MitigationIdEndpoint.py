from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.endpoints.ironscales.MitigationsIdDetailsEndpoint import MitigationsIdDetailsEndpoint
from pyironscales.endpoints.ironscales.MitigationsIdImpersonationEndpoint import MitigationsIdImpersonationEndpoint
from pyironscales.endpoints.ironscales.MitigationsIdIncidentsEndpoint import MitigationsIdIncidentsEndpoint
from pyironscales.endpoints.ironscales.MitigationsIdStatsEndpoint import MitigationsIdStatsEndpoint

class MitigationIdEndpoint(
    IronscalesEndpoint,
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "{id}", parent_endpoint=parent_endpoint)
        self.details = self._register_child_endpoint(MitigationsIdDetailsEndpoint(client, parent_endpoint=self))
        self.impersonation = self._register_child_endpoint(MitigationsIdImpersonationEndpoint(client, parent_endpoint=self))
        self.incidents = self._register_child_endpoint(MitigationsIdIncidentsEndpoint(client, parent_endpoint=self))
        self.stats = self._register_child_endpoint(MitigationsIdStatsEndpoint(client, parent_endpoint=self))
