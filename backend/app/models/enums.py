from enum import Enum

class TicketStatus(str, Enum):
    NEW = "new"
    TRIAGED = "triaged"
    IN_PROGRESS = "in_progress"
    WAITING_ON_CUSTOMER = "waiting_on_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"

class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Category(str, Enum):
    BUG_REPORT = "bug_report"
    BILLING = "billing"
    ACCOUNT_ACCESS = "account_access"
    FEATURE_REQUEST = "feature_request"
    GENERAL = "general"


class ActionType (str, Enum):
    OVERRIDE = "override"
    STATUS_UPDATE = "status_change"



class TicketSource(str, Enum):
    WEB_FORM = "web_form"
    API = "api"
    EMAIL = "email"
    MONITORING = "monitoring"