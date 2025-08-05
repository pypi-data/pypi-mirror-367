def add(a, b):
    return a + b

def boost(value, multiplier):
    return value * multiplier

def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("No se puede dividir entre cero")
    return a / b

def custom_boost(a, b):
    return a + b  # ajusta lógica si tienes otra fórmula


class Booster:
    def __init__(self):
        self.power = 0

    def set_power(self, value):
        self.power = value

    def increase(self):
        self.power += 1

    def decrease(self):
        self.power -= 1

    def reset(self):
        self.power = 0

    def __str__(self):
        return f"Booster con power={self.power}"

    def __repr__(self):
        return f"<Booster power={self.power}>"
