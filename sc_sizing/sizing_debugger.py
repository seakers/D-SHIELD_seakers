import sc_sizing.vassar as vp

# input locations
file_name = 'power_vs_mass.json'

# Start Java Virtual Machine
vp.start_JVM()

#design spacecraft and create output
#designs_json = vp.arch_design(file_name, print_bool=True, debug_prints=True, detabase_update=True)
#designs_eval = vp.arch_eval(file_name)
#change = vp.change_design(file_name, "payload-power", 100, prints=True)
ppower = vp.solve_sat_mass_to_payload_power(file_name, 1500, prints=True)
# vp.plot_ppower_vs_sat_mass(file_name, 0, 1000, 10)


# Shut down Java Virtual Machine
vp.end_JVM()

x = 0