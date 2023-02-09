from typing import Any, Text, Dict

from rasa_sdk import Tracker


class ObjectiveDialog:
    name = "objective"

    @staticmethod
    def run(tracker: Tracker) -> Dict[Text, Any]:
        message = "Processing your input for Objective section...\n"

        if tracker.latest_message["intent"]["name"] != "objective":
            message += "Could not understand your intent. Let's get an Objective for your resume.\n"
            message += f"I currently have this:\n{ObjectiveDialog.get_slots_from_tracker(tracker)}"
            return {"is_complete": False, "message": message, "slots": {}}

        slots = {}
        ObjectiveDialog.fill_objective_from_text(tracker, slots)

        if ObjectiveDialog.are_slots_complete(slots):
            message += "Your Objective information is complete.\n" \
                       f"I currently have this:\n{ObjectiveDialog.get_slots(slots)}"
            return {"is_complete": True, "message": message, "slots": slots}

        message += f"Continue providing your resume Objective.\n" \
                   f"I currently have this:\n{ObjectiveDialog.get_slots(slots)}"
        return {"is_complete": False, "message": message, "slots": slots}

    @staticmethod
    def get_slots(slots):
        return f'Objective: {slots["objective"]}'

    @staticmethod
    def missing_info_hint(tracker):
        if tracker.get_slot("objective") is None:
            return f"An Objective for your resume"
        return None

    @staticmethod
    def tracker_has_missing_slots(tracker) -> bool:
        return tracker.get_slot("objective") is None

    @staticmethod
    def are_slots_complete(slots) -> bool:
        return ObjectiveDialog.is_slot_complete("objective", slots)

    @staticmethod
    def is_slot_complete(slot_name, slots: Dict[Text, Text]) -> bool:
        return slot_name in slots.keys() and slots[slot_name] is not None

    @staticmethod
    def fill_objective_from_text(tracker: Tracker, slots):
        slots["objective"] = tracker.latest_message["text"]

    @staticmethod
    def get_slots_from_tracker(tracker):
        return f'Objective: {tracker.get_slot("objective")}'
