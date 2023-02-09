from typing import Any, Text, Dict, List

from rasa_sdk import Tracker
import json


class ExperienceDialog:
    name = "experience"

    @staticmethod
    def run(tracker: Tracker) -> Dict[Text, Any]:
        message = "Processing your input for Work History section...\n"

        intent = tracker.latest_message["intent"]["name"]
        if intent != "experience" and intent != "done":
            message += "Could not understand your intent. Let's get your work history - " \
                       "Companies you worked at, duration and job titles (one company at a time).\n"
            message += f"I currently have this:\n{ExperienceDialog.get_formatted_experience_from_tracker(tracker)}"
            return {"is_complete": False, "message": message, "slots": {}}

        slots = {}
        experience = ExperienceDialog.fill_slots_from_tracker_and_entities(tracker, slots)

        if intent == "done":
            if ExperienceDialog.are_all_companies_complete(experience):
                message += "Your work history information is complete.\n" \
                           f"I currently have this:\n{ExperienceDialog.get_formatted_work_history(experience)}"
                slots["experience_complete"] = True
                return {"is_complete": True, "message": message, "slots": slots}

        message += f"Continue providing additional/missing work history (one company at a time). " \
                   f"Just say Done when you are done with all companies.\n" \
                   f"I currently have this:\n{ExperienceDialog.get_formatted_work_history(experience)}"
        return {"is_complete": False, "message": message, "slots": slots}

    @staticmethod
    def get_formatted_work_history(experience: List[Dict[Text, Text]]):
        message = ""
        for company_history in experience:
            message += f'Company: {company_history["company"]} From: {company_history["from"]} ' \
                       f'To: {company_history["to"]} Job Title: {company_history["job_title"]}\n'
        return message

    @staticmethod
    def missing_info_hint(tracker):
        return "Work history - Companies you worked at, duration and job titles (one company at a time)."

    @staticmethod
    def tracker_has_missing_slots(tracker) -> bool:
        return tracker.get_slot("experience_complete") is None or \
               tracker.get_slot("experience_complete") is False

    @staticmethod
    def are_all_companies_complete(experience: List[Dict[Text, Text]]) -> bool:
        for company_work_history in experience:
            if len(company_work_history["from"]) == 0 or \
                    len(company_work_history["to"]) == 0 or \
                    len(company_work_history["job_title"]) == 0:
                return False
        return True

    @staticmethod
    def fill_slots_from_tracker_and_entities(tracker: Tracker, slots):
        experience = []
        experience_json = tracker.get_slot("experience")
        if experience_json is not None:
            experience = json.loads(experience_json)

        nlu_entities = tracker.latest_message["entities"]
        company_name = ExperienceDialog.find_entity(nlu_entities, "company", None)

        if company_name is not None:
            work_history = ExperienceDialog.get_or_create_work_history(experience, company_name)
            from_year = ExperienceDialog.find_entity(nlu_entities, "year", "from")
            if from_year is not None:
                work_history["from"] = from_year
            to_year = ExperienceDialog.find_entity(nlu_entities, "year", "to")
            if to_year is not None:
                work_history["to"] = to_year
            job_title = ExperienceDialog.find_entity(nlu_entities, "job_title", None)
            if job_title is not None:
                work_history["job_title"] = job_title

        slots["experience"] = str(experience).replace("'", '"')
        return experience

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
    def get_or_create_work_history(experience, company_name) -> Dict[Text, Any]:
        for company_work_history in experience:
            if company_work_history["company"] == company_name:
                return company_work_history

        work_history = {"company": company_name, "from": "", "to": "", "job_title": ""}
        experience.append(work_history)
        return work_history

    @staticmethod
    def get_formatted_experience_from_tracker(tracker):
        experience_json = tracker.get_slot("experience")
        experience = json.loads(experience_json)
        message = ""
        for company_history in experience:
            message += f'Company: {company_history["company"]} From: {company_history["from"]} ' \
                       f'To: {company_history["to"]} Job Title: {company_history["job_title"]}\n'
        return message
