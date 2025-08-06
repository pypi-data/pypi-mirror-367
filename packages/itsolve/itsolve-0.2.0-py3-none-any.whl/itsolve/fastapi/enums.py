from enum import Enum


class Country(str, Enum):
    RU = "RU"
    BY = "BY"
    ARM = "ARM"
    KZ = "KZ"
    KG = "KG"


class CompanyStatus(str, Enum):
    NOT_VERIFIED = "NOT_VERIFIED"
    REVIEW = "REVIEW"
    VERIFIED = "VERIFIED"


class DocumentStatus(str, Enum):
    NOT_UPLOADED = "NOT_UPLOADED"
    UPLOADED = "UPLOADED"
    REVIEW = "REVIEW"
    ACTIVE = "ACTIVE"


class InternalDocumentKind(str, Enum):
    CERT_REGISTRATION_LEGAL_ENTITY = "CERT_REGISTRATION_LEGAL_ENTITY"
    COMPANY_CHARTER = "COMPANY_CHARTER"
    ORDER_APPOINTMENT_LEADER = "ORDER_APPOINTMENT_LEADER"
    ACT_BEHALF_LEADER = "ACT_BEHALF_LEADER"
    DECISION_APPOINTMENT_LEADER = "DECISION_APPOINTMENT_LEADER"


class ByTaxation(str, Enum):
    NDS = "NDS"
    NON_NDS = "NDS"


class RuTaxation(str, Enum):
    OSNO = "OSNO"
    USN = "USN"
    ESHN = "ESHN"
    PSN = "PSN"
    NPD = "NPD"
    AUSN = "AUSN"


# TODO: Make 'Taxation' merge 'ByTaxation' and 'RuTaxation'
class Taxation(str, Enum):
    NDS = "NDS"
    NON_NDS = "NON_NDS"
    OSNO = "OSNO"
    USN = "USN"
    ESHN = "ESHN"
    PSN = "PSN"
    NPD = "NPD"
    AUSN = "AUSN"
