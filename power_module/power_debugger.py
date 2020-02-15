from power_module.Power_mod import Power_mod
import numpy as np

# MOCK MODULES
class ACS_mod:
    q = []

    def __init__(self, q):
        for i in range(len(q)):
            self.q.append(q[i])


class Orbit_mod:
    r = []
    v = []
    Re = 0.0
    e_sun = []

    def __init__(self, r, v, Re, e_sun):
        for i in range(3):
            self.r.append(r[i])
            self.v.append(v[i])
            self.e_sun.append(e_sun[i])
        self.Re = Re


class Optimizer_mod:
    plan = []

    def add_task(self, task):
        self.plan.append(task)


class Plan_task:
    sensors = []
    t_m = 0.0
    d = 0.0

    def __init__(self, sensors, t_m, d):
        for i in range(len(sensors)):
            self.sensors[i] = sensors[i]
        self.t_m = t_m
        self.d = d


class Sensor:
    name = "unknown_sensor"
    pow_req = 0.0

    def __init__(self, name, power_req):
        self.name = name
        self.pow_req = power_req

        class Satellite:
            power_source = []

            def add_power_source(self, power_source):
                self.power_source.append(power_source)

        class Power_source:
            type = "unknown_type"
            P_BOL = 0.0
            P_EOL = 0.0
            T = 0.0

            def __init__(self, type, P_BOL, P_EOL, T):
                self.type = type
                self.P_BOL = P_BOL
                self.P_EOL = P_EOL
                self.T = T


# MAIN DEBUGGER
r_0 = [0, 6793, 0]
v_0 = [100.0, 0.0, 0.0]
Re = 6371
e_sun = [-1.0, 0.0, 0.0]
q_0 = [1, 0, 0, 0]

orbit = Orbit_mod(r_0, v_0, Re, e_sun)
acs = ACS_mod(q_0)
batt_0 = 275;
batt_max = 500;
t_0 = 0.0
power = Power_mod(orbit, acs, batt_0, batt_max, t_0)

t = np.linspace(t_0, 100, 100)
for i in range(t.size):
    power.update(orbit, acs, batt_0, batt_max, t[i])