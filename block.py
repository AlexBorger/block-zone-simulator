"""
Block module - Alex Borger

For now, this contains the structure of a block zone.  In the future, this can have get/set methods and possibly
abstract away certain safety checks
"""


class Block:
    def __init__(self, name, block_dict):
        self.name = name
        self.next_block_name = block_dict['next_block']
        self.seconds_to_reach_block = block_dict['seconds_to_reach_block']
        self.seconds_to_clear_from_held = block_dict['seconds_to_clear_from_held']
        self.seconds_to_clear_block_in_motion = block_dict['seconds_to_clear_block_in_motion']
        self.is_occupied = block_dict['is_occupied']
        self.can_operate_from_stop = block_dict['can_operate_from_stop']
        self.mandatory_hold = block_dict['mandatory_hold']
        self.hold_time = block_dict['hold_time']
