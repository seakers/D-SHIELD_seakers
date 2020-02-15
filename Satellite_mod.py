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