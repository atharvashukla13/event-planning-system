from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
import json
import uuid

@dataclass
class EventInvitation:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    host_name: str = ""
    event_name: str = ""
    date_time: str = ""
    location: str = ""
    description: str = ""
    max_capacity: Optional[int] = None
    
    def to_json(self):
        return json.dumps(self.__dict__)
    
    @classmethod
    def from_json(cls, json_str):
        return cls(**json.loads(json_str))

@dataclass
class GuestResponse:
    guest_id: str = ""
    guest_name: str = ""
    event_id: str = ""
    response: str = ""  # "Yes", "No", "Maybe"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    message: Optional[str] = None
    
    def to_json(self):
        return json.dumps(self.__dict__)
    
    @classmethod
    def from_json(cls, json_str):
        return cls(**json.loads(json_str))

@dataclass
class EventSummary:
    event_id: str = ""
    event_name: str = ""
    total_invited: int = 0
    responses: List[Dict] = field(default_factory=list)
    attending_count: int = 0
    not_attending_count: int = 0
    maybe_count: int = 0
    no_response_count: int = 0
    
    def to_json(self):
        return json.dumps(self.__dict__)
    
    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls(**data)