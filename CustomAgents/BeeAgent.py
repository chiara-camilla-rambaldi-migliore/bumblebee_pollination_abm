from mesa.agent import Agent
import numpy as np
from math import floor
from Utils import BeeStage, BeeType, PlantType, ColonySize

DAYS_TILL_SAMPLING_MODE = 3
QUEEN_FORAGING_DAYS = 18
STEPS_COLONY_RETURN = 10 # should be a multiple of steps per day
BEE_AGE_EXPERIENCE = 5
MAX_POLLEN_LOAD = 20
MALE_PERCENTAGE = 0.3
NEW_QUEENS_PERCENTAGE = 0.1
NEST_BEES_PERCENTAGE = 0.3
#Generally, between 8 and 16 eggs are laid in this first batch.
# When the first batch of larvae pupate (and hence no longer need feeding), 
# the queen will generally collect more pollen and lay further batches of eggs
MAX_EGG = 8 #maximum number of eggs a queen can lay for every deposition
#TODO update the parameter based on the lifecycle of the queen (early first batch, then another batch when the first pupate and when the workers are out, the queen lay a lot of batch)
DAYS_PER_EGGS = 18 #number of days between depositions of eggs
# In some species, such as the buff-tailed bumblebee (Bombus terrestris), 
# the production of reproductive brood may not occur until several months after the queen has established her nest.
QUEEN_MALE_PRODUCTION_PERIOD = 150 #number of days after queen dishibernation for males and queen production
HIBERNATION_RESOURCES = (100, 100)
STAGE_DAYS = {
    BeeStage.EGG: 4,
    BeeStage.LARVAE: 14, #10-14 days
    BeeStage.PUPA: 14,
    BeeStage.BEE: {
        # Estimates of worker longevity also vary between species and between studies, 
        # from 13.2 days for B. terricola  to 41.3 days for B. morio  (Chapter 5)
        # 3 to 6 weeks for B. Terrestris
        BeeType.WORKER: 20,
        BeeType.NEST_BEE: 30,
        BeeType.MALE: 10,
        BeeType.QUEEN: 15
    },
    BeeStage.QUEEN: 160, #almost all the season, then will die or killed from workers
    BeeStage.HIBERNATION: 180
}

