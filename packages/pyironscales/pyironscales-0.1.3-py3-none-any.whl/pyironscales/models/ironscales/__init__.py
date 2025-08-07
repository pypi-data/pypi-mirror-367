from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from pyironscales.models.base.base_model import IronscalesModel

class Pagination(IronscalesModel):
    current_page: int | None = Field(default=None, alias="CurrentPage")
    current_page_count: int | None = Field(default=None, alias="CurrentPageCount")
    limit: int | None = Field(default=None, alias="Limit")
    total_count: int | None = Field(default=None, alias="TotalCount")
    next_page: int | None = Field(default=None, alias="NextPage")
    next_page_url: str | None = Field(default=None, alias="NextPageURL")
    next_page_token: str | None = Field(default=None, alias="NextPageToken")
    
class Campaigns(IronscalesModel):
    campaignID: int | None = Field(default=None, alias="CampaignId")
    campaignName: str | None = Field(default=None, alias="CampaignName")
    campaignStatus: str | None = Field(default=None, alias="CampaignStatus")
    flowType: str | None = Field(default=None, alias="FlowType")
    language: str | None = Field(default=None, alias="Language")
    maxEmailPerDay: int | None = Field(default=None, alias="MaxEmailPerDay")
    endDate: datetime | None = Field(default=None, alias="Modified")
    launchDate: datetime | None = Field(default=None, alias="Modified")
    emailsSent: int | None = Field(default=None, alias="EmailsSent")
    participants: int | None = Field(default=None, alias="Participants")
    emailsBounced: int | None = Field(default=None, alias="EmailsBounced")
    numberOfClickedParticipants: int | None = Field(default=None, alias="NumberOfClickedParticipants")
    numberOfTrainedParticipants: int | None = Field(default=None, alias="NumberOfTrainedParticipants")
    numberOfTrainedParticipatns: int | None = Field(default=None, alias="NumberOfTrainedParticipatns") #Seems ironscales had a type and for some reason continued to include it alongside the fixed string
    numberOfReportedParticipants: int | None = Field(default=None, alias="NumberOfReportedParticipants")
    numberOfReadParticipants: int | None = Field(default=None, alias="NumberOfReadParticipants")
    numberOfDeleted: int | None = Field(default=None, alias="NumberOfDeleted")
    attackReadinessFirstReport: str | None = Field(default=None, alias="AttackReadinessFirstReport")
    attackReadinessMitigationTime: str | None = Field(default=None, alias="AttackReadinessMitigationTime")
    attackReadinessLuredBeforeMitigation: str | None = Field(default=None, alias="AttackReadinessLuredBeforeMitigation")
    attackReadinessReportsToMitigate: str | None = Field(default=None, alias="AttackReadinessReportsToMitigate")
    companyId: int | None = Field(default=None, alias="CompanyId")
    randomized: bool | None = Field(default=None, alias="Randomized")

class CampaignParticipants(IronscalesModel):
    internalID: int | None = Field(default=None, alias="InternalID")
    name: str | None = Field(default=None, alias="Name")
    displayName: str | None = Field(default=None, alias="DisplayName")
    lastUpdate: datetime | None = Field(default=None, alias="LastUpdate")
    title: str | None = Field(default=None, alias="Title")
    department: str | None = Field(default=None, alias="Department")
    company: str | None = Field(default=None, alias="Company")
    manager: str | None = Field(default=None, alias="Manager")
    office: str | None = Field(default=None, alias="Office")
    country: str | None = Field(default=None, alias="Country")
    city: str | None = Field(default=None, alias="City")
    sentAt: datetime | None = Field(default=None, alias="SentAt")
    opened: str | None = Field(default=None, alias="Opened")
    openedAt: datetime | None = Field(default=None, alias="OpenedAt")
    enteredDetails: str | None = Field(default=None, alias="EnteredDetails")
    trainingModule: str | None = Field(default=None, alias="TrainingModule")
    trainingVideoStarted: str | None = Field(default=None, alias="TrainingVideoStarted")
    awarenessLevel: str | None = Field(default=None, alias="AwarenessLevel")
    customTags: str | None = Field(default=None, alias="CustomTags")
    reported: str | None = Field(default=None, alias="Reported")
    reportedTime: datetime | None = Field(default=None, alias="ReportedTime")
    read: str | None = Field(default=None, alias="Read")
    clicked: str | None = Field(default=None, alias="Clicked")
    clickedTime: datetime | None = Field(default=None, alias="ClickedTime")
    resendTrainingDates: list[datetime] | None = Field(default=None, alias="ResendTrainingDates")
    deleted: str | None = Field(default=None, alias="Deleted")
    trained: str | None = Field(default=None, alias="Trained")
    trainingCompletionDate: datetime | None = Field(default=None, alias="TrainingCompletionDate")
    trainingScore: int | None = Field(default=None, alias="TrainingScore")
    trainingDuration: int | None = Field(default=None, alias="TrainingDuration")
    trainingStartedOn: datetime | None = Field(default=None, alias="TrainingStartedOn")
    email: str | None = Field(default=None, alias="Email")
    template: str | None = Field(default=None, alias="Template")
    userIp: str | None = Field(default=None, alias="UserIp")

