import sc_sizing.sizing as sz
import json

# input locations
file_name = 'test_input.json'

# design spacecraft and create output
designs_json = sz.design_spacecraft(file_name, print_bool=True, debug_prints=True)