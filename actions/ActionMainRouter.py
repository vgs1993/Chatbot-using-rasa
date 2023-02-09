from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from actions.EducationDialog import EducationDialog
from actions.ExperienceDialog import ExperienceDialog
from actions.LeadershipDialog import LeadershipDialog
from actions.ObjectiveDialog import ObjectiveDialog
from actions.PersonalInfoDialog import PersonalInfoDialog
from actions.SkillsDialog import SkillsDialog
from actions.CommunicationDialog import CommunicationDialog


class ActionMainRouter(Action):
    def name(self) -> Text:
        return "action_main_router"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        ActionMainRouter.print_slots(tracker)
        print(f'INTENT: {tracker.latest_message["intent"]}')
        print(f'ENTITIES: {tracker.latest_message["entities"]}')

        # If an active dialog is found, route to it.
        active_dialog_name = tracker.get_slot("active_dialog")
        active_dialog = ActionMainRouter.get_active_dialog(active_dialog_name)
        if active_dialog is not None:
            print(f'Active Dialog: {active_dialog.name}')
            dialog_response = active_dialog.run(tracker)
            return ActionMainRouter.process_dialog_response(active_dialog, dispatcher, tracker, dialog_response)

        # Otherwise, check intent and route.
        dialog_by_intent = ActionMainRouter.get_dialog_by_intent(tracker)
        if dialog_by_intent is not None:
            print(f'Dialog by Intent: {dialog_by_intent.name}')
            dialog_response = dialog_by_intent.run(tracker)
            return ActionMainRouter.process_dialog_response(dialog_by_intent, dispatcher, tracker, dialog_response)

        # No intent understood. See if there are any incomplete dialogs.
        incomplete_dialog = ActionMainRouter.get_incomplete_dialog(tracker)
        if incomplete_dialog is not None:
            print(f'Incomplete Dialog: {incomplete_dialog.name}')
            dialog_response = incomplete_dialog.run(tracker)
            return ActionMainRouter.process_dialog_response(incomplete_dialog, dispatcher, tracker, dialog_response)

        return []

    @staticmethod
    def process_dialog_response(dialog: Any,
                                dispatcher: CollectingDispatcher,
                                tracker: Tracker,
                                dialog_response: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        slots = dialog_response["slots"]
        message = dialog_response["message"]

        if dialog_response["is_complete"]:
            slots["active_dialog"] = None
            next_dialog_hint = ActionMainRouter.get_incomplete_dialog_hint_excluding(dialog.name, tracker)
            if next_dialog_hint is None:
                message = message + "\n-------------------\n" \
                                    "** I got everything for your resume. Thank you. See you next time. Bye. **"
            else:
                message = f'{message} \n------\nContinue providing info about any of the sections below:\n' \
                          f'{next_dialog_hint}'
        else:
            slots["active_dialog"] = dialog.name

        dispatcher.utter_message(text=message)
        return ActionMainRouter.to_slot_sets(slots)

    @staticmethod
    def to_slot_sets(slots: Dict[Text, Text]) -> List[Dict[Text, Any]]:
        slot_sets = []
        for key in slots.keys():
            slot_sets.append(SlotSet(key, slots[key]))
        return slot_sets

    @staticmethod
    def get_incomplete_dialog_hint_excluding(excluding_dialog_name,
                                             tracker: Tracker):
        hint = ""
        for dialog in [PersonalInfoDialog, ObjectiveDialog, ExperienceDialog, EducationDialog, LeadershipDialog,
                       SkillsDialog, CommunicationDialog]:
            if dialog.name != excluding_dialog_name and dialog.tracker_has_missing_slots(tracker):
                hint += f'{dialog.missing_info_hint(tracker)}\n'
        if len(hint) > 0:
            return hint
        return None

    @staticmethod
    def get_incomplete_dialog(tracker: Tracker) -> Any:
        if PersonalInfoDialog.tracker_has_missing_slots(tracker):
            return PersonalInfoDialog
        if ObjectiveDialog.tracker_has_missing_slots(tracker):
            return ObjectiveDialog
        if ExperienceDialog.tracker_has_missing_slots(tracker):
            return ExperienceDialog
        if EducationDialog.tracker_has_missing_slots(tracker):
            return EducationDialog
        if LeadershipDialog.tracker_has_missing_slots(tracker):
            return LeadershipDialog
        if SkillsDialog.tracker_has_missing_slots(tracker):
            return SkillsDialog
        if CommunicationDialog.tracker_has_missing_slots(tracker):
            return CommunicationDialog
        return None

    @staticmethod
    def get_dialog_by_intent(tracker: Tracker) -> Any:
        intent = tracker.latest_message["intent"]
        if intent is None:
            return None
        # TODO Move intent to dialogs similar to dialog name.
        intent_name = intent["name"]
        if intent_name == "personal":
            return PersonalInfoDialog
        if intent_name == "objective":
            return ObjectiveDialog
        if intent_name == "experience":
            return ExperienceDialog
        if intent_name == "education":
            return EducationDialog
        if intent_name == "leadership":
            return LeadershipDialog
        if intent_name == "skills":
            return SkillsDialog
        if intent_name == "communication":
            return CommunicationDialog
        return None

    @staticmethod
    def get_active_dialog(active_dialog_name) -> Any:
        if active_dialog_name == PersonalInfoDialog.name:
            return PersonalInfoDialog
        if active_dialog_name == ObjectiveDialog.name:
            return ObjectiveDialog
        if active_dialog_name == ExperienceDialog.name:
            return ExperienceDialog
        if active_dialog_name == EducationDialog.name:
            return EducationDialog
        if active_dialog_name == LeadershipDialog.name:
            return LeadershipDialog
        if active_dialog_name == SkillsDialog.name:
            return SkillsDialog
        if active_dialog_name == CommunicationDialog.name:
            return CommunicationDialog
        return None

    @staticmethod
    def print_slots(tracker: Tracker):
        message = "SLOTS:\n"
        for key in tracker.slots.keys():
            message += f'{key}={tracker.slots[key]}  '
        print(message)