class PartnerCompany(IronscalesModel):
    id: int | None = Field(default=None, alias="Id")
    name: str | None = Field(default=None, alias="Name")
    domain: str | None = Field(default=None, alias="Domain")
    ownerEmail: str | None = Field(default=None, alias="OwnerEmail")
    ownerName: str | None = Field(default=None, alias="OwnerName")
    country: str | None = Field(default=None, alias="Country")
    registrationDate: datetime | None = Field(default=None, alias="RegistrationDate")
    partner_id: int | None = Field(default=None, alias="PartnerID")

class PartnerCompanyV2(IronscalesModel):
    id: int | None = Field(default=None, alias="Id")
    name: str | None = Field(default=None, alias="Name")
    domain: str | None = Field(default=None, alias="Domain")
    ownerEmail: str | None = Field(default=None, alias="OwnerEmail")
    ownerName: str | None = Field(default=None, alias="OwnerName")
    country: str | None = Field(default=None, alias="Country")
    registrationDate: datetime | None = Field(default=None, alias="RegistrationDate")
    partner_id: int | None = Field(default=None, alias="PartnerID")
    planExpirationDate: datetime | None = Field(default=None, alias="PlanExpirationDate")
    trialPlanExpirationDate: datetime | None = Field(default=None, alias="TrialPlanExpirationDate")
    
class CompanyAutoSyncStatus(IronscalesModel):
    in_progress: bool | None = Field(default=None, alias="InProgress")
    mailboxes_total_count: int | None = Field(default=None, alias="MailboxesTotalCount")
    protected_mailboxes_count: int | None = Field(default=None, alias="ProtectedMailboxesCount")
    enabled_mailboxes_count: int | None = Field(default=None, alias="EnabledMailboxesCount")
    synced_mailboxes_count: int | None = Field(default=None, alias="SyncedMailboxesCount")
    failed_mailboxes_count: int | None = Field(default=None, alias="FailedMailboxesCount")
    last_synced_at: datetime | None = Field(default=None, alias="LastSyncedAt")

class Company911Email(IronscalesModel):
    email: str | None = Field(default=None, alias="Email")

class CompanyAutoSyncGroups(IronscalesModel):
    id: str | None = Field(default=None, alias="Id")
    display_name: str | None = Field(default=None, alias="DisplayName")
    
class CompanyManifest(IronscalesModel):
    report_button: str | None = Field(default=None, alias="ReportButton")
    add_in_description: str | None = Field(default=None, alias="AddInDescription")
    report_phishing_caption: str | None = Field(default=None, alias="ReportPhishingCaption")
    provider_name: str | None = Field(default=None, alias="ProviderName")
    logo: str | None = Field(default=None, alias="Logo")
    
class CompanySyncedEmails(IronscalesModel):
    first_name: str | None = Field(default=None, alias="FirstName")
    last_name: str | None = Field(default=None, alias="LastName")
    email: str | None = Field(default=None, alias="Email")
    change_date: datetime | None = Field(default=None, alias="ChangeDate")
    
