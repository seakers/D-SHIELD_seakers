import math
import numpy as np
from scipy.integrate import odeint


def mag(r):
    mag_total = 0.0
    for i in range(len(r)):
        mag_total += r[i] ^ 2

    return mag_total


def dot(r1, r2):
    if len(r1) != len(r2):
        return -1

    dot_total = 0.0
    for i in range(len(r1)):
        dot_total += r1[i] * r2[i]

    return dot_total


class Power_mod:
    # PARAMETERS
    # Position and Orientation
    r = []
    r_prev = []
    q = []
    q_prev = []
    e_sun = []
    e_sun_prev = []
    Re = 0.0

    # Plan
    plan = []

    # Power Tracking
    p_gen = 0.0
    p_use = 0.0
    p_total = 0.0
    batt = 0.0
    batt_prev = 0.0
    batt_max = 0.0

    # time tracking
    t = 0.0
    t_prev = 0.0

    def __init__(self, orbit, acs, batt_0, batt_max, t_0):
        # initializes power module
        for i in range(len(orbit.r)):
            self.r_prev.append(orbit.r[i])
            self.r.append(orbit.r[i])
            self.e_sun_prev.append(orbit.e_sun[i])
            self.e_sun.append(orbit.e_sun[i])

        self.Re = orbit.Re

        for i in range(len(acs.q)):
            self.q_prev.append(acs.q[i])

        self.bat_prev = batt_0
        self.batt_max = batt_max
        self.eclipse = self.check_eclipse()
        self.t_prev = t_0

    def update(self, orbit, acs, optimizer, sat, t):
        # updates power values and returns warnings if power consumption goes beyond power supply
        # -unpack inputs
        self.r = []
        self.e_sun = []
        self.q = []

        for i in range(len(orbit.r)):
            self.r.append(orbit.r[i])
            self.e_sun.append(orbit.e_sun[i])

        for i in range(len(acs.q)):
            self.q.append(acs.q[i])

        self.t = t

        # -calculate power generation
        power_supplies = sat.power_source
        for i in range(len(power_supplies)):
            if (power_supplies[i].getType() == "Solar"):
                # self.p_gen += calcSolarRadiance() * self.check_eclipse(orbit)
                self.eclipse = self.check_eclipse()
                power_solar  = self.calc_solar_radiance()
                self.p_gen += power_solar * self.eclipse
            else:
                self.p_gen += power_supplies[i].getVal(t)

        # -calculate power use

        # -return power status
        self.p_total = self.p_gen - self.p_use

        # -calculate state of battery charge
        if (self.p_total > 0) and (self.batt >= self.batt_max):
            # --if p_total > 0 and battery is overcharged
            # ---don't charge battery
            x = 1
        else:
            # --else, calculate battery charge vs time
            deta_t = self.t - self.t_prev
            x = 2

        # -save current values as previous values for next iteration
        self.r_prev[0] = self.r[0]
        self.r_prev[1] = self.r[1]
        self.r_prev[2] = self.r[2]

        self.q_prev[0] = self.q[0]
        self.q_prev[1] = self.q[1]
        self.q_prev[2] = self.q[2]

        self.t_prev = self.t

    def end_sim(self):
        # ends simulation, outputs results to file
        x = 1

    def check_eclipse(self):
        th = math.acos(dot(self.r, self.e_sun) / mag(self.r))
        th_min = math.asin(self.Re / mag(self.r))

        if th <= th_min:
            return True
        else:
            return False

    def calc_solar_radiance(self):
        return 1.0