import json
import matplotlib.pyplot as plt
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


def arch_design(file_name, resources_path="./inputs/VASSAR_resources", print_bool=False, detabase_update=False,
                      debug_prints=False, fact_list=[[]]):
    # -Main architecture design function, outputs a json file with updated sizing values-
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

    # Create designs from input sensors and orbits
    designs = make_design(resources_path, instrument_lists, orbit_lists, fact_list)

    # Update designs in input JSON file and create new
    design_json = design_to_json(file_name, designs, print_bool, debug_prints)

    return [design_json, designs]


def arch_eval(file_name, resources_path="./inputs/VASSAR_resources", print_bool=False, detabase_update=False,
              debug_prints=False, fact_list=[[]]):
    # -Main architecture evauluation function, outputs a json file with updated sizing values-
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

    # Create designs from input sensors and orbits
    results = eval_design(resources_path, instrument_lists, orbit_lists, fact_list)
    designs = results.getDesigns()

    # Package outputs
    eval = [0.0, 0.0]
    eval[0] = results.getScience()
    eval[1] = results.getCost()

    return results


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


def make_design(resources_path, instrument_lists, orbit_list, fact_list):
    # -Returns design given a list of instruments and orbital parameters-
    vassar_py = jp.JClass("seakers.vassar.utils.VassarPy")("SMAP", instrument_lists, orbit_list, jp.JString(resources_path),fact_list)
    design = vassar_py.archDesign()

    return design


def eval_design(resources_path, instrument_lists, orbit_list, fact_list):
    # -Returns design given a list of instruments and orbital parameters-
    vassar_py = jp.JClass("seakers.vassar.utils.VassarPy")("SMAP", instrument_lists, orbit_list, jp.JString(resources_path), fact_list)
    results = vassar_py.archEval()

    return results


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
        design_i = designs.get(i)

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
            print("")
            print("     Satellite dry mass  \t\t\t[kg]: " + str(design_i.getValue("satellite-dry-mass")))
            print("          Adapter mass \t\t\t\t[kg]: " + str(design_i.getValue("adapter-mass")))
            print("          ADCS mass \t\t\t\t[kg]: " + str(design_i.getValue("ADCS-mass#")))
            print("          Avionics mass \t\t\t[kg]: " + str(design_i.getValue("avionics-mass#")))
            print("          Bus mass \t\t\t\t\t[kg]: " + str(design_i.getValue("bus-mass")))
            print("          Comms OBDH mass \t\t\t[kg]: " + str(design_i.getValue("comm-OBDH-mass")))
            print("          EPS mass \t\t\t\t\t[kg]: " + str(design_i.getValue("EPS-mass#")))
            print("          Payload mass \t\t\t\t[kg]: " + str(design_i.getValue("payload-mass#")))
            print("          ADCS Propellant mass \t\t[kg]: " + str(design_i.getValue("propellant-mass-ADCS")))
            print("          Injection Propellant mass [kg]: " + str(design_i.getValue("propellant-mass-injection")))
            print("          Propulsion mass \t\t\t[kg]: " + str(design_i.getValue("propulsion-mass#")))
            print("          Solar Array mass \t\t\t[kg]: " + str(design_i.getValue("solar-array-mass")))
            print("          Structure mass \t\t\t[kg]: " + str(design_i.getValue("structure-mass#")))
            print("          Thermal mass \t\t\t\t[kg]: " + str(design_i.getValue("thermal-mass#")))
            print("")
            print("     Satellite volume \t\t\t\t[m^3]: " + str(volume))
            print("")
            print("     Satellite power \t\t\t\t[W]: " + str(design_i.getValue("satellite-BOL-power#")))
            print("          Bus BOL power \t\t\t[W]: " + str(design_i.getValue("bus-BOL-power#")))
            print("          Payload Peak power \t\t[W]: " + str(design_i.getValue("payload-peak-power#")))
            print("          Payload power \t\t\t[W]: " + str(design_i.getValue("payload-power#")))
            print("          Power Duty Cycle \t\t\t[W]: " + str(design_i.getValue("power-duty-cycle#")))
            print("")
            print("     ADCS type \t\t\t\t\t\t[-]: " + str(design_i.getValue("ADCS-mass#")))
            print("          ADCS mass \t\t\t\t[kg]: " + str(design_i.getValue("ADCS-type")))
            print("          ADCS ISP \t\t\t\t\t[m/s]: " + str(design_i.getValue("Isp-ADCS")))
            print("")

    return input_data


