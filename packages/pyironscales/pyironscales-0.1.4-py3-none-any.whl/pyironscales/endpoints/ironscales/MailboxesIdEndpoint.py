from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.endpoints.ironscales.MailboxesIdComplianceReportEndpoint import MailboxesIdComplianceReportEndpoint
from pyironscales.endpoints.ironscales.MailboxesIdListEndpoint import MailboxesIdListEndpoint
from pyironscales.endpoints.ironscales.MailboxesIdUserCampaignsPerformanceEndpoint import MailboxesIdUserCampaignsPerformanceEndpoint

class MailboxesIdEndpoint(
    IronscalesEndpoint,
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "{id}", parent_endpoint=parent_endpoint)
        self.compliance_report = self._register_child_endpoint(MailboxesIdComplianceReportEndpoint(client, parent_endpoint=self))
        self.list = self._register_child_endpoint(MailboxesIdListEndpoint(client, parent_endpoint=self))
        self.user_campaigns_performance = self._register_child_endpoint(MailboxesIdUserCampaignsPerformanceEndpoint(client, parent_endpoint=self))
