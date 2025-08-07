from pyironscales.endpoints.base.base_endpoint import IronscalesEndpoint
from pyironscales.endpoints.ironscales.IntegrationsIdIntegrationStatusEndpoint import IntegrationsIdIntegrationStatusEndpoint
from pyironscales.endpoints.ironscales.IntegrationsIdDisableIntegrationEndpoint import IntegrationsIdDisableIntegrationEndpoint
from pyironscales.endpoints.ironscales.IntegrationsIdGWSAuthorizeEndpoint import IntegrationsIdGWSAuthorizeEndpoint
from pyironscales.endpoints.ironscales.IntegrationsIdGWSConsentRedirectURIEndpoint import IntegrationsIdGWSConsentRedirectURIEndpoint
from pyironscales.endpoints.ironscales.IntegrationsIdO365AuthorizeEndpoint import IntegrationsIdO365AuthorizeEndpoint
from pyironscales.endpoints.ironscales.IntegrationsIdO365ConsentRedirectURIEndpoint import IntegrationsIdO365ConsentRedirectURIEndpoint

class IntegrationsIdEndpoint(
    IronscalesEndpoint,
):
    def __init__(self, client, parent_endpoint=None) -> None:
        IronscalesEndpoint.__init__(self, client, "{id}", parent_endpoint=parent_endpoint)
        self.integration_status = self._register_child_endpoint(IntegrationsIdIntegrationStatusEndpoint(client, parent_endpoint=self))
        self.disable_integration = self._register_child_endpoint(IntegrationsIdDisableIntegrationEndpoint(client, parent_endpoint=self))
        self.gws_authorize_endpoint = self._register_child_endpoint(IntegrationsIdGWSAuthorizeEndpoint(client, parent_endpoint=self))
        self.gws_consent_redirect_uri = self._register_child_endpoint(IntegrationsIdGWSConsentRedirectURIEndpoint(client, parent_endpoint=self))
        self.o365_authorize = self._register_child_endpoint(IntegrationsIdO365AuthorizeEndpoint(client, parent_endpoint=self))
        self.o365_consent_redirect_uri = self._register_child_endpoint(IntegrationsIdO365ConsentRedirectURIEndpoint(client, parent_endpoint=self))
