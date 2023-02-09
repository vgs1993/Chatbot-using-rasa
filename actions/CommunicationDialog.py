from typing import Any, Text, Dict

from rasa_sdk import Tracker


class CommunicationDialog:
    name = "communication"

    @staticmethod
    def run(tracker: Tracker) -> Dict[Text, Any]:

        if tracker.latest_message["intent"]["name"] != "communication":
            message = "Please provide Communication details i.e. Languages known(read & write) for your resume.\n"
            message += f"I currently have this:\n{CommunicationDialog.get_slots_from_tracker(tracker)}"
            return {"is_complete": False, "message": message, "slots": {}}

        slots = {}
        CommunicationDialog.fill_communication_from_text(tracker, slots)

        if CommunicationDialog.are_slots_complete(slots):
            message = "Your Communication information is complete.\n" \
                      f"I currently have this:\n{CommunicationDialog.get_slots(slots)}"
            return {"is_complete": True, "message": message, "slots": slots}

        message = f"Continue providing your resume Communication.\n" \
                  f"I currently have this:\n{CommunicationDialog.get_slots(slots)}"
        return {"is_complete": False, "message": message, "slots": slots}

    @staticmethod
    def get_slots(slots):
        return f'Communication = {slots["communication"]}'

    @staticmethod
    def missing_info_hint(tracker) -> bool:
        if tracker.get_slot("communication") is None:
            return f"Communication Languages"
        return None

    @staticmethod
    def tracker_has_missing_slots(tracker) -> bool:
        return tracker.get_slot("communication") is None

    @staticmethod
    def are_slots_complete(slots) -> bool:
        return CommunicationDialog.is_slot_complete("communication", slots)

    @staticmethod
    def is_slot_complete(slot_name, slots: Dict[Text, Text]) -> bool:
        return slot_name in slots.keys() and slots[slot_name] is not None

    @staticmethod
    def fill_communication_from_text(tracker: Tracker, slots):
        slots["communication"] = tracker.latest_message["text"]

    @staticmethod
    def get_slots_from_tracker(tracker):
        return f'Communication = {tracker.get_slot("communication")}'
