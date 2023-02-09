from typing import Any, Text, Dict

from rasa_sdk import Tracker


class PersonalInfoDialog:
    name = "personal_info"

    @staticmethod
    def run(tracker: Tracker) -> Dict[Text, Any]:
        message = "Processing your input for Personal Information section...\n"

        # If this dialog is active and user utters something other than 'personal',
        # nudge them to provide personal info. Another scenario is when user begins conversation.
        if tracker.latest_message["intent"]["name"] != "personal":
            message += "Could not understand your intent. Let's get your personal information - " \
                       "Name, Address, Email, Phone.\n"
            message += f"I currently have this:\n{PersonalInfoDialog.get_slots_from_tracker(tracker)}"
            return {"is_complete": False, "message": message, "slots": {}}

        slots = {}
        if tracker.get_slot("active_slot") == "street":
            PersonalInfoDialog.fill_slots_for_street(tracker, slots)
        else:
            PersonalInfoDialog.fill_slots_from_tracker_and_entities(tracker, slots)
        
        PersonalInfoDialog.fill_street_from_text(tracker, slots)


        if PersonalInfoDialog.are_slots_complete(slots):
            message += "Your personal information is complete.\n" \
                       f"I currently have this:\n{PersonalInfoDialog.get_slots(slots)}"
            return {"is_complete": True, "message": message, "slots": slots}

        # NER is not able to recognize street due to spaces. Explicitly getting it from user.
        if PersonalInfoDialog.only_street_pending(slots):
            message += "I'm not good at understanding street addresses." \
                       " Can you please provide me your exact street address?\n" \
                       f"I currently have this:\n{PersonalInfoDialog.get_slots(slots)}"
            slots["active_slot"] = "street"
            return {"is_complete": False, "message": message, "slots": slots}

        # More than one slots pending.
        message += f"Continue providing the missing personal information " \
                   f"(except Street. I'm not good at understanding it).\n" \
                   f"I currently have this:\n{PersonalInfoDialog.get_slots(slots)}"
        return {"is_complete": False, "message": message, "slots": slots}

    @staticmethod
    def get_slots(slots):
        message = ""
        message += f'Name   = {slots["PERSON"]}\n'
        message += f'Street = {slots["street"]}, City = {slots["city"]},' \
                   f' State = {slots["state"]}, Pincode = {slots["pin_code"]}\n'
        message += f'Phone = {slots["phone_number"]}, Email = {slots["email"]}\n'
        return message

    @staticmethod
    def missing_info_hint(tracker):
        missing_slots = []
        for slot_name in ["PERSON", "street", "city", "state", "pin_code", "phone_number", "email"]:
            if tracker.get_slot(slot_name) is None:
                missing_slots.append(slot_name)

        if len(missing_slots) == 0:
            return None

        return f"Personal Information. Missing info - {missing_slots}"

    @staticmethod
    def tracker_has_missing_slots(tracker) -> bool:
        return tracker.get_slot("PERSON") is None or \
               tracker.get_slot("street") is None or \
               tracker.get_slot("city") is None or \
               tracker.get_slot("state") is None or \
               tracker.get_slot("pin_code") is None or \
               tracker.get_slot("phone_number") is None or \
               tracker.get_slot("email") is None

    @staticmethod
    def are_slots_complete(slots) -> bool:
        return PersonalInfoDialog.is_slot_complete("PERSON", slots) and \
               PersonalInfoDialog.is_slot_complete("street", slots) and \
               PersonalInfoDialog.is_slot_complete("city", slots) and \
               PersonalInfoDialog.is_slot_complete("state", slots) and \
               PersonalInfoDialog.is_slot_complete("pin_code", slots) and \
               PersonalInfoDialog.is_slot_complete("phone_number", slots) and \
               PersonalInfoDialog.is_slot_complete("email", slots)

    @staticmethod
    def only_street_pending(slots):
        return PersonalInfoDialog.is_slot_complete("PERSON", slots) and \
               not PersonalInfoDialog.is_slot_complete("street", slots) and \
               PersonalInfoDialog.is_slot_complete("city", slots) and \
               PersonalInfoDialog.is_slot_complete("state", slots) and \
               PersonalInfoDialog.is_slot_complete("pin_code", slots) and \
               PersonalInfoDialog.is_slot_complete("phone_number", slots) and \
               PersonalInfoDialog.is_slot_complete("email", slots)

    @staticmethod
    def is_slot_complete(slot_name, slots: Dict[Text, Text]) -> bool:
        return slot_name in slots.keys() and slots[slot_name] is not None

    @staticmethod
    def fill_street_from_text(tracker: Tracker, slots):
        if tracker.get_slot("active_slot") == "street":
            slots["active_slot"] = None
            slots["street"] = tracker.latest_message["text"]

    @staticmethod
    def fill_slots_from_tracker_and_entities(tracker: Tracker, slots):
        for slot_name in ["PERSON", "street", "city", "state", "pin_code", "phone_number", "email"]:
            # Prev value.
            slot_value = tracker.get_slot(slot_name)
            # New value from NLU.
            for entity in tracker.latest_message["entities"]:
                if entity["entity"] == slot_name:
                    slot_value = entity["value"]
            slots[slot_name] = slot_value

    @staticmethod
    def fill_slots_for_street(tracker: Tracker, slots):
        for slot_name in ["PERSON", "street", "city", "state", "pin_code", "phone_number", "email"]:
            # Prev value.
            slot_value = tracker.get_slot(slot_name)
            slots[slot_name] = slot_value

    @staticmethod
    def get_slots_from_tracker(tracker):
        message = ""
        message += f'Name   = {tracker.get_slot("PERSON")}\n'
        message += f'Street = {tracker.get_slot("street")}, City = {tracker.get_slot("city")},' \
                   f' State = {tracker.get_slot("state")}, Pincode = {tracker.get_slot("pin_code")}\n'
        message += f'Phone = {tracker.get_slot("phone_number")}, Email = {tracker.get_slot("email")}\n'
        return message
