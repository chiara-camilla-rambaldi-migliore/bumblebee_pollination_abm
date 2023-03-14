from mesa.model import Model
from mesa.space import MultiGrid
from mesa import DataCollector
import math
from CustomAgents.PlantAgent import PlantAgent
from CustomAgents.BeeAgent import BeeAgent
from CustomTime import RandomActivationByTypeOrdered

# metti i bombi ai bordi del parco dove c'è il bosco, un possibile parametro è la forma dello sfalcio,
# un altro parametro è la dezanzarizzazione, un obiettivo è la vivibilità del parco.

def computeTotalPollen(model):
    total_pollen = 0
    for agent in model.schedule.agents:
        if isinstance(agent, BeeAgent):
            for pollen in agent.pollen.values():
                total_pollen += pollen
    return total_pollen

class Schelling(Model):
    """
    Model class for the Schelling segregation model.
    """

    def __init__(self, width=20, height=20, plant_density=0.8, bee_density=0.2, no_mow_pc=0.2):
        """ """
        self.type_ordered_keys = self.getOrderedKeys()
        self.width = width
        self.height = height
        self.plant_density = plant_density
        self.bee_density = bee_density
        self.no_mow_pc = no_mow_pc

        self.schedule = RandomActivationByTypeOrdered(self)
        self.grid = MultiGrid(width, height, torus=False)

        self.datacollector = DataCollector(
            model_reporters={"Total pollen": computeTotalPollen},
            agent_reporters={
                "Nectar": lambda agent: agent.nectar if isinstance(agent, BeeAgent) else None
            }
        )

        # Set up agents
        # We use a grid iterator that returns
        # the coordinates of a cell as well as
        # its contents. (coord_iter)
        bee_id = 0
        plant_id = 0
        plant_types_quantity = 2
        for cell in self.grid.coord_iter():
            x = cell[1]
            y = cell[2]
            (x_min, y_min), (x_max, y_max) = self.getCoordForPlants()
            if x >= x_min and x <= x_max and y >= y_min and y <= y_max and self.random.random() < self.plant_density:
                if self.random.random() < 0.5:
                    plant_type = 1
                    reward = (0.4, 0.5)
                else:
                    plant_type = 0
                    reward = (0.35, 0.55)
                    
                agent = PlantAgent(plant_id, self, reward, plant_type)
                plant_id += 1
                self.grid.place_agent(agent, (x, y))
                self.schedule.add(agent)
            if self.random.random() < self.bee_density:
                agent = BeeAgent(bee_id, self, plant_types_quantity)
                bee_id += 1
                self.grid.place_agent(agent, (x, y))
                self.schedule.add(agent)

        self.running = True
        self.datacollector.collect(self)

    def getOrderedKeys(self):
        return [BeeAgent, PlantAgent]

    def step(self):
        """
        Run one step of the model. If All agents are happy, halt the model.
        """
        self.schedule.step(self.type_ordered_keys)
        # simulate days and seasons
        self.datacollector.collect(self)

    def getCoordForPlants(self):
        total_area = self.width*self.height
        no_mow_area = self.no_mow_pc*total_area
        no_mow_area_height = math.floor(no_mow_area/self.width)
        return ((0,0), (self.width-1, no_mow_area_height-1))