class CompanyFeaturesStates(IronscalesModel):
    silentMode: bool | None = Field(default=None, alias="SilentMode")
    silentModeMsg: bool | None = Field(default=None, alias="SilentModeMsg")
    ato: bool | None = Field(default=None, alias="ATO")
    serviceManagement: bool | None = Field(default=None, alias="ServiceManagement")
    trainingCampaignsWizer: bool | None = Field(default=None, alias="TrainingCampaignsWizer")
    api: bool | None = Field(default=None, alias="API")
    themisCoPilot: bool | None = Field(default=None, alias="ThemisCoPilot")
    attachmentsScan: bool | None = Field(default=None, alias="AttachmentsScan")
    linksScan: bool | None = Field(default=None, alias="LinksScan")
    STbundle: bool | None = Field(default=None, alias="STBundle")
    SATBundlePlus: bool | None = Field(default=None, alias="SATBundlePlus")
    AiEmpowerBundle: bool | None = Field(default=None, alias="AiEmpowerBundle")
    autopilotEnabled: bool | None = Field(default=None, alias="AutopilotEnabled")

class CompanyStatisticsAndLicense(IronscalesModel):
    openIncidentCount: int | None = Field(default=None, alias="OpenIncidentCount")
    highPriorityIncidentCount: int | None = Field(default=None, alias="highPriorityIncidentCount")
    mediumPriorityIncidentCount: int | None = Field(default=None, alias="mediumPriorityIncidentCount")
    lowPriorityIncidentCount: int | None = Field(default=None, alias="lowPriorityIncidentCount")
    activeAttacksCount: int | None = Field(default=None, alias="activeAttacksCount")
    license: dict[str, Any] | None = Field(default=None, alias="license")
    protectedMailboxes: bool | None = Field(default=None, alias="protectedMailboxes")
    activeMailboxes: bool | None = Field(default=None, alias="activeMailboxes")
    lastMailboxSyncDate: datetime | None = Field(default=None, alias="lastMailboxSyncDate")

class EscalatedEmails(IronscalesModel):
    arrival_date: datetime | None = Field(default=None, alias="ArrivalDate")
    incident_id: int | None = Field(default=None, alias="IncidentId")
    subject: str | None = Field(default=None, alias="Subject")
    sender_email: str | None = Field(default=None, alias="SenderEmail")
    recipient_name: str | None = Field(default=None, alias="RecipientName")
    recipient_email: str | None = Field(default=None, alias="RecipientEmail")
    primary_threat_type: str | None = Field(default=None, alias="PrimaryThreatType")
    is_scanback: bool | None = Field(default=None, alias="IsScanback")
    classification: str | None = Field(default=None, alias="Classification")
    incident_state: str | None = Field(default=None, alias="IncidentState")
    resolution: str | None = Field(default=None, alias="Resolution")
    sender_ip: str | None = Field(default=None, alias="SenderIp")
    reported_by: str | None = Field(default=None, alias="ReportedBy")
    mailbox_id: int | None = Field(default=None, alias="MailboxId")
    department: str | None = Field(default=None, alias="Department")
    remediated_time: datetime | None = Field(default=None, alias="RemediatedTime")
    mitigation_id: int | None = Field(default=None, alias="MitigationId")

