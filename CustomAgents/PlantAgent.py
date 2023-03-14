import mesa
import numpy as np

class PlantAgent(mesa.Agent):
    def __init__(self, id, model, reward, plant_type, nectar_storage = 100, pollen_storage = 100):
        super().__init__(f"plant_{id}", model)
        self.reward = reward
        self.plant_type = plant_type
        self.nectar_storage = nectar_storage
        self.pollen_storage = pollen_storage

    def step(self):
        # ogni giorno mi si ricarica il nettare e polline
        # nettare e polline si ricarica anche ad ogni step (poco)

        pass

    def daily_step(self):
        pass

    '''
    Returns nectar reward based on its minimum and maximum reward. 
    If it hasn't got enough nectar, it returns all the nectar the plant has.
    The nectar reward is subtracted from the plant nectar storage.
    '''
    def getNectar(self):
        nectar_reward = np.random.uniform(self.reward[0], self.reward[1])
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
    def getPollen(self):
        pollen_reward = np.random.uniform(0, 1)
        if (self.pollen_storage > pollen_reward):
            self.pollen_storage -= pollen_reward
        else:
            pollen_reward = self.pollen_storage
            self.pollen_storage = 0
        return pollen_reward