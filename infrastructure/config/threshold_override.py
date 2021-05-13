from dataclasses import dataclass
from typing import Optional


@dataclass
class ThresholdOverride:
    """ Threshold overrides can be optionally specified; if not specified - default values shall be used """

    deteriorated: Optional[int] = None
    failed: Optional[int] = None
