import sc_sizing.vassar as vp

# input locations
file_name = 'test_SMAP.json'

# Start Java Virtual Machine
vp.start_JVM()

# design spacecraft and create output
designs_json = vp.arch_design(file_name, print_bool=True, debug_prints=True, detabase_update=True)
# designs_eval = vp.arch_eval(file_name)

# Shut down Java Virtual Machine
vp.end_JVM()

x = 0