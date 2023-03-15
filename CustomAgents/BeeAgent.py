from mesa.agent import Agent
from .PlantAgent import PlantAgent
import numpy as np
from Utils import BeeStage, BeeType
from .ColonyAgent import ColonyAgent

QUEEN_FORAGING_DAYS = 15
BEE_AGE_EXPERIENCE = 5
MAX_POLLEN_LOAD = 20

class BeeAgent(Agent):
    """
    Bee agent
    """

    def __init__(self, id, model, flower_type_quantity, bee_type, bee_stage, colony: ColonyAgent, max_memory = 10):
        """
        Create a new bumblebe agent.

        Args:
           id: Unique identifier for the agent.
           model: model associated.
           flower_type_quantity: quantity of flower types present in the model.
           max_memory: maximum number of reward remembered by the bee.
        """
        super().__init__(f"bee_{id}", model)
        self.rewarded_memory = [] #list of tuple (plant_type, reward)
        self.bee_type = bee_type
        self.max_memory = max_memory
        self.nectar = 0
        self.pollen = {}
        self.colony = colony
        self.age = 0 #days
        self.queen_age = 0 # TODO decidere se resettare direttamente l'age nel momento in cui si risveglia dall'ibernazione.
        self.stage = bee_stage
        self.max_pollen_load = MAX_POLLEN_LOAD
        self.updateCollectionRatio()
        for i in range(flower_type_quantity):
            self.pollen[i] = 0

    def updateCollectionRatio(self):
        # il polline e nettare collezionato aumenta con l'età
        if self.bee_type == BeeType.QUEEN:
            self.collection_ratio = 1
        else:
            self.collection_ratio = self.age/BEE_AGE_EXPERIENCE if self.age < BEE_AGE_EXPERIENCE else 1


    def step(self):
        # simulare viaggi (ogni tot step, torna alla colonia e deposita polline e nettare)
        if (self.model.schedule.steps % 100 == 0):
            self.returnToColonyStep()
        if (self.model.schedule.steps % 1000 == 0):
            # TODO daily step centralizzato nel modello o nello scheduler
            self.daily_step()
        else:
            #colleziona polline e nettare dalla pianta in cui sono
            if(
                (self.bee_type == BeeType.WORKER or
                (self.bee_type == BeeType.QUEEN and self.queen_age < QUEEN_FORAGING_DAYS)) and
                self.stage == BeeStage.BEE
            ):
                self.updatePollenNectarMemory()
                newPosition = self.getNewPosition()
                self.model.grid.move_agent(self, newPosition)


        # TODO memoria del posto che ha dato maggior reward, ogni giorno si recano verso quell'aiuola, se non c'è cibo si spostano verso quella più vicina).
        # TODO a fine estate comincia a produrre males e queens.
        # TODO le nuove regine a inizio autunno se son riuscite ad accoppiarsi si ibernano


    def returnToColonyStep(self):
        # TODO pollen is stored and used in the colony
        self.colony.collectResources(self)
        # TODO only when they are fully loaded, or they have traveled too much or its night.
        # TODO colony uses the nectar in function of number of bees present.
        pass

    def daily_step(self):
        self.age += 1
        self.updateCollectionRatio()
        self.stage = BeeStage.newStage(self.stage, self.age)
        if(self.bee_type == BeeType.QUEEN):
            # TODO create new eggs
            pass

    def updatePollenNectarMemory(self):
        # TODO let plant produce seeds based on the quantity and variety of pollen brought by the bumblebee
        plant_in_same_position = list(filter(lambda a: isinstance(a, PlantAgent), self.model.grid.get_cell_list_contents(self.pos)))
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
        neighbors = list(filter(lambda n: isinstance(n, PlantAgent), self.model.grid.get_neighbors(self.pos, True)))
        plant_types = []
        for plant in neighbors:
            if plant.plant_type not in plant_types:
                plant_types.append(plant.plant_type)

        neighborhood = self.model.grid.get_neighborhood(self.pos, True)
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