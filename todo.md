# TODO

1. Add transfer tracks for loading / offloading trains during operation
2. Add variable load/unload times **[DONE]**
3. Add dual/quad load synchronization
   - Splitter/Merger switches implemented allow for dual station setup **[DONE]**
   - fix issue with 2 train ops where merger/splitter switches are out of sync
4. Add real examples and analyze capacity
5. Finish moving logic into block.py, train.py **[DONE]**
6. Add more complex block functionality for rides with switch tracks
   - Beyond multi-station operation, unclear if additional switches impact throughput analysis
   - Thru-ride switches (where there is no junction with other incoming/outgoing blocks) take time and can be modeled as mandatory holds
7. Add GUI to visualize flow of operations in realtime
   - Basic gif / animation **[DONE]**
   - Add time info at each
   - Train in motion, held, etc, dictates shape/opacity/fill of marker
8. Build runbook in Google Colab for no-code operation
9. Can this simulator be used to test out different operational strategies?
   - for example, if operators learn to wait X seconds before dispatching a train, does it actually improve operations?
   - what else would we have to account for here to test that?