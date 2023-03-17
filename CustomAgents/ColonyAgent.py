import mesa

class ColonyAgent(mesa.Agent):
    def __init__(self, id, model):
        super().__init__(f"colony_{id}", model)
        self.nectar = 0
        self.pollen = 0
        self.consumption_per_bee = 1.5

    def setQueen(self, queen: mesa.Agent):
        self.queen = queen

    def step(self):
        pass

    def daily_step(self):
        pass

    def collectResources(self, bee: mesa.Agent):
        self.nectar += bee.nectar
        self.pollen += sum(bee.pollen.values())
