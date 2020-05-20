import sc_sizing.sizing as sz
import json

# input locations
resources_path = r"C:/Users/aguil/Documents/GitHub/VASSAR_resources"
file_name = 'test_input.json'



# design spacecraft and create output
designs_json = sz.design_spacecraft(file_name, resources_path, True)