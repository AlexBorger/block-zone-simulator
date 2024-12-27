# block-zone-simulator
Simulation of roller coaster block zones

This repo is a WIP.  As of now, the notebook allows for the following:

- Specify block zones and add trains to a circuit
- Run basic simulations under the following rules:
  - Every block zone can only occupy one train and has a mechanism for stopping a train at the end.
  - Each train must obtain ownership of the proceeding block zone before it may advance past the brakes in its current block zone
  - Each train must maintain ownership of its current block zone until it completely exits it, at which point it will become free
  - Each block zone has the following characteristics:
    - \# of seconds from start of zone to brakes at end of zone
    - \# of seconds to advance past the brakes and clear zone without having stopped
    - \# of seconds to advance past the brakes and clear zone from complete stop
    - E-Stop Block (yes/no): these blocks can stop a ride vehicle but cannot advance a train forward.  Being held at an E-Stop block causes a complete shutdown of the attraction.
    
The data generated by the simulation allows for calculating:

- Total Hourly Throughput of attraction in \# of cycles 
- Percent of simulation time each train spent idle (held at block due to congestion)
- Comparison of theoretical vs actual throughput when dispatch delay is introduced

More metrics and features to come are listed in todo.md.

### Example Simulation Animation
![Example Animation](Code/example_sim.gif)

This example gif shows a circuit with dual loading stations.  Track switches are used on lift 1 and final block 1, the current switch position of which is shown on the graph.  Please ignore the x and y axes!
