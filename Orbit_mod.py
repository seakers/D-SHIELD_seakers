class Orbit_mod:
    r = []
    v = []
    Re = 0.0
    e_sun = []

    def __init__(self, r, v, Re, e_sun):
        for i in range(3):
            self.r[i] = r[i]
            self.v[i] = v[i]
            self.e_sun[i] = e_sun[i]
        self.Re = Re