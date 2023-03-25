from mesa.model import Model
from CustomMultiGrid import CustomMultiGrid
from mesa import DataCollector
from Utils import BeeType, BeeStage, PlantStage, PlantType, AreaConstructor, FlowerAreaType
import math
from CustomAgents.PlantAgent import PlantAgent
from CustomAgents.BeeAgent import BeeAgent
from CustomAgents.ColonyAgent import ColonyAgent
from CustomTime import RandomActivationByTypeOrdered

# TODO un possibile parametro è la forma dello sfalcio
# TODO un altro parametro è la dezanzarizzazione, un obiettivo è la vivibilità del parco.
# TODO simulare dezanzarizzazione, con conseguente stordimento del bombo

STEPS_PER_DAY = 40

def computeTotalPollen(model):
    total_pollen = 0
    for agent in model.schedule.agents:
        if isinstance(agent, BeeAgent):
            for pollen in agent.pollen.values():
                total_pollen += pollen
    return total_pollen

class GreenArea(Model):
    """
    Model class for the urban green area.
    The model starts in March
    """

    def __init__(self, width=20, height=20, plant_density=0.8, queens_density=0.3, no_mow_pc=0.2):
        """ """
        self.type_ordered_keys = self.getOrderedKeys()
        self.width = width
        self.height = height
        self.plant_density = plant_density
        self.queens_density = queens_density
        self.no_mow_pc = no_mow_pc

        self.areaConstructor = AreaConstructor(FlowerAreaType.WEST_SECTION, self.height, self.width, self.no_mow_pc)

        self.schedule = RandomActivationByTypeOrdered(self, STEPS_PER_DAY)
        self.grid = CustomMultiGrid(width, height, torus=False)

        self.datacollector = DataCollector(
            #model_reporters={"Total pollen": computeTotalPollen},
            agent_reporters={
                "Nectar": lambda agent: agent.nectar if isinstance(agent, BeeAgent) else None
            }
        )

        # Set up agents
        # We use a grid iterator that returns
        # the coordinates of a cell as well as
        # its contents. (coord_iter)
        self.bee_id = 0
        self.plant_id = 0
        self.plant_types_quantity = 2
        (r_max, t_max, l_max, d_max), wood_surface = self.areaConstructor.getWoodBoundsAndSurface()
        for cell in self.grid.coord_iter():
            x = cell[1]
            y = cell[2]
            if self.areaConstructor.isPointInFlowerArea((x,y)):
                if self.random.random() < 0.5:
                    plant_type = PlantType.TYPE2
                    reward = (0.4, 0.5)
                else:
                    plant_type = PlantType.TYPE1
                    reward = (0.35, 0.55)
                    
                agent = PlantAgent(self.plant_id, self, reward, plant_type, plant_stage=PlantStage.FLOWER)
                self.plant_id += 1
                self.grid.place_agent(agent, (x, y))
                self.schedule.add(agent)
            if (
                (x <= r_max-1 or x >= self.width-l_max-1 or y <= d_max-1 or y >= self.height-l_max-1) and 
                self.random.random() < self.queens_density
            ):
                # metti i nidi dei bombi ai bordi del parco dove c'è il bosco 
                colony_agent = ColonyAgent(self.bee_id, self)
                queen_agent = BeeAgent(self.bee_id, self, BeeType.QUEEN, BeeStage.BEE, colony_agent)
                colony_agent.setQueen(queen_agent)
                self.bee_id += 1
                self.grid.place_agent(queen_agent, (x, y))
                self.grid.place_agent(colony_agent, (x, y))
                self.schedule.add(queen_agent)
                self.schedule.add(colony_agent)

        self.running = True
        self.datacollector.collect(self)

    def getOrderedKeys(self):
        return [BeeAgent, PlantAgent]

    def step(self):
        """
        Run one step of the model. 
        """
        # days are simulated in the schedule
        self.schedule.step(self.type_ordered_keys)
        # TODO simulate seasons
        self.datacollector.collect(self)
        # TODO simulare taglio erba periodico

    def createNewFlowers(self, qty, parent: PlantAgent):
        # TODO può avere senso partire dal neighborhood della pianta per far nascere i semi?
        for cell in self.grid.coord_iter():
            x = cell[1]
            y = cell[2]
            if (
                self.areaConstructor.isPointInParkBoundaries((x,y)) and 
                self.grid.is_cell_suitable_for_seed((x,y)) and
                qty > 0
            ):
                agent = PlantAgent(self.plant_id, self, parent.reward, parent.plant_type)
                qty -= 1
                self.plant_id += 1
                self.grid.place_agent(agent, (x, y))
                self.schedule.add(agent)

    def createNewBumblebees(self, qty, bumblebee_type: BeeType, parent: BeeAgent):
        for _ in range (qty):
            bumblebee = BeeAgent(self.bee_id, self, bumblebee_type, BeeStage.EGG, parent.colony)
            parent.colony.addNewBee(bumblebee)
            self.bee_id += 1
            self.grid.place_agent(bumblebee, parent.colony.pos)
            self.schedule.add(bumblebee)
        
    def removeDeceasedAgent(self, agent):
        self.grid.remove_agent(agent)
        self.schedule.remove(agent)
