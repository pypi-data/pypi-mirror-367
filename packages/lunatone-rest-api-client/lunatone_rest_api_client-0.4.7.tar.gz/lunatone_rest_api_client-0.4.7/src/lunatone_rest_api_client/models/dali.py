from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field, NonNegativeInt


class StartScanData(BaseModel):
    new_installation: bool = Field(False, alias="newInstallation")
    no_addressing: bool = Field(False, alias="noAddressing")
    use_lines: list[NonNegativeInt] = Field([], alias="useLines")


class ScanState(StrEnum):
    NOT_STARTED = "not started"
    CANCELLED = "cancelled"
    DONE = "done"
    ADDRESSING = "addressing"
    IN_PROGRESS = "in progress"


class ScanData(BaseModel):
    id: str = ""
    progress: float = 0
    found: int = 0
    found_sensors: int = Field(0, alias="foundSensors")
    status: ScanState = ScanState.NOT_STARTED
    lines: list[dict] = []