class IncidentDetails(IronscalesModel):
    company_id: int | None = Field(default=None, alias="CompanyId")
    company_name: str | None = Field(default=None, alias="CompanyName")
    incident_id: int | None = Field(default=None, alias="IncidentId")
    classification: str | None = Field(default=None, alias="Classification")
    first_reported_by: str | None = Field(default=None, alias="FirstReportedBy")
    first_reported_date: datetime | None = Field(default=None, alias="FirstReportedDate")
    affected_mailbox_count: int | None = Field(default=None, alias="AffectedMailboxCount")
    sender_reputation: str | None = Field(default=None, alias="SenderReputation")
    banner_displayed: bool | None = Field(default=None, alias="BannerDisplayed")
    sender_email: str | None = Field(default=None, alias="SenderEmail")
    reply_to: str | None = Field(default=None, alias="ReplyTo")
    spf_result: str | None = Field(default=None, alias="SPFResult")
    sender_is_internal: bool | None = Field(default=None, alias="SenderIsInternal")
    themis_proba: float | None = Field(default=None, alias="ThemisProba")
    themis_verdict: str | None = Field(default=None, alias="ThemisVerdict")
    mail_server: dict[str, str] | None = Field(default=None, alias="MailServer")
    federation: dict[str, int | float] | None = Field(default=None, alias="Federation")
    reports: dict[str, str | dict[str, str]] | None = Field(default=None, alias="Reports")
    links: dict[str, str] | None = Field(default=None, alias="Links")
    attachments: dict[str, str | int] | None = Field(default=None, alias="Attachments")
    original_email_body: str | None = Field(default=None, alias="OriginalEmailBody")
    email_body_text: str | None = Field(default=None, alias="EmailBodyText")
    reported_by_end_user: bool | None = Field(default=None, alias="ReportedByEndUser")
    reporter_name: str | None = Field(default=None, alias="ReporterName")

class Incidents(IronscalesModel):
    incidentID: int | None = Field(default=None, alias="ArrivalDate")
    emailSubject: str | None = Field(default=None, alias="EmailSubject")
    linksCount: int | None = Field(default=None, alias="LinksCount")
    attachmentsCount: int | None = Field(default=None, alias="AttachmentsCount")
    recipientEmail: str | None = Field(default=None, alias="RecipientEmail")
    recipientName: str | None = Field(default=None, alias="RecipientName")
    classification: str | None = Field(default=None, alias="Classification")
    assignee: str | None = Field(default=None, alias="Assignee")
    senderName: str | None = Field(default=None, alias="SenderName")
    senderEmail: str | None = Field(default=None, alias="SenderEmail")
    affectedMailboxesCount: int | None = Field(default=None, alias="AffectedMailboxesCount")
    created: str | None = Field(default=None, alias="Created")
    reportedBy: str | None = Field(default=None, alias="ReportedBy")
    resolvedBy: str | None = Field(default=None, alias="ResolvedBy")
    incidentType: str | None = Field(default=None, alias="IncidentsType")
    commentsCount: int | None = Field(default=None, alias="CommentsCount")
    releaseRequestCount: int | None = Field(default=None, alias="ReleaseRequestCount")
    latestEmailDate: datetime | None = Field(default=None, alias="LatestEmailDate")

class IncidentClassify(IronscalesModel):
    classification: int | None = Field(default=None, alias="Classification")
    prev_classification: str | None = Field(default=None, alias="PrevClassification")
    classifying_user_email: int | None = Field(default=None, alias="ClassifyingUserEmail")

class ScanbackIncidents(IronscalesModel):
    incidentID: int | None = Field(default=None, alias="ArrivalDate")
    emailSubject: str | None = Field(default=None, alias="EmailSubject")
    linksCount: int | None = Field(default=None, alias="LinksCount")
    attachmentsCount: int | None = Field(default=None, alias="AttachmentsCount")
    recipientEmail: str | None = Field(default=None, alias="RecipientEmail")
    recipientName: str | None = Field(default=None, alias="RecipientName")
    classification: str | None = Field(default=None, alias="Classification")
    assignee: str | None = Field(default=None, alias="Assignee")
    senderName: str | None = Field(default=None, alias="SenderName")
    senderEmail: str | None = Field(default=None, alias="SenderEmail")
    affectedMailboxesCount: int | None = Field(default=None, alias="AffectedMailboxesCount")
    created: str | None = Field(default=None, alias="Created")
    reportedBy: str | None = Field(default=None, alias="ReportedBy")
    resolvedBy: str | None = Field(default=None, alias="ResolvedBy")

