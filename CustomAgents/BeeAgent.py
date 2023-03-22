from mesa.agent import Agent
import numpy as np
from math import floor
from Utils import BeeStage, BeeType, PlantType

# TODO sampling mode

QUEEN_FORAGING_DAYS = 15
STEPS_COLONY_RETURN = 4 # should be a multiple of steps per day
BEE_AGE_EXPERIENCE = 5
MAX_POLLEN_LOAD = 20
MALE_PERCENTAGE = 0.3
NEW_QUEENS_PERCENTAGE = 0.1
MAX_EGG = 20 #maximum number of eggs a queen can lay for every deposition
DAYS_PER_EGGS = 20 #number of days between depositions of eggs
QUEEN_MALE_PRODUCTION_PERIOD = 150 #number of days after queen dishibernation for males and queen production
HIBERNATION_SURVIVAL_PROB = 0.8
STAGE_DAYS = {
    BeeStage.EGG: 4,
    BeeStage.LARVAE: 4,
    BeeStage.PUPA: 8,
    BeeStage.BEE: {
        BeeType.WORKER: 20,
        BeeType.NEST_BEE: 25,
        BeeType.MALE: 10,
        BeeType.QUEEN: 15
    },
    BeeStage.HIBERNATION: 180
}

DAYS_BEFORE_HIBERNATION = 10

