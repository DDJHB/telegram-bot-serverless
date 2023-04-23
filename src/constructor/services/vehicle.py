class Vehicle:
    license: str = ""
    model: str = ""
    color: str = ""
    year: str = ""

    def __init__(self, license, model, color, year):
        self.license = license
        self.model = model
        self.color = color
        self.year = year

    def get_tuple(self) -> tuple:
        return self.license, self.model, self.color, self.year
