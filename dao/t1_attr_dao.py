from dataclasses import dataclass
from datetime import datetime
import json
from typing import Any


@dataclass
class T1AttrDao:
    id: int
    mac: str
    flow_state: int # 0-离开; 1\2\3-浅(活动); 4\5\6-中(学习); 7\8\9-深(心流); 10-异常
    focus_status: int

    def __init__(self, id=0, mac="", body_status=0, flow_state=0, focus_status=0, posture_state=0, activity_freq=0, warning_event=0):
        self.id = id
        self.mac = mac
        self.flow_state = flow_state
        self.focus_status = focus_status

    def from_json(self, json_data):
        self.id = json_data.get('id', 0)
        self.mac = json_data.get('mac', "")
        self.flow_state = json_data.get('flow_state', 0)
        self.focus_status = json_data.get('focus_status', 0)