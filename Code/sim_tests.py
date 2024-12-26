from circuit import Circuit

blocks = {
    'station 1': {
        'next_block': 'lift 1',
        'seconds_to_reach_block': 8,
        'seconds_to_clear_from_held': 6,
        'seconds_to_clear_block_in_motion': None,
        'is_occupied': False,
        'can_operate_from_stop': True,
        'mandatory_hold': True,
        'hold_time': 38,
        'has_merger_switch': False,
        'has_splitter_switch': False
    },
    'station 2': {
        'next_block': 'lift 1',
        'seconds_to_reach_block': 8,
        'seconds_to_clear_from_held': 6,
        'seconds_to_clear_block_in_motion': None,
        'is_occupied': False,
        'can_operate_from_stop': True,
        'mandatory_hold': True,
        'hold_time': 38,
        'has_merger_switch': False,
        'has_splitter_switch': False
    },
    'lift 1': {
        'next_block': 'gravity 1',
        'seconds_to_reach_block': 18,
        'seconds_to_clear_from_held': 8,
        'seconds_to_clear_block_in_motion': 7,
        'is_occupied': False,
        'can_operate_from_stop': True,
        'mandatory_hold': False,
        'hold_time': None,
        'has_merger_switch': True,
        'merger_block_a': 'station 1',
        'merger_block_b': 'station 2',
        'seconds_to_clear_merger': 2,
        'seconds_merger_to_block': 16,  # purely for reference at the moment
        'has_splitter_switch': False
    },
    'gravity 1': {
        'next_block': 'lift 2',
        'seconds_to_reach_block': 30,
        'seconds_to_clear_from_held': 6,
        'seconds_to_clear_block_in_motion': 3,
        'is_occupied': False,
        'can_operate_from_stop': True,
        'mandatory_hold': False,
        'hold_time': None,
        'has_merger_switch': False,
        'has_splitter_switch': False
    },
    'lift 2': {
        'next_block': 'gravity 2',
        'seconds_to_reach_block': 20,
        'seconds_to_clear_from_held': 8,
        'seconds_to_clear_block_in_motion': 7,
        'is_occupied': False,
        'can_operate_from_stop': True,
        'mandatory_hold': False,
        'hold_time': None,
        'has_merger_switch': False,
        'has_splitter_switch': False
    },
    'gravity 2': {
        'next_block': 'final block 1',
        'seconds_to_reach_block': 22,
        'seconds_to_clear_from_held': 6,
        'seconds_to_clear_block_in_motion': 3,
        'is_occupied': False,
        'can_operate_from_stop': True,
        'mandatory_hold': False,
        'hold_time': None,
        'has_merger_switch': False,
        'has_splitter_switch': False
    },
    'final block 1': {
        'next_block': 'station 1',
        'seconds_to_reach_block': 8,
        'seconds_to_clear_from_held': 6,
        'seconds_to_clear_block_in_motion': 3,
        'is_occupied': False,
        'can_operate_from_stop': True,
        'mandatory_hold': False,
        'hold_time': None,
        'has_merger_switch': False,
        'has_splitter_switch': True,
        'splitter_block_a': 'station 1',
        'splitter_block_b': 'station 2'
    }
}

num_trains = 4

optional_params = {
    'sluggishness': True,
    'sluggishness_mu': 1.5,
    'sluggishness_sigma': 0.6,
    'random_seed': 10
}

circuit = Circuit(block_ref_dict=blocks, num_trains=num_trains, optional_params=optional_params)

# run the sim
for _ in range(36000):
    circuit.step()

# question - what percent of the sim run time did each train sit idle?
print("Percent of Sim Time Spent Idle:")
for train_name in circuit.trains:
    print(round(100*circuit.trains[train_name].total_seconds_held / circuit.time, 2))

num_riders_per_train = 24
avg_cycles_completed = sum([circuit.trains[train].circuits_completed for train in circuit.trains]) / len(circuit.trains)
avg_cycles_per_hour = avg_cycles_completed * 3600 / circuit.time
total_cycles_per_hour = avg_cycles_per_hour * len(circuit.trains)
total_hourly_capacity = round(num_riders_per_train * total_cycles_per_hour, 1)
print(f"Average Hourly Capacity with {num_trains} trains: {total_hourly_capacity}")