class BeeAgent(Agent):
    """
    Bee agent
    """

    def __init__(self, id, model, bee_type, bee_stage, colony: Agent, max_memory = 10):
        """
        Create a new bumblebe agent.

        Args:
           id: Unique identifier for the agent.
           model: model associated.
           max_memory: maximum number of reward remembered by the bee.
        """
        super().__init__(f"bee_{id}", model)
        self.rewarded_memory = [] #list of tuple (plant_type, reward)
        self.bee_type = bee_type
        self.max_memory = max_memory
        self.last_flower_position = None
        self.nectar = 0
        self.pollen = {}
        self.colony = colony
        self.age = 0 #days
        self.mated = False
        self.bee_stage = bee_stage
        self.max_pollen_load = MAX_POLLEN_LOAD
        self.initializePollen()
        self.updateCollectionRatio()

    def initializePollen(self):
        for type in PlantType:
            self.pollen[type] = 0

    def updateCollectionRatio(self):
        # il polline e nettare collezionato aumenta con l'età
        if self.bee_type == BeeType.QUEEN:
            self.collection_ratio = 1
        else:
            self.collection_ratio = self.age/BEE_AGE_EXPERIENCE if self.age < BEE_AGE_EXPERIENCE else 1

    def pesticideConfusion(self):
        self.max_memory = floor(self.max_memory/2)
        self.rewarded_memory = []

    def step(self):
        # simulare viaggi (ogni tot step, torna alla colonia e deposita polline e nettare)
        # males never return to the colony
        if (
            (self.model.schedule.steps % STEPS_COLONY_RETURN == 0 and self.bee_type != BeeType.MALE) or
            (self.pollen >= self.max_pollen_load)
        ):
            self.returnToColonyStep()
        else:
            #colleziona polline e nettare dalla pianta in cui sono
            # foraging workers, males and new queens
            if(
                (self.bee_type != BeeType.NEST_BEE and self.bee_stage == BeeStage.BEE) or
                (self.bee_type == BeeType.QUEEN and self.age < QUEEN_FORAGING_DAYS and self.bee_stage == BeeStage.QUEEN)
            ):
                self.updatePollenNectarMemory()
                newPosition = self.getNewPosition()
                self.model.grid.move_agent(self, newPosition)


    def returnToColonyStep(self):
        self.last_flower_position = self.pos
        self.colony.collectResources(self)
        self.nectar = 0
        self.initializePollen()
        self.model.grid.move_agent(self, self.colony.pos)
        pass

    def dailyStep(self):
        self.age += 1
        self.updateCollectionRatio()
        self.updateStage()
        if(self.bee_type == BeeType.QUEEN):
            if self.model.schedule.days % DAYS_PER_EGGS == 0:
                self.createNewEggs()

    def createNewEggs(self):
        prob = self.model.random.randrange(6,10)/10
        eggs = floor(prob * MAX_EGG)
        if self.age  < QUEEN_MALE_PRODUCTION_PERIOD:
            self.model.createNewBumblebees(eggs, BeeType.WORKER, self)
        else:
            male_eggs = floor(MALE_PERCENTAGE*eggs)
            new_queen_eggs = floor(NEW_QUEENS_PERCENTAGE*eggs)
            eggs = eggs - male_eggs - new_queen_eggs

            self.model.createNewBumblebees(eggs, BeeType.WORKER, self)
            self.model.createNewBumblebees(male_eggs, BeeType.MALE, self)
            self.model.createNewBumblebees(new_queen_eggs, BeeType.QUEEN, self)

    def updateStage(self):
        if self.bee_stage == BeeStage.EGG:
            if self.age >= STAGE_DAYS[BeeStage.EGG]:
                self.age = 0
                self.bee_stage = BeeStage.LARVAE

        elif self.bee_stage == BeeStage.LARVAE:
            if self.age >= STAGE_DAYS[BeeStage.LARVAE]:
                self.age = 0
                self.bee_stage =  BeeStage.PUPA
                
        elif self.bee_stage == BeeStage.PUPA:
            if self.age >= STAGE_DAYS[BeeStage.PUPA]:
                self.age = 0
                self.bee_stage =  BeeStage.BEE
                
        elif self.bee_stage == BeeStage.BEE:
            if self.age >= STAGE_DAYS[BeeStage.BEE][self.bee_type]:
                if(self.bee_type == BeeType.QUEEN and self.mated):
                    self.bee_stage = BeeStage.HIBERNATION
                else:
                    self.bee_stage =  BeeStage.DEATH
                    self.setBeeDead()
                
        elif self.bee_stage == BeeStage.HIBERNATION:
            if self.age >= STAGE_DAYS[BeeStage.HIBERNATION]:
                if(self.model.random.random() < HIBERNATION_SURVIVAL_PROB):
                    self.age = 0
                    self.bee_stage =  BeeStage.QUEEN
                else:
                    self.setBeeDead()

    def setBeeDead(self):
        self.plant_stage = BeeStage.DEATH
        self.model.grid.remove_agent(self)

    def updatePollenNectarMemory(self):
        plant_in_same_position = self.model.grid.get_cell_plant_list_contents(self.pos)
        if len(plant_in_same_position) > 0:
            plant = plant_in_same_position[0]
            pollen_from_plant = plant.getPollen(self.collection_ratio)
            nectar_from_plant = plant.getNectar(self.collection_ratio)
            self.pollen[plant.plant_type] += pollen_from_plant
            self.nectar += nectar_from_plant
            self.enqueueNewReward(plant.plant_type, nectar_from_plant)

    def enqueueNewReward(self, plant_type, nectar_from_plant):
        self.rewarded_memory.append((plant_type, nectar_from_plant))
        if(len(self.rewarded_memory) > self.max_memory):
            self.rewarded_memory.pop(0)


    def getNewPosition(self):
        # guarda per ogni pianta se è nella memoria del bombo e scegli di visitare quella con reward maggiore e spostati in quella posizione
        neighbors = self.model.grid.get_plant_neighbors(self.pos, True, radius=8)
        plant_types = []
        for plant in neighbors:
            if plant.plant_type not in plant_types:
                plant_types.append(plant.plant_type)

        neighborhood = self.model.grid.get_neighborhood(self.pos, True, radius = 8)
        newPosition = neighborhood[np.random.randint(0, len(neighborhood))]
        if (len(neighbors) > 0):
            plantMeanRewards = self.getPlantMeanRewards()
            if(len(plantMeanRewards) > 0):
                plantMaxReward = dict(filter(lambda pair: pair[1] > 0 in plant_types, plantMeanRewards.items())) #filtra per quelli > 0
                plantMaxReward = [key for key, value in plantMaxReward.items() if value == max(plantMaxReward.values())]
                if (max_rew_len := len(plantMaxReward)) > 0:
                    if max_rew_len > 1:
                        plantMaxReward = plantMaxReward[np.random.randint(0, max_rew_len)]
                    else:
                        plantMaxReward = plantMaxReward[0]
                    plants_to_choose = list(filter(lambda n: n.plant_type == plantMaxReward, neighbors))
                    if (plant_len := len(plants_to_choose)) > 1:
                        plants_to_choose = plants_to_choose[np.random.randint(0, plant_len)]
                    else:
                        plants_to_choose = plants_to_choose[0]
                    newPosition = plants_to_choose.pos
            else:
                newPosition = neighbors[0].pos

        elif self.last_flower_position is not None:
            # vado nel posto in cui ero prima di tornare al nido
            # simulo una memoria del posto che ha dato maggior reward, ogni volta che ritornano al nido per depositare le risorse,
            # si recano successivamente verso quell'aiuola
            newPosition = self.last_flower_position
            
        return newPosition

    def getPlantMeanRewards(self):
        plantMeanRewards = {}
        if len(self.rewarded_memory) > 0:
            for (plant_type, reward) in self.rewarded_memory:
                if(plant_type not in plantMeanRewards):
                    plantMeanRewards[plant_type] = []
                plantMeanRewards[plant_type].append(reward)
            plantMeanRewards = {key: np.mean(np.array(plantMeanRewards[key])) for key in plantMeanRewards}
        
        return plantMeanRewards