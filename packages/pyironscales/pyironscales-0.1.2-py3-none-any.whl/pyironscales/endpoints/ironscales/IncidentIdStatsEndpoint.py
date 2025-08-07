from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.endpoints.ironscales.IncidentIdStatsRemediationStatusesEndpoint import IncidentIdStatsRemediationStatusesEndpoint


class IncidentIdStatsEndpoint(
    IronscalesEndpoint,
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "stats", parent_endpoint=parent_endpoint)
        self.remediation_statuses = self._register_child_endpoint(IncidentIdStatsRemediationStatusesEndpoint(client, parent_endpoint=self))
