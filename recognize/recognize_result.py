
from dataclasses import dataclass

from dao.invoice_record_dao import InvoiceRecordDao
from dao.tax_approval_dao import TaxApprovalDao


@dataclass
class InvoiceRecognizeResult:
    result: int
    msg: str
    data: None|InvoiceRecordDao


@dataclass
class CertificateRecognizeResult:
    result: int
    msg: str
    data: None|list[TaxApprovalDao]    