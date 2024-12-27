"""
Circuit module - Alex Borger

This class defines the complete attraction layout.

Attributes:
    - blocks
        - a dictionary of distinct block zones on the circuit
    - num_complete_blocks
        - inferred from self.blocks, discounts any blocks that are e-stops only.
    - num_trains (int) : an input parameter that specifies the number of trains on the circuit
    - trains
        - a dictionary of train objects, each responsible for managing their current location and state
    - time (int): current time step of the simulation run (default unit: seconds)
"""

import numpy as np

from block import Block
from train import Train


class Circuit:
    def __init__(self, block_ref_dict, num_trains, optional_params=None):
        self.blocks = {}
        for block in block_ref_dict:
            self.blocks[block] = Block(name=block, block_dict=block_ref_dict[block])
        self.num_complete_blocks = self.calculate_complete_blocks()
        self.num_trains = num_trains
        self.trains = {}
        self.add_trains_to_circuit()
        for train in self.trains:
            self.blocks[self.trains[train].current_block].occupy(override=True)
        self.time = 0
        self.dispatch_sluggishness = False
        self.sluggishness_mu = None
        self.sluggishness_sigma = None
        self.random_seed = 0
        if optional_params:
            if 'sluggishness' in optional_params:
                self.dispatch_sluggishness = optional_params['sluggishness']
                self.sluggishness_mu = optional_params['sluggishness_mu']
                self.sluggishness_sigma = optional_params['sluggishness_sigma']
            if 'random_seed' in optional_params:
                self.random_seed = optional_params['random_seed']
            if 'circuit_completion_blocks' in optional_params:
                self.circuit_completion_blocks = optional_params['circuit_completion_blocks']
            else:
                self.circuit_completion_blocks = None
        self.rng = np.random.default_rng(self.random_seed)

    def calculate_complete_blocks(self):
        return len([b for b in self.blocks if self.blocks[b].can_operate_from_stop])

    def add_trains_to_circuit(self):
        # evenly space out the blocks
        blocks_to_assign = [round(x*self.num_complete_blocks/self.num_trains) for x in range(self.num_trains)]
        valid_blocks = [b for b in self.blocks if self.blocks[b].can_operate_from_stop]
        trains_assigned = 0
        for i in range(self.num_trains):
            train_name = f'train {i}'
            lead_train = (i == 0)
            block = valid_blocks[blocks_to_assign[i]]
            train = {
                'name': train_name,
                'current_block': block,
                'next_block_name': self.blocks[block].next_block_name,
                'seconds_to_reach_block': 0,
                'seconds_to_clear_from_held': 0,
                'seconds_to_clear_block_in_motion': 0,
                'seconds_held_at_current_block': 0,
                'total_seconds_held': 0,
                'mandatory_hold_left': 0,
                'current_status': 'held',
                'circuits_completed': 0,
                'lead_train': lead_train
            }
            self.trains[train_name] = Train(train_ref_dict=train)

    def step(self):
        trains_advanced = 0
        trains_blocked = 0
        # advance each train if possible
        for train_name in self.trains:
            curr_block = self.trains[train_name].current_block
            next_block = self.blocks[curr_block].next_block_name  # self.trains[train_name].next_block_name
            if self.trains[train_name].current_status == 'held':
                # do a thing because they are held rn
                if self.trains[train_name].mandatory_hold_left > 0:
                    # held and not ready to go
                    self.trains[train_name].mandatory_hold_left -= 1
                else:
                    # held and ready to go
                    # is the next block ready?
                    if not self.blocks[next_block].occupy(requester_block=curr_block):
                        # we cannot go anywhere
                        if not self.blocks[curr_block].can_operate_from_stop:
                            # TODO: signal to all other trains to stop at the next possible block.
                            raise ValueError(f"Train {train_name} halted at block {curr_block}. Ride is now in 101 status.")
                        self.trains[train_name].seconds_held_at_current_block += 1
                        self.trains[train_name].total_seconds_held += 1
                        trains_blocked += 1
                    else:
                        # we can proceed but from held position
                        self.trains[train_name].seconds_to_clear_from_held = self.blocks[curr_block].seconds_to_clear_from_held
                        self.trains[train_name].current_status = 'after block - from held'
            # elif/else... means we are in motion.  EITHER: seconds_to_reach_block > 0 (we haven't reached our own block yet), OR
            # seconds_to_clear_from_held > 0 (we were held and were recently released), OR seconds_to_clear_block_in_motion > 0 (we reached
            # our own block but haven't exited it yet).  Only ONE of these should be > 0 at any given time. if all are 0...
            elif self.trains[train_name].seconds_to_reach_block > 0:
                # if we haven't reached block yet, check if we cleared merger
                if self.blocks[curr_block].has_merger_switch:
                    if self.trains[train_name].seconds_to_clear_merger > 0:
                        self.trains[train_name].seconds_to_clear_merger -= 1
                        if self.trains[train_name].seconds_to_clear_merger == 0 and self.num_trains > 1:
                            # let block decide if it wants to activate merge switch
                            active_block, inactive_block = self.blocks[curr_block].get_merger_switch_status()
                            # if we know the next dispatch is going to be from the inactive block, switch it.
                            # TODO: Implement above. If both stations are empty, merger should anticipate taking
                            # train from whichever station the splitter is going to send a train to
                            # if exactly one is occupied, it should point to the occupied block
                            # if both are occupied, it should take from the train that will dispatch sooner, or in a
                            # dead tie, do nothing
                            active_block_occupied = self.blocks[active_block].is_occupied
                            inactive_block_occupied = self.blocks[inactive_block].is_occupied
                            # TODO: If this is the best implementation, simplify
                            switch = False
                            if not active_block_occupied and not inactive_block_occupied:
                                # neither are occupied, point to wherever the splitter is pointing
                                corr_splitter_block = self.blocks[curr_block].corresponding_splitter_block
                                if self.blocks[corr_splitter_block].splitter_switch_position == inactive_block:
                                    switch = True
                            elif active_block_occupied and not inactive_block_occupied:
                                # we shouldn't do anything
                                # self.blocks[curr_block].signal_cleared_merger(switch=False)
                                switch = False
                            elif not active_block_occupied and inactive_block_occupied:
                                # we need to switch to the other
                                switch = True
                            else:
                                # both are occupied
                                switch = False
                            self.blocks[curr_block].signal_cleared_merger(switch=switch)
                    else:
                        # not sure if this attribute is really needed
                        self.trains[train_name].seconds_merger_to_block -= 1
                self.trains[train_name].seconds_to_reach_block -= 1
            elif self.trains[train_name].seconds_to_clear_from_held > 0:
                # we were held, decrease this
                self.trains[train_name].seconds_to_clear_from_held -= 1
            elif self.trains[train_name].seconds_to_clear_block_in_motion > 0:
                # we are past our own block, never stopped at it either
                self.trains[train_name].seconds_to_clear_block_in_motion -= 1
            else:
                # 'before block', 'after block - from held', 'after block - not held'
                # we either reached the block OR are ready to exit it
                if self.trains[train_name].current_status == 'before block':
                    # we hadn't reached the block and now we either have to keep moving from motion or stop
                    if self.blocks[curr_block].mandatory_hold:
                        # we reached station (or show scene? transfer track? etc... and must pause
                        self.trains[train_name].current_status = 'held'
                        self.trains[train_name].mandatory_hold_left = self.blocks[curr_block].hold_time
                        if self.dispatch_sluggishness:
                            delay = round(self.rng.lognormal(mean=1.5, sigma=0.6))
                            self.trains[train_name].mandatory_hold_left += delay
                    else:
                        if not self.blocks[next_block].occupy(requester_block=curr_block):
                        # this means another train is there! we cannot proceed.
                        # mark train as held
                            self.trains[train_name].current_status = 'held'
                            trains_blocked += 1
                            if not self.blocks[curr_block].can_operate_from_stop:
                                # TODO: signal to all other trains to stop at the next possible block.
                                raise ValueError(f"Train {train_name} halted at block {curr_block}. Ride is now in 101 status.")
                        else:
                            # we were moving, reached block and are cleared to move forward
                            self.trains[train_name].seconds_to_clear_block_in_motion = self.blocks[curr_block].seconds_to_clear_block_in_motion
                            self.trains[train_name].current_status = 'after block - not held'
                    # if next block already belongs to us, that means we already reached our block and are proceeding forward
                else:
                    # we reached end of block from motion OR stopped, either way... advance to next block
                    # we already own the next block, no need to check or alter it
                    # release current block
                    self.trains[train_name].current_block = next_block
                    self.trains[train_name].next_block_name = self.blocks[next_block].next_block_name
                    self.trains[train_name].seconds_to_reach_block = self.blocks[next_block].seconds_to_reach_block
                    self.trains[train_name].seconds_to_clear_merger = self.blocks[next_block].seconds_to_clear_merger
                    self.trains[train_name].seconds_held_at_current_block = 0
                    self.trains[train_name].current_status = 'before block'
                    self.blocks[curr_block].unoccupy(override_switch=(self.num_trains == 1))
                    if self.circuit_completion_blocks:
                        if next_block in self.circuit_completion_blocks:
                            self.trains[train_name].circuits_completed += 1
                            #if trains[train_name]['lead_train']:
                            #    print("Lead train completed circuit!")
                            trains_advanced += 1
        if trains_blocked == self.num_trains:
            # we hit gridlock
            raise ValueError(f"Gridlock hit at t={self.time}!")
        self.time += 1
