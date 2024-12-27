"""
Block module - Alex Borger

For now, this contains the structure of a block zone.  In the future, this can have get/set methods and possibly
abstract away certain safety checks

- we could add a get_next here
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
        self.has_merger_switch = block_dict['has_merger_switch']
        self.merger_switch_position = None
        self.merger_switch_status = None
        self.corresponding_splitter_block = None
        self.corresponding_merger_block = None
        self.seconds_to_clear_merger = 0
        self.seconds_merger_to_block = 0
        if self.has_merger_switch:
            self.merger_block_a = block_dict['merger_block_a']
            self.merger_block_b = block_dict['merger_block_b']
            self.seconds_to_clear_merger = block_dict['seconds_to_clear_merger']
            self.seconds_merger_to_block = block_dict['seconds_merger_to_block']
            self.merger_switch_position = self.merger_block_a
            self.merger_switch_status = 'in position'  # can be 'in position' or 'in motion' -> en route to switch_pos
            self.corresponding_splitter_block = block_dict['corresponding_splitter_block']
            # for now, we should just have instantaneous switching. once it all works, add switch delay
        self.has_splitter_switch = block_dict['has_splitter_switch']
        if self.has_splitter_switch:
            self.splitter_block_a = block_dict['splitter_block_a']
            self.splitter_block_b = block_dict['splitter_block_b']
            if self.next_block_name == self.splitter_block_a:
                self.splitter_switch_position = self.splitter_block_a
            elif self.next_block_name == self.splitter_block_b:
                self.splitter_switch_position = self.splitter_block_b
            else:
                raise ValueError("Invalid 'next_block_name' specified for block with splitter switch.")
            self.splitter_switch_status = 'in position'  # same as above
            self.corresponding_merger_block = block_dict['corresponding_merger_block']

    def occupy(self, requester_block=None, override=False):
        """ train wants to occupy zone
        """
        if override:
            self.is_occupied = True
            return True
        # if switch involved: verify status of switch before giving approval
        if self.is_occupied:
            return False
        elif self.has_merger_switch:
            if not requester_block:
                raise ValueError("Merger block occupy() called without requester block specified.")
            if self.merger_switch_status == 'in motion':
                return False
            # otherwise, it must be in position
            if self.merger_switch_position == requester_block:
                # we arent occupied and switch is ready and in position from requesting block
                self.is_occupied = True
                return True
            else:
                # not requester's turn!
                return False
        else:
            self.is_occupied = True
            return True

    def unoccupy(self, override_switch=False):
        """ train is leaving block zone, free it.  if override_switch = True, we will not switch
        """
        self.is_occupied = False
        if self.has_splitter_switch and not override_switch:
            # we should toggle the splitter switch.
            self.toggle_splitter_switch()

    def get_merger_switch_status(self):
        """ return block names of (active, inactive) inbound merger blocks in that order """
        if self.merger_switch_position == self.merger_block_a:
            return self.merger_block_a, self.merger_block_b
        else:
            return self.merger_block_b, self.merger_block_a

    def signal_cleared_merger(self, switch):
        # update internal state to the extent we care to
        if switch:
            self.toggle_merger_switch()
        else:
            pass

    def toggle_merger_switch(self):
        """ change merger switch position from current to other
        eventually we can add delay here
        """
        if self.merger_switch_position == self.merger_block_a:
            self.merger_switch_position = self.merger_block_b
        elif self.merger_switch_position == self.merger_block_b:
            self.merger_switch_position = self.merger_block_a
        else:
            raise ValueError("toggle_merger_switch encountered invalid self.merger_switch_position!")

    def toggle_splitter_switch(self):
        if self.splitter_switch_position == self.splitter_block_a:
            self.splitter_switch_position = self.splitter_block_b
            self.next_block_name = self.splitter_block_b
        elif self.splitter_switch_position == self.splitter_block_b:
            self.splitter_switch_position = self.splitter_block_a
            self.next_block_name = self.splitter_block_a
        else:
            raise ValueError("toggle_splitter_switch encountered invalid self.splitter_switch_position!")
