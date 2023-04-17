from mesa.model import Model
from bumblebee_pollination_abm.CustomMultiGrid import CustomMultiGrid
from bumblebee_pollination_abm.Utils import BeeType, BeeStage, PlantStage, PlantType, AreaConstructor, FlowerAreaType, Season
from bumblebee_pollination_abm.CustomAgents import PlantAgent, BeeAgent, ColonyAgent, TreeAgent
from bumblebee_pollination_abm.CustomTime import RandomActivationByTypeOrdered
from bumblebee_pollination_abm.CustomDataCollector import CustomDataCollector
from bumblebee_pollination_abm.setup_logger import logger
import sys


def computeIntraInterPollen(model):
    rs = []
    active_bumblebees = filter(lambda a: a.bee_stage == BeeStage.BEE or a.bee_stage == BeeStage.QUEEN, model.schedule.agents_by_type[BeeAgent].values())
    active_plants = list(filter(lambda a: a.plant_stage == PlantStage.FLOWER, model.schedule.agents_by_type[PlantAgent].values()))
    if len(active_plants) == 0:
        return 0
    plant_types = []
    for plant in active_plants:
        if plant.plant_type not in plant_types:
            plant_types.append(plant.plant_type)
    for agent in active_bumblebees:
        types = {}
        for t in plant_types:
            types[t] = 0

        for t, _ in agent.rewarded_memory:
            if t in types:
                types[t] += 1

        max_types = len(plant_types)
        max_length = agent.max_memory
        average = max_length/max_types if max_types > 0 else 0
        r = 0
        if(sum(types.values()) == 0):
            rs.append(r)
        else:
            for value in types.values():
                r += abs(value-average)
            rs.append(r)
    return sum(rs)/len(rs) if len(rs) > 0 else 0

def computeSeedProducingProbability(model):
    probs = 0
    count = 0
    for agent in model.schedule.agents_by_type[PlantAgent].values():
        if agent.plant_stage == PlantStage.FLOWER:
            probs += agent.seed_production_prob
            count += 1
        
    return probs/count if count > 0 else 0

def computPlantNectarAverage(model):
    nectar = 0
    count = 0
    for agent in model.schedule.agents_by_type[PlantAgent].values():
        if agent.plant_stage == PlantStage.FLOWER:
            nectar += agent.nectar_storage
            count += 1
        
    return nectar/count if count > 0 else 0

def computPlantPollenAverage(model):
    pollen = 0
    count = 0
    for agent in model.schedule.agents_by_type[PlantAgent].values():
        if agent.plant_stage == PlantStage.FLOWER:
            pollen += agent.pollen_storage
            count += 1
        
    return pollen/count if count > 0 else 0

# Un possibile parametro è la forma dello sfalcio


