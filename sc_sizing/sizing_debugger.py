import sc_sizing.vassar as vp

# input locations
file_name = 'test_SMAP.json'

# design spacecraft and create output
designs_json = vp.design_spacecraft(file_name, print_bool=True, debug_prints=True, detabase_update=True)
#designs_eval = vp.arch_eval(file_name)
x = 0