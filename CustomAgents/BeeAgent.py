from mesa.agent import Agent
from .PlantAgent import PlantAgent
import numpy as np
from Utils import BeeStage
import math

class BeeAgent(Agent):
    """
    Bee agent
    """

    def __init__(self, id, model, flower_type_quantity, max_memory = 10):
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
        self.max_memory = max_memory
        self.nectar = 0
        self.pollen = {}
        self.age = 0 #days
        self.stage = BeeStage.EGG
        for i in range(flower_type_quantity):
            self.pollen[i] = 0

    def step(self):
        #colleziona polline e nettare dalla pianta in cui sono
        self.updatePollenNectarMemory()
        newPosition = self.getNewPosition()

        # simulare viaggi (ogni tot step, torna alla colonia e deposita polline e nettare)
        # il polline e nettare collezionato aumenta con l'età
        # memoria del posto che ha dato maggior reward, ogni giorno si recano verso quell'aiuola.

        self.model.grid.move_agent(self, newPosition)

    def returnToColonyStep(self):
        # only when they are fully loaded, or they have traveled too much or its night.
        # pollen is stored and used in the colony
        pass

    def daily_step(self):
        self.age += 1
        self.stage = BeeStage.newStage(self.stage, self.age)
        pass

    def updatePollenNectarMemory(self):
        plant_in_same_position = list(filter(lambda a: isinstance(a, PlantAgent), self.model.grid.get_cell_list_contents(self.pos)))
        if len(plant_in_same_position) > 0:
            plant = plant_in_same_position[0]
            pollen_from_plant = plant.getPollen()
            nectar_from_plant = plant.getNectar()
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
                plantMaxReward = dict(filter(lambda pair: int(pair[0]) in plant_types, plantMeanRewards.items()))
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