class GreenArea(Model):
    """
    Model class for the urban green area.
    The model starts in March
    """

    def __init__(
        self, 
        width=20, 
        height=20, 
        queens_quantity=2, 
        no_mow_pc=0.2,
        steps_per_day = 40,
        mowing_days = 30,
        pesticide_days = 60,
        false_year_duration = 190, #false duration of the year withouth hibernation period
        seed_max_age = {
            PlantType.SPRING_TYPE1: 0,
            PlantType.SPRING_TYPE2: 0,
            PlantType.SPRING_TYPE3: 0,
            PlantType.SUMMER_TYPE1: 70,
            PlantType.SUMMER_TYPE2: 70,
            PlantType.SUMMER_TYPE3: 70,
            PlantType.AUTUMN_TYPE1: 150,
            PlantType.AUTUMN_TYPE2: 150,
            PlantType.AUTUMN_TYPE3: 150
        },
        plant_reward = {
            PlantType.SPRING_TYPE1: (0.4, 0.5),
            PlantType.SPRING_TYPE2: (0.35, 0.55),
            PlantType.SPRING_TYPE3: (0.4, 0.55),
            PlantType.SUMMER_TYPE1: (0.4, 0.5),
            PlantType.SUMMER_TYPE2: (0.35, 0.55),
            PlantType.SUMMER_TYPE3: (0.4, 0.55),
            PlantType.AUTUMN_TYPE1: (0.4, 0.5),
            PlantType.AUTUMN_TYPE2: (0.35, 0.55),
            PlantType.AUTUMN_TYPE3: (0.4, 0.55)
        },
        woods_drawing = True,
        flower_area_type = FlowerAreaType.SOUTH_SECTION,
        bumblebee_params = {
            "max_memory": 10,
            "days_till_sampling_mode": 3,
            "steps_colony_return": 10,
            "bee_age_experience": 5,
            "max_pollen_load": 20,
            "male_percentage": 0.3,
            "new_queens_percentage": 0.3,
            "nest_bees_percentage": 0.3,
            "max_egg": 12,
            "days_per_eggs": 5,
            "queen_male_production_period": 120,
            "hibernation_resources": (15, 15),
            "stage_days": {
                BeeStage.EGG: 4,
                BeeStage.LARVAE: 13, 
                BeeStage.PUPA: 13,
                BeeStage.BEE: {
                    BeeType.WORKER: 25,
                    BeeType.NEST_BEE: 30,
                    BeeType.MALE: 10,
                    BeeType.QUEEN: 20
                },
                BeeStage.QUEEN: 130
            },
            "steps_for_consfused_flower_visit": 3
        },
        plant_params = {
            "nectar_storage": 100, 
            "pollen_storage": 100,
            "nectar_step_recharge": 0.02, #amount of recharge after a step
            "pollen_step_recharge": 0.02, #amount of recharge after a step
            "flower_age": {
                PlantType.SPRING_TYPE1: 70,
                PlantType.SPRING_TYPE2: 70,
                PlantType.SPRING_TYPE3: 70,
                PlantType.SUMMER_TYPE1: 80,
                PlantType.SUMMER_TYPE2: 80,
                PlantType.SUMMER_TYPE3: 80,
                PlantType.AUTUMN_TYPE1: 40, # it's important that the sum coincides with false year duration
                PlantType.AUTUMN_TYPE2: 40,
                PlantType.AUTUMN_TYPE3: 40
            },
            "initial_seed_prod_prob": 0.2, #initial probability of seed production (it takes into account the wind and rain pollination)
            "max_seeds": 6, #maximum number of seeds produced by the flower
            "seed_prob": 0.6, #probability of a seed to become a flower
        },
        colony_params = {
            "days_till_death": 4
        }
    ):
        """ """
        #parameters
        self.type_ordered_keys = self.getOrderedKeys()
        self.width = width
        self.height = height
        self.queens_quantity = queens_quantity
        self.no_mow_pc = no_mow_pc
        self.false_year_duration = false_year_duration
        self.seed_max_age = seed_max_age
        self.plant_reward = plant_reward
        self.steps_per_day = steps_per_day
        self.mowing_days = mowing_days
        self.pesticide_days = pesticide_days
        self.woods_drawing = woods_drawing
        self.flower_area_type = flower_area_type
        self.bumblebee_params = bumblebee_params
        self.plant_params = plant_params
        self.colony_params = colony_params

        self.areaConstructor = AreaConstructor(self.flower_area_type, self.height, self.width, self.no_mow_pc)

        self.schedule = RandomActivationByTypeOrdered(self, self.steps_per_day)
        self.grid = CustomMultiGrid(width, height, torus=False)

        self.datacollector_colonies = CustomDataCollector(
            [ColonyAgent],
            agent_reporters={
                "Nectar": "nectar",
                "Pollen": "pollen"
            }
        )
        self.datacollector_bumblebees = CustomDataCollector(
            [BeeAgent],
            model_reporters={"Intra/inter pollen": computeIntraInterPollen},
        )

        self.datacollector_plants = CustomDataCollector(
            [PlantAgent],
            model_reporters={
                "Seed Probability": computeSeedProducingProbability,
                "Plant Nectar Average": computPlantNectarAverage,
                "Plant Pollen Average": computPlantPollenAverage
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
        for _, x, y in self.grid.coord_iter():
            if self.areaConstructor.isPointInFlowerArea((x,y)):
                self.createPlantAgents(x, y)

            if (self.woods_drawing and self.areaConstructor.isPointInWoodsArea((x,y))):
                # solo per poter disegnare il bosco
                tree_agent = TreeAgent(self.tree_id, self)
                self.grid.place_agent(tree_agent, (x, y))
                self.schedule.add(tree_agent)
                self.tree_id += 1
                
        for _ in range(self.queens_quantity):
            # metti i nidi dei bombi ai bordi del parco dove c'è il bosco 
            queen_agent = BeeAgent(
                self.bee_id, 
                self, 
                BeeType.QUEEN, 
                BeeStage.QUEEN, 
                None,
                **self.bumblebee_params
            )
            colony_agent = self.createNewColony(queen_agent)
            queen_agent.colony = colony_agent
            self.bee_id += 1
            self.grid.place_agent(queen_agent, colony_agent.pos)
            self.schedule.add(queen_agent)

        self.running = True

        # self.datacollector_colonies.collect(self)
        # self.datacollector_bumblebees.collect(self)
        # self.datacollector_plants.collect(self)

    def createPlantAgents(self, x, y):
        plant_types = []
        
        rand = self.random.random()
        if rand < 0.33:
            plant_types.append((PlantType.SPRING_TYPE1, Season.SPRING))
        elif rand < 0.66:
            plant_types.append((PlantType.SPRING_TYPE2, Season.SPRING))
        else:
            plant_types.append((PlantType.SPRING_TYPE3, Season.SPRING))
            
        rand = self.random.random()
        if rand < 0.33:
            plant_types.append((PlantType.SUMMER_TYPE1, Season.SUMMER))
        elif rand < 0.66:
            plant_types.append((PlantType.SUMMER_TYPE3, Season.SUMMER))
        else:
            plant_types.append((PlantType.SUMMER_TYPE2, Season.SUMMER))

        rand = self.random.random()
        if rand < 0.33:
            plant_types.append((PlantType.AUTUMN_TYPE1, Season.AUTUMN))
        elif rand < 0.66:
            plant_types.append((PlantType.AUTUMN_TYPE2, Season.AUTUMN))
        else:
            plant_types.append((PlantType.AUTUMN_TYPE3, Season.AUTUMN))
            
        for plant_type, plant_season in plant_types:
            agent = PlantAgent(
                self.plant_id, 
                self, 
                reward = self.plant_reward[plant_type], 
                plant_type = plant_type, 
                plant_season = plant_season,
                plant_stage = PlantStage.SEED if self.seed_max_age[plant_type] > 0 else PlantStage.FLOWER, 
                seed_age = self.seed_max_age[plant_type],
                **self.plant_params
            )
            self.plant_id += 1
            self.grid.place_agent(agent, (x, y))
            self.schedule.add(agent)

    def getOrderedKeys(self):
        return [BeeAgent, PlantAgent, ColonyAgent]

    def step(self):
        """
        Run one step of the model. 
        """
        # days are simulated in the schedule
        self.schedule.step(self.type_ordered_keys)
        
        if (self.schedule.days != 0):
            # simulo taglio erba periodico
            if (self.schedule.days % self.mowing_days == 0):
                self.mowPark()
            # dezanzarizzazione con conseguente stordimento del bombo
            if (self.schedule.days % self.pesticide_days == 0 and self.schedule.steps % self.steps_per_day == 0):
                for bumblebee in self.schedule.agents_by_type[BeeAgent].values():
                    if bumblebee.bee_stage == BeeStage.BEE and bumblebee.bee_type == BeeType.WORKER:
                        bumblebee.pesticideConfusion()
            
        # self.datacollector_bumblebees.collect(self)
        # self.datacollector_plants.collect(self)

    def dailyStep(self):
        # self.datacollector_colonies.collect(self)
        pass

    def mowPark(self):
        for cell in self.grid.coord_iter():
            x = cell[1]
            y = cell[2]
            if not self.areaConstructor.isPointInFlowerArea((x,y)):
                plants = list(filter(lambda a: (isinstance(a, PlantAgent) and a.plant_stage == PlantStage.FLOWER), self.grid[x][y]))
                for plant in plants:
                    plant.setPlantDead()

    def createNewFlowers(self, qty: int, parent: PlantAgent, seed_age: int, generation: int):
        # parto dal neighborhood del fiore per mettere i semi
        radius = 6
        neighbors = self.grid.get_neighbor_cells_suitable_for_seeds(self.areaConstructor, parent.plant_season, parent.pos, True, radius = radius)

        while len(neighbors) < qty and radius < 10:
            #self.log("infinite loop potential")
            radius += 1
            neighbors = self.grid.get_neighbor_cells_suitable_for_seeds(self.areaConstructor, parent.plant_season, parent.pos, True, radius = radius)
        
        qty = min(len(neighbors), qty)
        
        self.random.shuffle(neighbors)

        for i in range(qty):
            x, y = neighbors[i]
            agent = PlantAgent(
                self.plant_id, 
                self, 
                reward = parent.reward, 
                plant_type = parent.plant_type, 
                plant_season = parent.plant_season,
                plant_stage = PlantStage.SEED if seed_age > 0 else PlantStage.FLOWER, 
                seed_age = seed_age,
                gen_number = generation,
                **self.plant_params
            )
            self.plant_id += 1
            self.grid.place_agent(agent, (x, y))
            self.schedule.add(agent)
        
        self.log(f"Day {self.schedule.days}: Created {qty} plants of type {parent.plant_type.name}, and seed age of {seed_age} days")

    def createNewBumblebees(self, qty, bumblebee_type: BeeType, parent: BeeAgent):
        for _ in range (qty):
            bumblebee = BeeAgent(
                self.bee_id, 
                self, 
                bumblebee_type, 
                BeeStage.EGG, 
                parent.colony,
                **self.bumblebee_params
            )
            parent.colony.addNewBee(bumblebee)
            self.bee_id += 1
            self.grid.place_agent(bumblebee, parent.colony.pos)
            self.schedule.add(bumblebee)

    def createNewColony(self, queen):
        pos = self.areaConstructor.getRandomPositionInWoods(self.random)
        lambda_func = lambda a: not isinstance(a, TreeAgent)
        agents_same_pos = self.grid.get_cell_custom_list_contents(lambda_func, pos)
        loop = 0
        while (len(agents_same_pos) > 0):
            if(loop >= 10):
                sys.exit("Infinite Loop")
            self.log("possible infinite loop")
            self.log(f"pos: {pos}, agents: {agents_same_pos}")
            pos = self.areaConstructor.getRandomPositionInWoods(self.random)
            loop += 1
        
        colony_agent = ColonyAgent(
            self.colony_id, 
            self,
            **self.colony_params
        )
        self.colony_id += 1
        self.grid.place_agent(colony_agent, pos)  
        self.schedule.add(colony_agent)
        colony_agent.setQueen(queen)
        return colony_agent
        
    def removeDeceasedAgent(self, agent):
        self.grid.remove_agent(agent)
        self.schedule.remove(agent)
        if(isinstance(agent, ColonyAgent)):
            self.log(f"Colony {agent.unique_id} died")

    def log(self, message):
        logger.info(message)