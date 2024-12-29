"""
Train module by Alex Borger

Currently, this class is just a data store.

Other things that could be added here that the circuit object shouldn't be in charge of:

- how long it actually takes to get through the circuit, maybe a function of how full the train is

"""


class Train:
    def __init__(self, train_ref_dict):
        self.name = train_ref_dict['name']
        self.current_block = train_ref_dict['current_block']
        self.next_block_name = train_ref_dict['next_block_name']
        self.seconds_to_reach_block = train_ref_dict['seconds_to_reach_block']
        self.seconds_to_clear_from_held = train_ref_dict['seconds_to_clear_from_held']
        self.seconds_to_clear_block_in_motion = train_ref_dict['seconds_to_clear_block_in_motion']
        self.seconds_to_clear_merger = 0
        self.seconds_merger_to_block = 0
        self.seconds_held_at_current_block = train_ref_dict['seconds_held_at_current_block']
        self.total_seconds_held = train_ref_dict['total_seconds_held']
        self.mandatory_hold_left = train_ref_dict['mandatory_hold_left']
        self.current_status = train_ref_dict['current_status']
        self.circuits_completed = train_ref_dict['circuits_completed']
        self.lead_train = train_ref_dict['lead_train']
        self.history = {
            'total_seconds_held':
                {}
        }
