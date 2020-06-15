import json
import pandas as pd
import numpy as np
import jpype as jp
import os

## Constants
G = 6.674e-11

M_sun = 1.989e30
M_earth = 5.972e24
M_mars = 6.39e23
M_saturn = 5.6834e26
M_titan = 1345.5e20
M_moon = 7.34767309e22

# mu_earth = G*M_earth
mu_earth = 3.986004415e14

R_earth = 6378.1363

AU = 1.496e11
a_earth = 1 * AU

# J2_earth = 1.08262668e-3
J2_earth = 1.0826362e-3


def design_spacecraft(file_name, resources_path="./inputs/VASSAR_resources", print_bool=False, detabase_update=False,
                      debug_prints=False):
    # -Main spacecraft design function, outputs a json file with updated sizing values-
    # Read input file
    instrument_lists = get_instrument_lists(file_name)
    orbit_lists = get_orbit_lists(file_name)

    if detabase_update:
        update_database(file_name, resources_path)

    if debug_prints:
        print()
        print("Spacecraft Sizing Inputs:")
        print(instrument_lists)
        print(orbit_lists)

    # Start Java Virtual Machine
    start_JVM()

    # Create designs from input sensors and orbits
    designs = []
    for i in range(len(instrument_lists)):
        if debug_prints:
            print("Designing Spacecraft Number " + str(i + 1) + "...")
        design = make_design(resources_path, instrument_lists[i], orbit_lists, i)
        designs.append(design)

    # Update designs in input JSON file and create new
    design_json = design_to_json(file_name, designs, print_bool, debug_prints)

    # Shut down Java Virtual Machine
    end_JVM()

    return design_json


def arch_eval(file_name, resources_path="./inputs/VASSAR_resources", print_bool=False, detabase_update=False,
              debug_prints=False):
    # -Main spacecraft design function, outputs a json file with updated sizing values-
    # Read input file
    instrument_lists = get_instrument_lists(file_name)
    orbit_lists = get_orbit_lists(file_name)

    if detabase_update:
        update_database(file_name, resources_path)

    if debug_prints:
        print()
        print("Spacecraft Sizing Inputs:")
        print(instrument_lists)
        print(orbit_lists)

    # Start Java Virtual Machine
    start_JVM()

    # Create designs from input sensors and orbits
    designs = []
    for i in range(len(instrument_lists)):
        if debug_prints:
            print("Designing Spacecraft Number " + str(i + 1) + "...")
        design = eval_design(resources_path, instrument_lists, orbit_lists, i)
        designs.append(design)

    # Update designs in input JSON file and create new
    design_json = design_to_json(file_name, designs, print_bool, debug_prints)

    # Package outputs
    eval = [0.0, 0.0]
    eval[0] = designs[0].get(0).getScience()
    eval[1] = designs[0].get(0).getCost()

    # Shut down Java Virtual Machine
    end_JVM()

    return eval


def get_instrument_lists(file_name):
    # -Returns the Instrument lists from input JSON-
    # Open file
    filePath = "./inputs/" + file_name
    with open(filePath) as f:
        input_data = json.load(f)

    # Read every satellite in space segment
    instrument_lists = []
    for i in range(len(input_data['spaceSegment'][0]['satellites'])):
        tempList = []
        for j in range(len(input_data['spaceSegment'][0]['satellites'][i]['payload'])):
            tempList.append(input_data['spaceSegment'][0]['satellites'][i]['payload'][j]['acronym'])
        instrument_lists.append(tempList)

    return instrument_lists


def get_orbit_lists(file_name):
    # -Returns the Orbit lists from input JSON-
    # Open file
    filePath = "./inputs/" + file_name
    with open(filePath) as f:
        input_data = json.load(f)

    # Read every satellite in space segment
    orbit_lists = []
    for i in range(len(input_data['spaceSegment'][0]['satellites'])):
        # Translate inputs into VASSAR format
        orbit_data = input_data['spaceSegment'][0]['satellites'][i]['orbit']
        orbit_lists.append(translate_orbit(orbit_data))

    return orbit_lists


def update_database(file_name, resources_path):
    filePath = "./inputs/" + file_name
    with open(filePath) as f:
        input_data = json.load(f)

    old_instruments = pd.read_excel(resources_path + r"\problems\DSHIELD\xls\Instrument Capability Definition.xls",
                                    "CHARACTERISTICS")
    name_list = old_instruments._getitem_column("Name").get_values().__array__()
    old_mass_list = old_instruments._getitem_column("mass# nil").get_values().__array__()
    old_x_dim_list = old_instruments._getitem_column("dimension-x# nil").get_values().__array__()
    old_y_dim_list = old_instruments._getitem_column("dimension-y# nil").get_values().__array__()
    old_z_dim_list = old_instruments._getitem_column("dimension-z# nil").get_values().__array__()
    old_power_list = old_instruments._getitem_column("mass# nil").get_values().__array__()

    x = 1


def translate_orbit(orbit_data):
    # -Translate inputs into VASSAR format-
    # Initialize result and unpackage input
    type = ""
    h = 0.0
    inc = ""

    a = orbit_data['semimajorAxis']
    i = orbit_data['inclination']
    e = orbit_data['eccentricity']
    arg = orbit_data['periapsisArgument']
    raan = orbit_data['rightAscensionAscendingNode']
    anom = orbit_data['trueAnomaly']
    epoch = orbit_data['epoch']
    time = orbit_data['time']

    if e <= 0.1:
        h = int(a - R_earth)
    else:
        h = int((a - a * e) - R_earth)

    if i == 90:
        type = "LEO"
        time = "NA"
        if abs(i - 90) <= 0.1:
            inc = "polar"
        else:
            inc = "NA"
    elif is_sso(a, e, i):
        type = "SSO"
        inc = "SSO"
    elif is_geo(a):
        type = "GEO"
        if abs(i - 90) <= 0.1:
            inc = "polar"
        else:
            inc = "NA"
    else:
        type = "LEO"
        time = "NA"
        if abs(i - 90) <= 0.1:
            inc = "polar"
        else:
            inc = "NA"

    return type + "-" + str(h) + "-" + inc + "-" + time


