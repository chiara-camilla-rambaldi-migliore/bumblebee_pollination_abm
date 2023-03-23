import mesa

class ColonyAgent(mesa.Agent):
    def __init__(self, id, model):
        super().__init__(f"colony_{id}", model)
        self.nectar = 0
        self.pollen = 0
        self.nectar_consumption_per_bee = 1.5
        self.pollen_consumption_per_bee = 1.5
        self.population = {}

    def setQueen(self, queen: mesa.Agent):
        self.queen = queen
        self.addNewBee(queen)

    def step(self):
        pass

    def daily_step(self):
        self.useResources()

    def removeBee(self, agent: mesa.Agent):
        self.population.pop(agent.unique_id)
        pass

    def addNewBee(self, agent: mesa.Agent):
        self.population[agent.unique_id] = agent
        pass

    def useResources(self):
        self.nectar -= len(self.population)*self.nectar_consumption_per_bee
        self.pollen -= len(self.population)*self.pollen_consumption_per_bee

    def collectResources(self, bee: mesa.Agent):
        self.nectar += bee.nectar
        self.pollen += sum(bee.pollen.values())
