from typing import Any, Text, Dict, List

from rasa_sdk import Tracker
import json


class LeadershipDialog:
    name = "leadership"

    @staticmethod
    def run(tracker: Tracker) -> Dict[Text, Any]:
        message = "Processing your input for Leadership section...\n"

        intent = tracker.latest_message["intent"]["name"]
        if intent != "leadership" and intent != "done":
            message += "Could not understand your intent. Let's get highlights for your leadership skills.\n"
            message += f"I currently have this:\n{LeadershipDialog.get_formatted_leadership_from_tracker(tracker)}"
            return {"is_complete": False, "message": message, "slots": {}}

        slots = {}
        if intent == "done":
            message += "Completed your leadership highlights.\n" \
                       f"I currently have this:\n{LeadershipDialog.get_formatted_leadership_from_tracker(tracker)}"
            slots["leadership_complete"] = True
            return {"is_complete": True, "message": message, "slots": slots}

        leadership = LeadershipDialog.fill_slots_from_tracker(tracker, slots)

        message += f"Continue providing additional highlights (one at a time). " \
                   f"Just say Done when you are done with all highlights.\n" \
                   f"I currently have this:\n{LeadershipDialog.get_formatted_leadership(leadership)}"
        return {"is_complete": False, "message": message, "slots": slots}

    @staticmethod
    def missing_info_hint(tracker):
        return "Leadership highlights - Highlight instances where you showed leadership skills " \
               "(one highlight at a time)"

    @staticmethod
    def tracker_has_missing_slots(tracker) -> bool:
        return tracker.get_slot("leadership_complete") is None or \
               tracker.get_slot("leadership_complete") is False

    @staticmethod
    def fill_slots_from_tracker(tracker: Tracker, slots):
        leadership = []
        leadership_json = tracker.get_slot("leadership")
        if leadership_json is not None:
            leadership = json.loads(leadership_json)

        nlu_text = tracker.latest_message["text"]
        leadership.append(nlu_text)

        slots["leadership"] = str(leadership).replace("'", '"')
        return leadership

    @staticmethod
    def get_formatted_leadership_from_tracker(tracker):
        leadership_json = tracker.get_slot("leadership")
        leadership = json.loads(leadership_json)
        return LeadershipDialog.get_formatted_leadership(leadership)

    @staticmethod
    def get_formatted_leadership(leadership: List[Text]):
        message = ""
        for idx, highlight in enumerate(leadership):
            message += f'{idx + 1}: {highlight}\n'
        return message
