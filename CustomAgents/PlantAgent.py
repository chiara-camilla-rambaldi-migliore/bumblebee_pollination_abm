import mesa
import numpy as np
from Utils import PlantStage
from ..Model import GreenArea
from CustomAgents.BeeAgent import BeeAgent
from math import floor

NECTAR_STEP_RECHARGE = 0.1
POLLEN_STEP_RECHARGE = 0.1
SEED_AGE = 3
FLOWER_AGE = 10
INITIAL_SEED_PROD_PROB = 0.1
MAX_SEEDS = 10


class PlantAgent(mesa.Agent):
    def __init__(self, id, model: GreenArea, reward, plant_type, plant_stage = PlantStage.SEED, nectar_storage = 100, pollen_storage = 100):
        super().__init__(f"plant_{id}", model)
        self.reward = reward
        self.plant_type = plant_type
        self.max_nectar_storage = nectar_storage
        self.max_pollen_storage = pollen_storage
        self.nectar_storage = nectar_storage
        self.pollen_storage = pollen_storage
        self.seed_production_prob = 0.1
        self.plant_stage = plant_stage
        self.age = 0

    def step(self):
        # TODO lifecycle of the plant
        bumblebees_in_same_position = list(filter(lambda a: isinstance(a, BeeAgent), self.model.grid.get_cell_list_contents(self.pos)))
        for bumblebee in bumblebees_in_same_position:
            self.updateSeedProductionProb(bumblebee)

        # nettare e polline si ricaricano anche ad ogni step (poco)
        self.resourcesRecharge(NECTAR_STEP_RECHARGE, POLLEN_STEP_RECHARGE)

        pass

    def dailyStep(self):
        self.updateStage()
        # ogni giorno mi si ricarica il nettare e polline
        if self.plant_stage == PlantStage.FLOWER:
            self.completeResourcesRecharge()
        elif self.plant_stage == PlantStage.DEATH:
            self.model.createNewFlowers(floor(MAX_SEEDS*self.seed_production_prob), self)

    def updateStage(self):
        if self.plant_stage == PlantStage.SEED:
            if self.age > SEED_AGE:
                self.plant_stage = PlantStage.FLOWER
        elif self.plant_stage == PlantStage.FLOWER:
            if self.age > SEED_AGE+FLOWER_AGE:
                self.plant_stage = PlantStage.DEATH

    def updateSeedProductionProb(self, bumblebee: BeeAgent):
        quantity_same_pollen = bumblebee.pollen[self.plant_type]
        quantity_other_pollen = sum(bumblebee.pollen.values()) - quantity_same_pollen
    
        self.seed_production_prob = min(
            ((quantity_same_pollen - quantity_other_pollen) / bumblebee.max_pollen_load) * 0.1, 
            1
        )

    def resourcesRecharge(self, amountNectar, amountPollen):
        if(self.nectar_storage<self.max_nectar_storage):
            self.nectar_storage = min(self.nectar_storage + amountNectar, self.max_nectar_storage)
        if(self.pollen_storage<self.max_pollen_storage):
            self.pollen_storage = min(self.pollen_storage + amountPollen, self.max_pollen_storage)

    def completeResourcesRecharge(self):
        self.resourcesRecharge(self, self.max_nectar_storage, self.max_pollen_storage)

    '''
    Returns nectar reward based on its minimum and maximum reward. 
    If it hasn't got enough nectar, it returns all the nectar the plant has.
    The nectar reward is subtracted from the plant nectar storage.
    '''
    def getNectar(self, ratio):
        nectar_reward = np.random.uniform(self.reward[0], self.reward[1])*ratio
        if (self.nectar_storage > nectar_reward):
            self.nectar_storage -= nectar_reward
        else:
            nectar_reward = self.nectar_storage
            self.nectar_storage = 0
        return nectar_reward
    
    '''
    Returns pollen reward based on its minimum and maximum reward. 
    If it hasn't got enough pollen, it returns all the pollen the plant has.
    The pollen reward is subtracted from the plant pollen storage.
    '''
    def getPollen(self, ratio):
        pollen_reward = np.random.uniform(0, 1)*ratio
        if (self.pollen_storage > pollen_reward):
            self.pollen_storage -= pollen_reward
        else:
            pollen_reward = self.pollen_storage
            self.pollen_storage = 0
        return pollen_reward