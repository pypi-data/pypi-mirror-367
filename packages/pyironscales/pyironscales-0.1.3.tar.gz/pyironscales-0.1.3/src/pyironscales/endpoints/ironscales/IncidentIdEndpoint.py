from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.endpoints.ironscales.IncidentIdClassifyEndpoint import IncidentIdClassifyEndpoint
from pyironscales.endpoints.ironscales.IncidentIdDetailsEndpoint import IncidentIdDetailsEndpoint
from pyironscales.endpoints.ironscales.IncidentIdListEndpoint import IncidentIdListEndpoint
from pyironscales.endpoints.ironscales.IncidentIdScanbackListEndpoint import IncidentIdScanbackListEndpoint
from pyironscales.endpoints.ironscales.IncidentIdStatsEndpoint import IncidentIdStatsEndpoint
from pyironscales.endpoints.ironscales.IncidentIdStatusEndpoint import IncidentIdStatusEndpoint

class IncidentIdEndpoint(
    IronscalesEndpoint,
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "{id}", parent_endpoint=parent_endpoint)
        self.classify = self._register_child_endpoint(IncidentIdClassifyEndpoint(client, parent_endpoint=self))
        self.details = self._register_child_endpoint(IncidentIdDetailsEndpoint(client, parent_endpoint=self))
        self.list = self._register_child_endpoint(IncidentIdListEndpoint(client, parent_endpoint=self))
        self.scanback_list = self._register_child_endpoint(IncidentIdScanbackListEndpoint(client, parent_endpoint=self))
        self.stats = self._register_child_endpoint(IncidentIdStatsEndpoint(client, parent_endpoint=self))

    def id(self, id: int) -> IncidentIdStatusEndpoint:
        """
        Sets the ID for this endpoint and returns an initialized IncidentIdStatusEndpoint object to move down the chain.

        Parameters:
            id (int): The ID to set.
        Returns:
            IncidentIdStatusEndpoint: The initialized IncidentIdStatusEndpoint object.
        """
        child = IncidentIdStatusEndpoint(self.client, parent_endpoint=self)
        child._id = id
        return child
