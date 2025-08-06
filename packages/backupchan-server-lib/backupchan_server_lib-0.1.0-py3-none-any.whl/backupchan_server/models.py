"""
Application models. Read database SQL files for explanation of what each field represents.
"""

import json
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional
from datetime import datetime
from . import nameformat
from . import utility

class BackupRecycleCriteria(str, Enum):
    NONE = "none"
    COUNT = "count"
    AGE = "age"

class BackupRecycleAction(str, Enum):
    DELETE = "delete"
    RECYCLE = "recycle"

class BackupType(str, Enum):
    SINGLE = "single"
    MULTI = "multi"

@dataclass
class BackupTarget:
    id: str
    name: str
    target_type: BackupType
    recycle_criteria: BackupRecycleCriteria
    recycle_value: Optional[int]
    recycle_action: BackupRecycleAction
    location: str
    name_template: str
    deduplicate: bool
    alias: Optional[str]

@dataclass
class Backup:
    id: str
    target_id: str
    created_at: datetime
    manual: bool
    is_recycled: bool
    filesize: int

    def pretty_created_at(self) -> str:
        return self.created_at.strftime("%B %d, %Y %H:%M")

    def pretty_filesize(self) -> str:
        return utility.humanread_file_size(self.filesize)

    def asdict(self) -> dict:
        backup = asdict(self)
        backup["created_at"] = self.created_at.isoformat()
        return backup
