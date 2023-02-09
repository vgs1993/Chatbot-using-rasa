from typing import Any, Text, Dict, List

from rasa_sdk import Tracker
import json


class EducationDialog:
    name = "education"

    @staticmethod
    def run(tracker: Tracker) -> Dict[Text, Any]:
        message = "Processing your input for Education section...\n"

        intent = tracker.latest_message["intent"]["name"]
        if intent != "education" and intent != "done":
            message += "Could not understand your intent. Let's get your Education history - " \
                       "Degrees, duration and Location (one degree at a time).\n"
            message += f"I currently have this:\n{EducationDialog.get_formatted_education_from_tracker(tracker)}"
            return {"is_complete": False, "message": message, "slots": {}}

        slots = {}
        education = EducationDialog.fill_slots_from_tracker_and_entities(tracker, slots)

        if intent == "done":
            if EducationDialog.are_all_degrees_complete(education):
                message += "Your Education history information is complete.\n" \
                           f"I currently have this:\n{EducationDialog.get_formatted_education_history(education)}"
                slots["education_complete"] = True
                return {"is_complete": True, "message": message, "slots": slots}

        message += f"Continue providing additional/missing Education history (one degree at a time). " \
                   f"Just say Done when you are done with all degrees.\n" \
                   f"I currently have this:\n{EducationDialog.get_formatted_education_history(education)}"
        return {"is_complete": False, "message": message, "slots": slots}

    @staticmethod
    def get_formatted_education_history(education: List[Dict[Text, Text]]):
        message = ""
        for education_history in education:
            message += f'Degree: {education_history["degree"]} From: {education_history["from"]} ' \
                       f'To: {education_history["to"]} School: {education_history["school"]} ' \
                       f'Location: {education_history["location"]}\n'
        return message

    @staticmethod
    def missing_info_hint(tracker):
        return "Education history - Degrees, duration and Location (one degree at a time)."

    @staticmethod
    def tracker_has_missing_slots(tracker) -> bool:
        return tracker.get_slot("education_complete") is None or \
               tracker.get_slot("education_complete") is False

    @staticmethod
    def are_all_degrees_complete(education: List[Dict[Text, Text]]) -> bool:
        for degree_details in education:
            if len(degree_details["from"]) == 0 or \
                    len(degree_details["to"]) == 0 or \
                    len(degree_details["school"]) == 0 or \
                    len(degree_details["location"]) == 0:
                return False
        return True

    @staticmethod
    def fill_slots_from_tracker_and_entities(tracker: Tracker, slots):
        education = []
        eduation_json = tracker.get_slot("education")
        if eduation_json is not None:
            education = json.loads(eduation_json)

        nlu_entities = tracker.latest_message["entities"]
        degree = EducationDialog.find_entity(nlu_entities, "degree", None)

        if degree is not None:
            work_history = EducationDialog.get_or_create_education_history(education, degree)
            from_year = EducationDialog.find_entity(nlu_entities, "year", "from")
            if from_year is not None:
                work_history["from"] = from_year
            to_year = EducationDialog.find_entity(nlu_entities, "year", "to")
            if to_year is not None:
                work_history["to"] = to_year
            school = EducationDialog.find_entity(nlu_entities, "school", None)
            if school is not None:
                work_history["school"] = school
            location = EducationDialog.find_entity(nlu_entities, "city", None)
            if location is not None:
                work_history["location"] = location

        slots["education"] = str(education).replace("'", '"')
        return education

    @staticmethod
    def find_entity(nlu_entities, entity_name, entity_role):
        for entity in nlu_entities:
            if entity["entity"] == entity_name:
                if entity_role is None:
                    return entity["value"]
                else:
                    if entity["role"] == entity_role:
                        return entity["value"]
        return None

    @staticmethod
    def get_or_create_education_history(education, degree) -> Dict[Text, Any]:
        for degree_details in education:
            if degree_details["degree"] == degree:
                return degree_details

        degree_details = {"degree": degree, "from": "", "to": "", "school": "", "location": ""}
        education.append(degree_details)
        return degree_details

    @staticmethod
    def get_formatted_education_from_tracker(tracker):
        education_json = tracker.get_slot("education")
        education = json.loads(education_json)
        message = ""
        for degree_details in education:
            message += f'Degree: {degree_details["degree"]} From: {degree_details["from"]} ' \
                       f'To: {degree_details["to"]} School: {degree_details["school"]} ' \
                       f'Location: {degree_details["location"]}\n'
        return message
