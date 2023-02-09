from typing import Any, Text, Dict

from rasa_sdk import Tracker


class SkillsDialog:
    name = "skills"

    @staticmethod
    def run(tracker: Tracker) -> Dict[Text, Any]:

        if tracker.latest_message["intent"]["name"] != "skills":
            message = "Let's get Skills information for your resume. You can provide top 3 skills\n"
            message += f"I currently have this:\n{SkillsDialog.get_slots_from_tracker(tracker)}"
            return {"is_complete": False, "message": message, "slots": {}}

        slots = {}
        SkillsDialog.fill_skills_from_text(tracker, slots)

        if SkillsDialog.are_slots_complete(slots):
            message = "Your Skills information is complete.\n" \
                      f"I currently have this:\n{SkillsDialog.get_slots(slots)}"
            return {"is_complete": True, "message": message, "slots": slots}

        message = f"Continue providing your resume Skills.\n" \
                  f"I currently have this:\n{SkillsDialog.get_slots(slots)}"
        return {"is_complete": False, "message": message, "slots": slots}

    @staticmethod
    def get_slots(slots):
        return f'Skills = {slots["skill"]}'

    @staticmethod
    def missing_info_hint(tracker) -> bool:
        if tracker.get_slot("skill") is None:
            return f"Skills and Abilities"
        return None

    @staticmethod
    def tracker_has_missing_slots(tracker) -> bool:
        return tracker.get_slot("skill") is None

    @staticmethod
    def are_slots_complete(slots) -> bool:
        return SkillsDialog.is_slot_complete("skill", slots)

    @staticmethod
    def is_slot_complete(slot_name, slots: Dict[Text, Text]) -> bool:
        return slot_name in slots.keys() and slots[slot_name] is not None

    @staticmethod
    def fill_skills_from_text(tracker: Tracker, slots):
        slots["skill"] = tracker.latest_message["text"]

    @staticmethod
    def get_slots_from_tracker(tracker):
        return f'Skills = {tracker.get_slot("skill")}'