DAYS_BEFORE_HIBERNATION = 10
# TODO skippa l'inverno facendo si che l'ibernazione duri pochissimo (giusto un periodo di transizione per il modello)

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
        self.resetRewardedMemory() #list of tuple (plant_type, reward)
        self.bee_type = bee_type
        self.max_memory = max_memory
        self.last_flower_position = None
        self.nectar = 0
        self.pollen = {}
        self.colony = colony
        self.age = 0 #days
        self.mated = False
        self.bee_stage = bee_stage
        self.sampling_mode = True
        self.max_pollen_load = MAX_POLLEN_LOAD
        self.confused = False
        self.initializePollen()
        self.updateCollectionRatio()
    
    def __del__(self):
        pass#print("Deleted bumblebee", self.unique_id, self.bee_type.name)
    
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
        self.resetRewardedMemory()
        self.confused = True

    def step(self):
        # simulare viaggi (ogni tot step, torna alla colonia e deposita polline e nettare)
        # males never return to the colony
        if (
            (self.model.schedule.steps != 0 and self.model.schedule.steps % STEPS_COLONY_RETURN == 0 and self.bee_type != BeeType.MALE) or
            (sum(self.pollen.values()) >= self.max_pollen_load)
        ):
            self.returnToColonyStep()
        else:
            #colleziona polline e nettare dalla pianta in cui sono
            # foraging workers, males and new queens
            if(
                ((self.bee_type != BeeType.NEST_BEE and self.bee_stage == BeeStage.BEE) or
                (self.bee_type == BeeType.QUEEN and self.age < QUEEN_FORAGING_DAYS and self.bee_stage == BeeStage.QUEEN)) and
                ((not self.confused) or self.model.schedule.steps % 2 == 0)

            ):
                self.updatePollenNectarMemory()
                newPosition = self.getNewPosition()
                self.model.grid.move_agent(self, newPosition)


    def returnToColonyStep(self):
        plant_in_same_position = self.model.grid.get_cell_plant_list_contents(self.pos)
        if len(plant_in_same_position) > 0:
            self.last_flower_position = self.pos
        if(not (self.bee_type == BeeType.QUEEN and self.bee_stage == BeeStage.BEE) and
           not (self.bee_type == BeeType.MALE and self.bee_stage == BeeStage.BEE)
        ):
            self.colony.collectResources(self)
            self.nectar = 0
            self.initializePollen()
        self.model.grid.move_agent(self, self.colony.pos)
        pass

    def resetRewardedMemory(self):
        self.rewarded_memory = []

    def dailyStep(self):
        if(self.model.schedule.days % DAYS_TILL_SAMPLING_MODE == 0):
            self.sampling_mode = True
            self.resetRewardedMemory()
        self.age += 1
        self.updateCollectionRatio()
        self.updateStage()
        if(self.bee_type == BeeType.QUEEN and self.bee_stage == BeeStage.QUEEN):
            if self.age % DAYS_PER_EGGS == 0:
                self.createNewEggs()

        if(self.bee_type == BeeType.MALE and self.bee_stage == BeeStage.BEE):
            self.mating()

    def mating(self):
        # TODO check plausibility
        available_queens = list(filter(lambda a: a.bee_type == BeeType.QUEEN and a.bee_stage == BeeStage.BEE and (not a.mated), self.model.schedule.agents_by_type[BeeAgent].values()))
        if len(available_queens > 0):
            self.model.random.shuffle(available_queens)
            queen = available_queens.pop()
            queen.mated = True

    def createNewEggs(self):
        #produzione uova basata su quantità di risorse nella colonia
        (colony_nectar, colony_pollen) = self.colony.getResources()
        (nect_cons, pol_cons) = self.colony.getConsumption()
        eggs = floor(min(min(colony_nectar/(20*nect_cons), MAX_EGG), min(colony_pollen/(20*pol_cons), MAX_EGG)))
        print(f"producing {eggs} eggs")
        if self.age  < QUEEN_MALE_PRODUCTION_PERIOD:
            nest_bee_eggs = floor(NEST_BEES_PERCENTAGE*eggs)
            worker_eggs = eggs-nest_bee_eggs
            self.model.createNewBumblebees(nest_bee_eggs, BeeType.NEST_BEE, self)
            self.model.createNewBumblebees(worker_eggs, BeeType.WORKER, self)
        else:
            # quantità nuove regine basata su quantità workers nella colonia
            if self.colony.getSize() == ColonySize.SMALL:
                male_percentage = 0
                new_queens_percentage = 0
            elif self.colony.getSize() == ColonySize.MEDIUM:
                male_percentage = MALE_PERCENTAGE
                new_queens_percentage = 0
            elif self.colony.getSize() == ColonySize.BIG:
                male_percentage = MALE_PERCENTAGE
                new_queens_percentage = NEW_QUEENS_PERCENTAGE

            male_eggs = floor(male_percentage*eggs)
            new_queen_eggs = floor(new_queens_percentage*eggs)
            eggs = eggs - male_eggs - new_queen_eggs

            self.model.createNewBumblebees(eggs, BeeType.WORKER, self)
            self.model.createNewBumblebees(male_eggs, BeeType.MALE, self)
            print("created males", male_eggs)
            self.model.createNewBumblebees(new_queen_eggs, BeeType.QUEEN, self)
            print("created new queens", new_queen_eggs)

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

        elif self.bee_stage == BeeStage.QUEEN:  
            if self.age >= STAGE_DAYS[BeeStage.QUEEN]:
                self.bee_stage =  BeeStage.DEATH
                self.setBeeDead()
        
        elif self.bee_stage == BeeStage.HIBERNATION:
            if self.age >= STAGE_DAYS[BeeStage.HIBERNATION]:
                # survival based on resources loaded
                # TODO check plausibility
                print("resources: ", self.nectar, sum(self.pollen.values()))
                if(self.nectar >= HIBERNATION_RESOURCES[0] and sum(self.pollen.values()) < HIBERNATION_RESOURCES[1]):
                    self.age = 0
                    #TODO new colony in random position
                    self.bee_stage =  BeeStage.QUEEN
                else:
                    self.setBeeDead()

    def setBeeDead(self):
        self.plant_stage = BeeStage.DEATH
        self.colony.removeBee(self)
        self.model.removeDeceasedAgent(self)

    def updatePollenNectarMemory(self):
        plant_in_same_position = self.model.grid.get_cell_plant_list_contents(self.pos)
        if len(plant_in_same_position) > 0:
            plant = plant_in_same_position[0]
            pollen_from_plant = plant.getPollen(self.collection_ratio)
            nectar_from_plant = plant.getNectar(self.collection_ratio)
            self.pollen[plant.plant_type] += pollen_from_plant
            self.nectar += nectar_from_plant
            self.enqueueNewReward(plant.plant_type, nectar_from_plant)

        if len(self.rewarded_memory) == self.max_memory:
            self.sampling_mode = False

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
            if(not self.sampling_mode):
                plantMeanRewards = self.getPlantMeanRewards()
                if(len(plantMeanRewards) > 0):
                    plantMaxReward = dict(filter(lambda pair: pair[1] > 0 and pair[0] in plant_types, plantMeanRewards.items())) #filtra per quelli > 0 e con plant type presente nel vicinato
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
            else:
                newPosition = neighbors[0].pos

        elif self.last_flower_position is not None:
            # vado nel posto in cui ero prima di tornare al nido
            # simulo una memoria del posto che ha dato maggior reward, ogni volta che ritornano al nido per depositare le risorse,
            # si recano successivamente verso quell'aiuola
            newPosition = (self.last_flower_position)
            
            
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