def print_json(file_name, design_json, debug_prints):
    with open('./outputs/' + file_name, 'w') as outfile:
        json.dump(design_json, outfile, indent=4)

    if debug_prints:
        print("Updated JSON printed to text file")


##############################
# Design Study Tools
##############################

def change_design(file_name, field, val, prints=False):
    # Size spacecraft by overriding info from data spreadsheets
    if(field == "payload-power"):
        factList = [["payload-power#", str(val)], ["payload-peak-power#", str(val)]]
    else:
        factList = [field, str(val)],

    return arch_design(file_name,fact_list=factList, debug_prints=prints)

def change_eval(file_name, field, val, prints=False):
    # Evaluate architecture by overriding info from data spreadsheets
    if(field == "payload-power"):
        factList = [["payload-power#", str(val)], ["payload-peak-power#", str(val)]]
    else:
        factList = [field, str(val)],

    return arch_eval(file_name,fact_list=factList, debug_prints=prints)

def solve_sat_mass_to_payload_power(file_name, target_mass, prints=False, design_out=False):
    # Returns the payload power req for a given spacecraft mass
    tolerance = 0.1

    ppower_u = 2000
    ppower_l = 0
    mass_mid = get_mass(file_name, ppower_u)
    i = 0

    mass_u = get_mass(file_name, ppower_u)
    if(mass_u[1] >= target_mass):
        # Error, target mass is smaller than payload mass
        return -1

    while(abs(mass_mid[0] - target_mass) > tolerance):
        ppower_mid = ppower_l + (ppower_u - ppower_l)/2
        mass_mid = get_mass(file_name, ppower_mid)

        if(mass_mid[0] <= target_mass):
            ppower_l = ppower_mid
        else:
            ppower_u = ppower_mid

        i = i + 1

        if(i > 10000):
            # time out, no solution found
            return -1

    if(design_out):
        return change_design(file_name, "payload-power", ppower_mid, prints)
    else:
        return ppower_mid

def get_mass(file_name, ppower):
    arch_design = change_design(file_name, "payload-power", ppower)
    return [float(arch_design[1].get(0).getValue("satellite-dry-mass")), float(arch_design[1].get(0).getValue("payload-mass#"))]

def plot_ppower_vs_sat_mass(filename, ppower_l, ppower_u, n):
    ppower = [0] * n
    sat_mass = [0] * n
    step = (ppower_u - ppower_l)/n
    for i in range(len(ppower)):
        if i == 0:
            ppower[i] = ppower_l
        else:
            ppower[i] = ppower[i - 1] + step

        sat_mass[i] = get_mass(filename, ppower[i])

    plt.scatter(ppower, sat_mass)
    plt.grid()
    plt.show()


##############################
# Java Virtual Machine Setup
##############################
def start_JVM():
    curr_dir = os.listdir(os.getcwd() + r"/lib")

    classpath = ""
    for filename in curr_dir:
        if filename == 'seakers':
            # open seakers folder
            seakers_dir = os.listdir(os.getcwd() + r"/lib/seakers")
            for seak_filename in seakers_dir:
                file_dir = os.getcwd() + r"/lib/seakers" + r"/" + seak_filename
                classpath = os.pathsep.join((classpath, file_dir))
        elif filename == '.gradle':
            gradle_dir = os.listdir(os.getcwd() + r"/lib/.gradle")
            for gradle_filename in gradle_dir:
                file_dir = os.getcwd() + r"/lib/.gradle" + r"/" + gradle_filename
                classpath = os.pathsep.join((classpath, file_dir))
        elif filename == 'gov':
            gov_dir = os.listdir(os.getcwd() + r"/lib/gov")
            for gov_filename in gov_dir:
                file_dir = os.getcwd() + r"/lib/gov" + r"/" + gov_filename
                classpath = os.pathsep.join((classpath, file_dir))

    jp.startJVM(jp.getDefaultJVMPath(), "-ea", "-Djava.class.path=%s" % classpath)


def end_JVM():
    jp.shutdownJVM()