class RemediationStatusesStats(IronscalesModel):
    phishing: dict[str, int] | None = Field(default=None, alias="Phishing")
    spam: dict[str, int] | None = Field(default=None, alias="Spam")
    safe: dict[str, int] | None = Field(default=None, alias="Safe")
    unclassified: dict[str, int] | None = Field(default=None, alias="Unclassified")

class UnclassifiedIncidentIDs(IronscalesModel):
    incident_ids: list[int] | None = Field(default=None, alias="IncidentIds")

class IntegrationStatus(IronscalesModel):
    company_id: int | None = Field(default=None, alias="CompanyId")
    integration_type: str | None = Field(default=None, alias="IntegrationType")
    is_integrated: bool | None = Field(default=None, alias="IsIntegrated")

class IntegrationO365Authorize(IronscalesModel):
    admin_consent: bool | None = Field(default=None, alias="AdminConsent")
    state: str | None = Field(default=None, alias="State")
    tenant: str | None = Field(default=None, alias="Tenant")
    error: str | None = Field(default=None, alias="Error")
    error_description: str | None = Field(default=None, alias="ErrorDescription")

class IntegrationO365AuthorizeResponse(IronscalesModel):
    additional_data: Any | None = Field(default=None, alias="AdditionalData")
    
class IntegrationGWSAuthorizeResponse(IronscalesModel):
    error_message: Any | None = Field(default=None, alias="AdditionalData")
    
class IntegrationDisableIntegration(IronscalesModel):
    company_id: int | None = Field(default=None, alias="CompanyId")
    integration_type: str | None = Field(default=None, alias="IntegrationType")
    integration_status: str | None = Field(default=None, alias="IntegrationStatus")
    
class IntegrationsGWSConsentRedirectURL(IronscalesModel):
    oauth_full_url: str | None = Field(default=None, alias="OAuthFullUrl")

class IntegrationsO365ConsentRedirectURL(IronscalesModel):
    azure_redirect_uri: str | None = Field(default=None, alias="AzureRedirectURI")
    additional_data: Any | None = Field(default=None, alias="AdditionalData")

class IntegrationsO365ConsentRedirectURLResponse(IronscalesModel):
    oauth_full_url: str | None = Field(default=None, alias="OAuthFullUrl")

class ComplianceReport(IronscalesModel):
    id: int | None = Field(default=None, alias="Id")
    firstName: str | None = Field(default=None, alias="FirstName")
    lastName: str | None = Field(default=None, alias="LastName")
    country: str | None = Field(default=None, alias="Country")
    department: str | None = Field(default=None, alias="Department")
    title: str | None = Field(default=None, alias="Title")
    email: str | None = Field(default=None, alias="Email")
    language: str | None = Field(default=None, alias="Language")
    simulationCampaignsCompletionsCount: int | None = Field(default=None, alias="SimulationCampaignsCompletionsCount")
    lastSimulationCampaignDate: datetime | None = Field(default=None, alias="LastSimulationCampaignDate")
    trainingCampaignsCompletionsCount: int | None = Field(default=None, alias="TrainingCampaignsCompletionCount")
    lastTrainingCampaignDate: datetime | None = Field(default=None, alias="LastTrainingCampaignDate")
    riskLevel: str | None = Field(default=None, alias="RiskLevel")
    awarenessLevel: str | None = Field(default=None, alias="AwarenessLevel")

class CompanyMailboxes(IronscalesModel):
    id: int | None = Field(default=None, alias="Id")
    firstName: str | None = Field(default=None, alias="FirstName")
    lastName: str | None = Field(default=None, alias="LastName")
    title: str | None = Field(default=None, alias="Title")
    department: str | None = Field(default=None, alias="Department")
    email: str | None = Field(default=None, alias="Email")
    phoneNumber: str | None = Field(default=None, alias="PhoneNumber")
    tags: list[str] | None = Field(default=None, alias="Tags")
    language: str | None = Field(default=None, alias="Language")
    enabled: bool | None = Field(default=None, alias="Enabled")
    riskLevel: str | None = Field(default=None, alias="RiskLevel")
    awarenessLevel: str | None = Field(default=None, alias="AwarenessLevel")
    protected: bool | None = Field(default=None, alias="Protected")
    unprotectedReason: str | None = Field(default=None, alias="UnprotectedReason")

