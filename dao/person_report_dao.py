from dataclasses import dataclass
from datetime import datetime
import json
from typing import Any


@dataclass
class PersonConcentration:
    low_concentration_time: float
    mid_concentration_time: float
    deep_concentration_time: float
    def __init__(self, low_concentration_time=0.0, mid_concentration_time=0.0, deep_concentration_time=0.0):
        self.low_concentration_time = low_concentration_time
        self.mid_concentration_time = mid_concentration_time
        self.deep_concentration_time = deep_concentration_time
    def from_json(self, json_data):
        self.low_concentration_time = json_data.get('low_concentration_time', 0.0)
        self.low_concentration_time = round(self.low_concentration_time, 1) if isinstance(self.low_concentration_time, float) else self.low_concentration_time
        self.mid_concentration_time = json_data.get('mid_concentration_time', 0.0)
        self.mid_concentration_time = round(self.mid_concentration_time, 1) if isinstance(self.mid_concentration_time, float) else self.mid_concentration_time
        self.deep_concentration_time = json_data.get('deep_concentration_time', 0.0)
        self.deep_concentration_time = round(self.deep_concentration_time, 1) if isinstance(self.deep_concentration_time, float) else self.deep_concentration_time

@dataclass
class StudentPersonStudyScore:
    focus_score: float
    posture_score: float
    def __init__(self, focus_score=0.0, posture_score=0.0):
        self.focus_score = focus_score
        self.posture_score = posture_score

    def from_json(self, json_data):
        self.focus_score = json_data.get('focus_score', 0.0)
        self.focus_score = round(self.focus_score, 1) if isinstance(self.focus_score, float) else self.focus_score
        self.posture_score = json_data.get('posture_score', 0.0)
        self.posture_score = round(self.posture_score, 1) if isinstance(self.posture_score, float) else self.posture_score
        
@dataclass
class StudentPersonFlowState:
    flow_state: int
    start_time: str
    def __init__(self, flow_state=0, start_time=""):
        self.flow_state = flow_state
        if start_time == "":
            self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            self.start_time = start_time
    def from_json(self, json_data):
        self.flow_state = json_data.get('flow_state', 0)
        self.start_time = json_data.get('start_time', "")

@dataclass
class PersonReportDao:
    student_id: int
    student_name: str
    deep_concentration_total_time: float
    deep_concentration_max_time: float
    posture_not_correct_time: float
    person_concentration: PersonConcentration
    study_score: StudentPersonStudyScore
    person_flow_state: list[StudentPersonFlowState]

    def __init__(self, student_id=0, student_name="", deep_concentration_total_time=0.0, deep_concentration_max_time=0.0, posture_not_correct_time=0.0):
        self.student_id = student_id
        self.student_name = student_name
        self.deep_concentration_total_time = deep_concentration_total_time
        self.deep_concentration_max_time = deep_concentration_max_time
        self.posture_not_correct_time = posture_not_correct_time
        self.person_concentration = PersonConcentration()
        self.study_score = StudentPersonStudyScore()
        self.person_flow_state = []
        
    def from_json(self, json_data):
        self.student_id = json_data.get('student_id', 0)
        self.student_name = json_data.get('student_name', "")
        self.deep_concentration_total_time = json_data.get('deep_concentration_total_time', 0.0)
        self.deep_concentration_total_time = round(self.deep_concentration_total_time, 1) if isinstance(self.deep_concentration_total_time, float) else self.deep_concentration_total_time
        self.deep_concentration_max_time = json_data.get('deep_concentration_max_time', 0.0)
        self.deep_concentration_max_time = round(self.deep_concentration_max_time, 1) if isinstance(self.deep_concentration_max_time, float) else self.deep_concentration_max_time
        self.posture_not_correct_time = json_data.get('posture_not_correct_time', 0.0)
        self.posture_not_correct_time = round(self.posture_not_correct_time, 1) if isinstance(self.posture_not_correct_time, float) else self.posture_not_correct_time
        person_concentration = PersonConcentration()
        person_concentration.from_json(json_data.get('person_concentration', {}))
        self.person_concentration = person_concentration
        study_score = StudentPersonStudyScore()
        study_score.from_json(json_data.get('study_score', {}))
        self.study_score = study_score
        person_flow_state_list = []
        flow_state_json = json_data.get('person_flow_state', [])
        if flow_state_json is not None:
            for item in json_data.get('person_flow_state', []):
                person_flow_state = StudentPersonFlowState()
                person_flow_state.from_json(item)
                person_flow_state_list.append(person_flow_state)
        self.person_flow_state = person_flow_state_list



def get_person_report_by_student_id(student_id: int) -> tuple[int, str|PersonReportDao]:
    url = f"{api_manager.server_url}/course/queryStudentPersonReport"
    fields = { 
        "student_id": str(student_id),
        }
    result = api_manager.api_https.request("GET", url=url, fields=fields)
    if result.status == 200:
        jobj = json.loads(result.data)
        if jobj["code"] == 200:
            datas = jobj.get('data', {})
            person_report_dao = PersonReportDao()
            person_report_dao.from_json(datas)
            return 200, person_report_dao
        else:
            return jobj["code"], jobj["message"]
    else:
        return result.status, str(result.data)
