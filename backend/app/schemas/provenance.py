from app.schemas.acquisition import AcquisitionOperationOut, AcquisitionSessionOut
from app.schemas.case import CaseOut
from app.schemas.device import DeviceOut
from app.schemas.evidence import EvidenceOut


class EvidenceDetailOut(EvidenceOut):
    """Evidence with the chain back to where it came from: session, operation, device, case.

    `stored_path` is not part of it, and no download of the bytes exists.
    """

    session: AcquisitionSessionOut
    operation: AcquisitionOperationOut | None
    device: DeviceOut
    case: CaseOut
