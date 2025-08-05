"""
Search Terms
"""
import datetime

from dataclasses import dataclass
from typing import Optional, Sequence, Union, Tuple


@dataclass(eq=True, frozen=True)
class SearchTerms:  # pylint: disable=too-many-instance-attributes
    """ 
    dataclass containing all search fields.
    """
    def __post_init__(self) -> None:
        if self.patid is not None:
            assert isinstance(self.patid, str)
            # assert len(self.patid) == 7

    date_range: Optional[Union[datetime.date, Tuple[datetime.date, datetime.date]]] = None
    timestamp: Optional[str] = None
    study_desc: Optional[str] = None
    study_uid: Optional[str] = None
    patid: Optional[str] = None
    pat_name: Optional[str] = None
    accession_number: Optional[str] = None
    modalities: Optional[Sequence[str]] = None
