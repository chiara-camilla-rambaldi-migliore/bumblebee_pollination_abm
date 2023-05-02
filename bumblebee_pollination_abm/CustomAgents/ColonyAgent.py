import mesa
from bumblebee_pollination_abm.Utils import BeeStage, ColonySize

class ColonyAgent(mesa.Agent):
    def __init__(
            self, 
            id, 
            model,
            nectar_consumption_per_bee = 0.7,
            pollen_consumption_per_bee = 1.2,
            days_till_death = 4
        ):
        super().__init__(f"colony_{id}", model)
        self.nectar = 0
        self.pollen = 0
        self.nectar_consumption_per_bee = nectar_consumption_per_bee
        self.pollen_consumption_per_bee = pollen_consumption_per_bee
        self.population = {}
        self.no_resource_days = 0
        self.age = 0
        self.days_till_death = days_till_death

    def __del__(self):
        pass#self.model.log(f"Colony {self.unique_id} died")

    def setQueen(self, queen: mesa.Agent):
        self.queen = queen
        self.addNewBee(queen)

    def step(self):
        pass

    def dailyStep(self):
        self.age += 1
        if (self.age >= self.model.false_year_duration):
            self.setColonyDead()

        self.useResources()
        if (self.pollen > 0 and self.nectar > 0):
            self.no_resource_days = 0
        else:
            self.no_resource_days += 1

        if (self.no_resource_days > self.days_till_death):
            # quando è in deficit di risorse da tot giorni, la colonia muore
            self.setColonyDead()

    def setColonyDead(self):
        for bumblebee in self.population.values():
            bumblebee.bee_stage = BeeStage.DEATH
            self.model.removeDeceasedAgent(bumblebee)
        self.population = {}
        self.model.removeDeceasedAgent(self)

    def removeBee(self, agent: mesa.Agent):
        self.population.pop(agent.unique_id)
        if(len(self.population) == 0):
            # when no more bees, the colony die
            self.setColonyDead

    def addNewBee(self, agent: mesa.Agent):
        self.population[agent.unique_id] = agent

    def useResources(self):
        self.nectar -= len(self.population)*self.nectar_consumption_per_bee
        self.pollen -= len(self.population)*self.pollen_consumption_per_bee

    def collectResources(self, bee: mesa.Agent):
        self.nectar += bee.nectar
        self.pollen += sum(bee.pollen.values())

    def getResources(self):
        return (self.nectar, self.pollen)

    def getConsumption(self):
        return (self.nectar_consumption_per_bee, self.pollen_consumption_per_bee)
    
    def getSize(self):
        # TODO check plausibility
        if len(self.population) < 90:
            return ColonySize.SMALL
        elif len(self.population) < 180:
            return ColonySize.MEDIUM
        else:
            # succesful colonies reach 500 bumblebees
            return ColonySize.BIG