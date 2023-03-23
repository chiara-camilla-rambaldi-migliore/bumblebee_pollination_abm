import mesa
import numpy as np
from Utils import PlantStage, PlantType
from math import floor

NECTAR_STEP_RECHARGE = 0.1 #amount of recharge after a step
POLLEN_STEP_RECHARGE = 0.1 #amount of recharge after a step
SEED_AGE = 3 #maximum seed age before becoming a flower
FLOWER_AGE = 10 #maximum flower age until death
INITIAL_SEED_PROD_PROB = 0.1 #initial porbability of seed production (it takes into account the wind and rain pollination)
MAX_SEEDS = 6 #maximum number of seeds producted by the flower
SEED_PROB = 0.6 #probability of a seed to become a flower

# seed hibernation is controlled by number of days a seed need to become a flower
# the assumption is that each plant type ha only one generation per year


class PlantAgent(mesa.Agent):
    def __init__(self, id, model: mesa.Model, reward, plant_type: PlantType, plant_stage = PlantStage.SEED, nectar_storage = 100, pollen_storage = 100):
        super().__init__(f"plant_{id}", model)
        self.reward = reward
        self.plant_type = plant_type
        self.max_nectar_storage = nectar_storage
        self.max_pollen_storage = pollen_storage
        self.nectar_storage = nectar_storage
        self.pollen_storage = pollen_storage
        self.plant_stage = plant_stage
        self.seed_production_prob = INITIAL_SEED_PROD_PROB if self.plant_stage == PlantStage.FLOWER else 0
        self.age = 0

    def __del__(self):
        print("Deleted plant")

    def step(self):
        if self.plant_stage == PlantStage.FLOWER:
            bumblebees_in_same_position = self.model.grid.get_cell_bumblebee_list_contents(self.pos)
            for bumblebee in bumblebees_in_same_position:
                self.updateSeedProductionProb(bumblebee)

            # nettare e polline si ricaricano anche ad ogni step (poco)
            self.resourcesRecharge(NECTAR_STEP_RECHARGE, POLLEN_STEP_RECHARGE)

        pass

    def dailyStep(self):
        self.age += 1
        self.updateStage()
        # ogni giorno mi si ricarica il nettare e polline
        if self.plant_stage == PlantStage.FLOWER:
            self.completeResourcesRecharge()

    def updateStage(self):
        if self.plant_stage == PlantStage.SEED:
            if self.age >= SEED_AGE:
                if self.model.random.random() < SEED_PROB:
                    self.plant_stage = PlantStage.FLOWER
                    self.seed_production_prob = INITIAL_SEED_PROD_PROB
                    self.age = 0
                else:
                    self.setPlantDead()

        elif self.plant_stage == PlantStage.FLOWER:
            if self.age >= FLOWER_AGE:
                if floor(MAX_SEEDS*self.seed_production_prob) > 0:
                    self.model.createNewFlowers(floor(MAX_SEEDS*self.seed_production_prob), self)
                self.setPlantDead()

    def setPlantDead(self):
        self.plant_stage = PlantStage.DEATH
        self.model.removeDeceasedAgent(self)


    def updateSeedProductionProb(self, bumblebee: mesa.Agent):
        quantity_same_pollen = bumblebee.pollen[self.plant_type]
        quantity_other_pollen = sum(bumblebee.pollen.values()) - quantity_same_pollen
    
        self.seed_production_prob = min(
            self.seed_production_prob + ((quantity_same_pollen - quantity_other_pollen) / bumblebee.max_pollen_load), 
            1
        )

    def resourcesRecharge(self, amountNectar, amountPollen):
        if(self.nectar_storage<self.max_nectar_storage):
            self.nectar_storage = min(self.nectar_storage + amountNectar, self.max_nectar_storage)
        if(self.pollen_storage<self.max_pollen_storage):
            self.pollen_storage = min(self.pollen_storage + amountPollen, self.max_pollen_storage)

    def completeResourcesRecharge(self):
        self.resourcesRecharge(self.max_nectar_storage, self.max_pollen_storage)

    '''
    Returns nectar reward based on its minimum and maximum reward. 
    If it hasn't got enough nectar, it returns all the nectar the plant has.
    The nectar reward is subtracted from the plant nectar storage.
    '''
    def getNectar(self, ratio):
        if self.plant_stage == PlantStage.FLOWER:
            nectar_reward = np.random.uniform(self.reward[0], self.reward[1])*ratio
            if (self.nectar_storage > nectar_reward):
                self.nectar_storage -= nectar_reward
            else:
                nectar_reward = self.nectar_storage
                self.nectar_storage = 0
        else: 
            nectar_reward = 0
        return nectar_reward
    
    '''
    Returns pollen reward based on its minimum and maximum reward. 
    If it hasn't got enough pollen, it returns all the pollen the plant has.
    The pollen reward is subtracted from the plant pollen storage.
    '''
    def getPollen(self, ratio):
        if self.plant_stage == PlantStage.FLOWER:
            pollen_reward = np.random.uniform(0, 1)*ratio
            if (self.pollen_storage > pollen_reward):
                self.pollen_storage -= pollen_reward
            else:
                pollen_reward = self.pollen_storage
                self.pollen_storage = 0
        else:
            pollen_reward = 0
        return pollen_reward