def is_sso(a, e, i):
    # -Returns true if orbit is sun synchronous-
    n = np.sqrt(mu_earth / np.power(a, 3))
    p = a * (1 - np.power(e, 2))
    i_sso = (180 / np.pi) * np.arccos(-1.227 * 10e-4 * (1 / n) * (np.power(p, 2) / np.power(R_earth, 2)))

    return abs(i - i_sso) <= 0.01


def is_geo(a):
    # -Returns true if orbit is Geostationary-
    T = 2 * np.pi * np.sqrt(np.power(a, 3) / mu_earth)
    return abs(T - 24 * 3600) <= 60


def make_design(resources_path, instrument_list, orbit_list, i):
    # -Returns design given a list of instruments and orbital parameters-
    params = jp.JClass("seakers.vassar.problems.Assigning.DSHIELDParams")(instrument_list,
                                                                          jp.JString("SMAP"),
                                                                          jp.JString(resources_path),
                                                                          jp.JString("CRISP-ATTRIBUTES"),
                                                                          jp.JString("test"), jp.JString("normal"))

    design = params.archSize(resources_path, orbit_list[0][i])

    return design


def eval_design(resources_path, instrument_list, orbit_list, i):
    # -Returns design given a list of instruments and orbital parameters-
    params = jp.JClass("seakers.vassar.problems.Assigning.DSHIELDParams")(instrument_list[0],
                                                                          jp.JString("SMAP"),
                                                                          jp.JString(resources_path),
                                                                          jp.JString("CRISP-ATTRIBUTES"),
                                                                          jp.JString("test"), jp.JString("normal"))

    design = params.archEval(resources_path, orbit_list[0][i])

    return design


def design_to_json(file_name, designs, print, debug_prints):
    # -Returns old input json with updated designs. Can print to a text file-
    # open file
    filePath = "./inputs/" + file_name
    with open(filePath) as f:
        input_data = json.load(f)

    # change design parameters
    out_data = update_json(input_data, designs, debug_prints)

    # print file
    if print:
        print_json(file_name, out_data, debug_prints)
    return out_data


def update_json(input_data, designs, debug_prints):
    # -Updates values in input json and returns an updated json object-
    for i in range(len(input_data['spaceSegment'][0]['satellites'])):
        # get design from designs list
        design_i = designs[i].get(0)

        # update values in json file
        sat_dims = design_i.getValue("satellite-dimensions").split()
        volume = float(sat_dims[0]) * float(sat_dims[1]) * float(sat_dims[2])

        input_data['spaceSegment'][0]['satellites'][i]['mass'] = round(float(design_i.getValue("satellite-dry-mass")),
                                                                       3)
        input_data['spaceSegment'][0]['satellites'][i]['dryMass'] = round(
            float(design_i.getValue("satellite-dry-mass")), 3)
        input_data['spaceSegment'][0]['satellites'][i]['volume'] = round(volume, 3)
        input_data['spaceSegment'][0]['satellites'][i]['power'] = round(
            float(design_i.getValue("satellite-BOL-power#")), 3)
        input_data['spaceSegment'][0]['satellites'][i]['adcs']['mass'] = round(float(design_i.getValue("ADCS-mass#")),
                                                                               3)
        input_data['spaceSegment'][0]['satellites'][i]['adcs']['type'] = design_i.getValue("ADCS-type")

        if debug_prints:
            print("     Satellite dry mass  [kg]: " + str(design_i.getValue("satellite-dry-mass")))
            print("     Satellite volume    [m^3]: " + str(volume))
            print("     Satellite power     [W]: " + str(design_i.getValue("satellite-BOL-power#")))
            print("     ADCS type           [-]: " + str(design_i.getValue("ADCS-mass#")))
            print("     ADCS mass           [kg]: " + str(design_i.getValue("ADCS-type")))

    return input_data


def print_json(file_name, design_json, debug_prints):
    with open('./outputs/' + file_name, 'w') as outfile:
        json.dump(design_json, outfile, indent=4)

    if debug_prints:
        print("Updated JSON printed to text file")


def start_JVM():
    curr_dir = os.listdir(os.getcwd() + r"\lib")

    classpath = ""
    for filename in curr_dir:
        if filename == 'seakers':
            # open seakers folder
            seakers_dir = os.listdir(os.getcwd() + r"\lib\seakers")
            for seak_filename in seakers_dir:
                file_dir = os.getcwd() + r"\lib\seakers" + r"/" + seak_filename
                classpath = os.pathsep.join((classpath, file_dir))
        elif filename == '.gradle':
            gradle_dir = os.listdir(os.getcwd() + r"\lib\.gradle")
            for gradle_filename in gradle_dir:
                file_dir = os.getcwd() + r"\lib\.gradle" + r"/" + gradle_filename
                classpath = os.pathsep.join((classpath, file_dir))
        elif filename == 'gov':
            gov_dir = os.listdir(os.getcwd() + r"\lib\gov")
            for gov_filename in gov_dir:
                file_dir = os.getcwd() + r"\lib\gov" + r"/" + gov_filename
                classpath = os.pathsep.join((classpath, file_dir))

    jp.startJVM(jp.getDefaultJVMPath(), "-ea", "-Djava.class.path=%s" % classpath)


def end_JVM():
    jp.shutdownJVM()
