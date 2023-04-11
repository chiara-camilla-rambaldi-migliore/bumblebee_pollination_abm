import mesa
import numpy as np
from Utils import PlantStage, PlantType
from math import floor
from typing import Tuple

# seed hibernation is controlled by number of days a seed need to become a flower
# the assumption is that each plant type ha only one generation per year

class PlantAgent(mesa.Agent):
    def __init__(
            self, 
            id, 
            model: mesa.Model, 
            reward: Tuple[float, float] = (0.4, 0.6), 
            plant_type: PlantType = PlantType.SPRING_TYPE1, 
            plant_stage = PlantStage.SEED, 
            seed_age = 3,
            nectar_storage = 100, 
            pollen_storage = 100, 
            nectar_step_recharge = 0.02, #amount of recharge after a step
            pollen_step_recharge = 0.02, #amount of recharge after a step
            flower_age = {
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
            initial_seed_prod_prob = 0.2, #initial probability of seed production (it takes into account the wind and rain pollination)
            max_seeds = 6, #maximum number of seeds produced by the flower
            seed_prob = 0.6 #probability of a seed to become a flower
        ):        
        super().__init__(f"plant_{id}", model)
        self.nectar_step_recharge = nectar_step_recharge #amount of recharge after a step
        self.pollen_step_recharge = pollen_step_recharge #amount of recharge after a step
        self.flower_age = flower_age
        self.initial_seed_prod_prob = initial_seed_prod_prob #initial probability of seed production (it takes into account the wind and rain pollination)
        self.max_seeds = max_seeds #maximum number of seeds produced by the flower
        self.seed_prob = seed_prob #probability of a seed to become a flower
        self.reward = reward
        self.plant_type = plant_type
        self.seed_age = seed_age #maximum seed age before becoming a flower
        self.max_nectar_storage = nectar_storage
        self.max_pollen_storage = pollen_storage
        self.nectar_storage = nectar_storage
        self.pollen_storage = pollen_storage
        self.plant_stage = plant_stage
        self.seed_production_prob = self.initial_seed_prod_prob if self.plant_stage == PlantStage.FLOWER else 0
        self.age = 0

    def __del__(self):
        pass#print("Deleted plant", self.unique_id)

    def step(self):
        if self.plant_stage == PlantStage.FLOWER:
            bumblebees_in_same_position = self.model.grid.get_cell_bumblebee_list_contents(self.pos)
            for bumblebee in bumblebees_in_same_position:
                self.updateSeedProductionProb(bumblebee)

            # nettare e polline si ricaricano anche ad ogni step (poco)
            self.resourcesRecharge(self.nectar_step_recharge, self.pollen_step_recharge)

        pass

    def dailyStep(self):
        self.age += 1
        self.updateStage()
        # ogni giorno mi si ricarica il nettare e polline
        if self.plant_stage == PlantStage.FLOWER:
            self.dailyResourcesRecharge()

    def updateStage(self):
        if self.plant_stage == PlantStage.SEED:
            if self.age >= self.seed_age:
                if self.model.random.random() < self.seed_prob:
                    self.plant_stage = PlantStage.FLOWER
                    # print(f"Plant of type {self.plant_type.name} is born")
                    self.seed_production_prob = self.initial_seed_prod_prob
                    self.age = 0
                else:
                    self.setPlantDead()

        elif self.plant_stage == PlantStage.FLOWER:
            if self.age >= self.flower_age[self.plant_type]:
                if floor(self.max_seeds*self.seed_production_prob) > 0:
                    new_seed_age = (self.model.false_year_duration - self.model.schedule.days) + self.model.days_per_season[self.plant_type]
                    self.model.createNewFlowers(floor(self.max_seeds*self.seed_production_prob), self, new_seed_age)
                self.setPlantDead()

    def setPlantDead(self):
        self.plant_stage = PlantStage.DEATH
        self.model.removeDeceasedAgent(self)


    def updateSeedProductionProb(self, bumblebee: mesa.Agent):
        quantity_same_pollen = bumblebee.pollen[self.plant_type]
        quantity_other_pollen = (sum(bumblebee.pollen.values()) - quantity_same_pollen) #TODO control plausibility
    
        self.seed_production_prob = min(
            self.seed_production_prob + ((quantity_same_pollen - quantity_other_pollen) / bumblebee.max_pollen_load), 
            1
        )

    def resourcesRecharge(self, amountNectar, amountPollen):
        if(self.nectar_storage<self.max_nectar_storage):
            self.nectar_storage = min(self.nectar_storage + amountNectar, self.max_nectar_storage)
        if(self.pollen_storage<self.max_pollen_storage):
            self.pollen_storage = min(self.pollen_storage + amountPollen, self.max_pollen_storage)

    def dailyResourcesRecharge(self):
        self.resourcesRecharge(self.nectar_step_recharge*20, self.pollen_step_recharge*20)

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