class CompanyMailboxesPutResponse(IronscalesModel):
    mailbox_ids: list[int] | None = Field(default=None, alias="MailboxIds")
    error_message: str | None = Field(default=None, alias="ErrorMessage")

class UserCampaignPerformance(IronscalesModel):
    id: int | None = Field(default=None, alias="Id")
    userId: int | None = Field(default=None, alias="UserId")
    firstName: str | None = Field(default=None, alias="FirstName")
    lastName: str | None = Field(default=None, alias="LastName")
    country: str | None = Field(default=None, alias="Country")
    department: str | None = Field(default=None, alias="Department")
    title: str | None = Field(default=None, alias="Title")
    email: str | None = Field(default=None, alias="Email")
    campaignId: int | None = Field(default=None, alias="CampaignId")
    campaignName: str | None = Field(default=None, alias="CampaignName")
    campaignType: str | None = Field(default=None, alias="CampaignType")
    campaignSimulationResult: str | None = Field(default=None, alias="CampaignSimulationResult")
    campaignTrainingStatus: str | None = Field(default=None, alias="CampaignTrainingStatus")
    campaignTrainingName: str | None = Field(default=None, alias="CampaignTrainingName")
    campaignCollectingEndDate: datetime | None = Field(default=None, alias="CampaignCollectingEndDate")
    campaignScore: int | None = Field(default=None, alias="CampaignScore")
    campaignLocale: str | None = Field(default=None, alias="CampaignLocale")
    campaignTemplateName: str | None = Field(default=None, alias="CampaignTemplateName")

class CompanyImpersonationIncidents(IronscalesModel):
    incidentID: int | None = Field(default=None, alias="IncidentId")
    mailboxId: int | None = Field(default=None, alias="MailboxId")
    remediatedTime: datetime | None = Field(default=None, alias="RemediatedTime")
    mailboxEmail: str | None = Field(default=None, alias="MailboxEmail")
    senderEmail: str | None = Field(default=None, alias="SenderEmail")
    subject: str | None = Field(default=None, alias="Subject")
    reportedBy: str | None = Field(default=None, alias="ReportedBy")
    incidentType: str | None = Field(default=None, alias="IncidentType")
    resolution: str | None = Field(default=None, alias="Resolution")
    remediations: int | None = Field(default=None, alias="Remediations")

class CompanyMitigationDetails(IronscalesModel):
    incidentID: int | None = Field(default=None, alias="IncidentId")
    incidentState: int | None = Field(default=None, alias="IncidentState")
    remediatedTime: datetime | None = Field(default=None, alias="RemediatedTime")
    affectedMailboxCount: int | None = Field(default=None, alias="AffectedMailboxCount")
    mailboxId: str | None = Field(default=None, alias="MailboxId")
    mailboxEmail: str | None = Field(default=None, alias="MailboxEmail")
    senderEmail: str | None = Field(default=None, alias="SenderEmail")
    subject: str | None = Field(default=None, alias="Subject")
    threatType: str | None = Field(default=None, alias="ThreatType")
    detectionType: str | None = Field(default=None, alias="DetectionType")
    reportedBy: str | None = Field(default=None, alias="ReportedBy")

class CompanyMitigationDetailsPostResponse(IronscalesModel):
    incidentID: int | None = Field(default=None, alias="IncidentId")
    mitigationID: int | None = Field(default=None, alias="MitigationID")
    incidentState: int | None = Field(default=None, alias="IncidentState")
    remediatedTime: datetime | None = Field(default=None, alias="RemediatedTime")
    mailboxId: str | None = Field(default=None, alias="MailboxId")
    mailboxEmail: str | None = Field(default=None, alias="MailboxEmail")
    subject: str | None = Field(default=None, alias="Subject")
    senderEmail: str | None = Field(default=None, alias="SenderEmail")
    senderIP: str | None = Field(default=None, alias="SenderIP")
    reportedBy: str | None = Field(default=None, alias="ReportedBy")
    resolution: str | None = Field(default=None, alias="Resolution")
    spfResult: str | None = Field(default=None, alias="SPFResult")

