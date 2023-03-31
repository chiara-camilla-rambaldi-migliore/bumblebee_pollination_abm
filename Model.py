from mesa.model import Model
from CustomMultiGrid import CustomMultiGrid
from mesa import DataCollector
from Utils import BeeType, BeeStage, PlantStage, PlantType, AreaConstructor, FlowerAreaType
from CustomAgents import PlantAgent, BeeAgent, ColonyAgent, TreeAgent
from CustomTime import RandomActivationByTypeOrdered

# Un possibile parametro è la forma dello sfalcio

STEPS_PER_DAY = 40
MOWING_DAYS = 30
PESTICIDE_DAYS = 60

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

        self.areaConstructor = AreaConstructor(FlowerAreaType.SOUTH_SECTION, self.height, self.width, self.no_mow_pc)

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
        self.colony_id = 0
        self.tree_id = 0
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
                (x <= r_max-1 or x >= self.width-l_max or y <= d_max-1 or y >= self.height-l_max)
            ):
                if (self.random.random() < self.queens_density):
                    # metti i nidi dei bombi ai bordi del parco dove c'è il bosco 
                    colony_agent = ColonyAgent(self.colony_id, self)
                    queen_agent = BeeAgent(self.bee_id, self, BeeType.QUEEN, BeeStage.QUEEN, colony_agent)
                    self.bee_id += 1
                    self.colony_id += 1
                    self.grid.place_agent(queen_agent, (x, y))
                    self.grid.place_agent(colony_agent, (x, y))
                    self.schedule.add(queen_agent)
                    self.schedule.add(colony_agent)
                    colony_agent.setQueen(queen_agent)

                # solo per poter disegnare il bosco
                tree_agent = TreeAgent(self.tree_id, self)
                self.grid.place_agent(tree_agent, (x, y))
                self.schedule.add(tree_agent)
                self.tree_id += 1
                
        self.running = True
        self.datacollector.collect(self)

    def getOrderedKeys(self):
        return [BeeAgent, PlantAgent, ColonyAgent]

    def step(self):
        """
        Run one step of the model. 
        """
        # days are simulated in the schedule
        self.schedule.step(self.type_ordered_keys)
        # TODO capire se è possibile skippare l'inverno
        self.datacollector.collect(self)
        if (self.schedule.days != 0):
            # simulo taglio erba periodico
            if (self.schedule.days % MOWING_DAYS == 0):
                self.mowPark()
            # dezanzarizzazione con conseguente stordimento del bombo
            if (self.schedule.days % PESTICIDE_DAYS == 0):
                for bumblebee in self.schedule.agents_by_type[BeeAgent].values():
                    if bumblebee.bee_stage == BeeStage.BEE and bumblebee.bee_type == BeeType.WORKER:
                        bumblebee.pesticideConfusion()


    def mowPark(self):
        for cell in self.grid.coord_iter():
            x = cell[1]
            y = cell[2]
            if not self.areaConstructor.isPointInFlowerArea((x,y)):
                plants = list(filter(lambda a: (isinstance(a, PlantAgent) and a.plant_stage == PlantStage.FLOWER), self.grid[x][y]))
                for plant in plants:
                    plant.setPlantDead()

    def createNewFlowers(self, qty, parent: PlantAgent):
        # parto dal neighborhood del fiore per mettere i semi
        radius = 6
        neighbors = self.grid.get_neighbor_cells_suitable_for_seeds(self.areaConstructor, parent.pos, True, radius = radius)

        while len(neighbors) < qty and radius < 10:
            print("infinite loop potential")
            radius += 1
            neighbors = self.grid.get_neighbor_cells_suitable_for_seeds(self.areaConstructor, parent.pos, True, radius = radius)
        
        qty = min(len(neighbors), qty)
        
        self.random.shuffle(neighbors)

        for i in range(qty):
            x, y = neighbors[i]
            agent = PlantAgent(self.plant_id, self, parent.reward, parent.plant_type)
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
        print(f"{BeeAgent.__name__} {agent.unique_id} died")
