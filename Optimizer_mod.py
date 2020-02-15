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