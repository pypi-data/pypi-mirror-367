from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.models.ironscales import Answer
from pyironscales.endpoints.ironscales.CampaignsIdDetailsEndpoint import CampaignsIdDetailsEndpoint
from pyironscales.endpoints.ironscales.CampaignsIdParticipantDetailsEndpoint import CampaignsIdParticipantDetailsEndpoint
from pyironscales.types import (
    JSON,
    IronscalesRequestParams,
)


class CampaignsIdEndpoint(
    IronscalesEndpoint,
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "{id}", parent_endpoint=parent_endpoint)
        self.search = self._register_child_endpoint(CampaignsIdDetailsEndpoint(client, parent_endpoint=self))
        self.search = self._register_child_endpoint(CampaignsIdParticipantDetailsEndpoint(client, parent_endpoint=self))