class CompanyMitigationStatistics(IronscalesModel):
    openIncidentCount: int | None = Field(default=None, alias="OpenIncidentCount")
    resolvedIncidentCount: int | None = Field(default=None, alias="ResolvedIncidentCount")
    phishingCount: int | None = Field(default=None, alias="PhishingCount")
    remediationCount: int | None = Field(default=None, alias="RemediationCount")
    maliciousAttachmentsCount: int | None = Field(default=None, alias="MaliciousAttachmentsCount")
    maliciousLinksCount: int | None = Field(default=None, alias="MaliciousLinksCount")
    impersonationCount: int | None = Field(default=None, alias="ImpersonationCount")
    reportedByEmployeesCount: int | None = Field(default=None, alias="ReportedByEmployeesCount")

class CompanyEmailStatistics(IronscalesModel):
    inspected_count: int | None = Field(default=None, alias="InspectedCount")
    phishing_count: int | None = Field(default=None, alias="PhishingCount")
    spam_count: int | None = Field(default=None, alias="SpamCount")
    impersonations_count: int | None = Field(default=None, alias="ImpersonationsCount")
    phishing_threat_types: dict[str, int] | None = Field(default=None, alias="PhishingThreatTypes")

class MostTargetedDepartments(IronscalesModel):
    name: int | None = Field(default=None, alias="Name")
    emails_count: int | None = Field(default=None, alias="EmailsCount")

class MostTargetedEmployees(IronscalesModel):
    mailbox: int | None = Field(default=None, alias="Mailbox")
    emails_count: int | None = Field(default=None, alias="EmailsCount")

class CompanyMitigationStatisticsV2(IronscalesModel):
    resolved_by_analyst: dict[str, int | float] | None = Field(default=None, alias="ResolvedByAnalyst")
    inspected_emails: dict[str, int] | None = Field(default=None, alias="InspectedEmails")
    resolved_automatically: dict[str, int | float] | None = Field(default=None, alias="ResolvedAutomatically")
    malicious_content_incidents: dict[str, int] | None = Field(default=None, alias="MaliciousContectIncidents")

class CompanyLicensedDomains(IronscalesModel):
    company_id: int | None = Field(default=None, alias="CompanyId")
    licensed_domains: list[str] | None = Field(default=None, alias="LicensedDomains")

class CompanyLicensedDomainsPutResponse(IronscalesModel):
    company_id: int | None = Field(default=None, alias="CompanyId")
    domains_added: list[str] | None = Field(default=None, alias="DomainsAdded")
    existing_domains: list[str] | None = Field(default=None, alias="ExistingDomains")

class CompanyLicense(IronscalesModel):
    id: int | None = Field(default=None, alias="Id")
    trialExpiration: datetime | None = Field(default=None, alias="TrialExpiration")
    trialPlanType: str | None = Field(default=None, alias="TrialPlanType")
    premiumContentType: str | None = Field(default=None, alias="PremiumContentType")
    planType: str | None = Field(default=None, alias="PlanType")
    planExpiration: str | None = Field(default=None, alias="PlanExpiration")
    mailboxLimit: int | None = Field(default=None, alias="MailboxLimit")
    is_partner: bool | None = Field(default=None, alias="IsPartner")
    testMode: bool | None = Field(default=None, alias="TestMode")

class AccountTakeoverSensitivySettings(IronscalesModel):
    sensitivity: int | None = Field(default=None, alias="Sensitivity")

class AllowListSettings(IronscalesModel):
    allow_list: dict[str, Any] | None = Field(default=None, alias="AllowList")
    internal_active: bool | None = Field(default=None, alias="InternalActive")
    external_active: bool | None = Field(default=None, alias="ExternalActive")

class ChallengedAlerts(IronscalesModel):
    recipients: list[str] | None = Field(default=None, alias="Recipients")

class CompanyNotificationSettings(IronscalesModel):
    recipients: list[str] | None = Field(default=None, alias="Recipients")

