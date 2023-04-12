from mesa.agent import Agent
import numpy as np
from math import floor
from Utils import BeeStage, BeeType, PlantType, ColonySize




class BeeAgent(Agent):
    """
    Bee agent
    """

    def __init__(
            self, 
            id, 
            model,
            bee_type, 
            bee_stage, 
            colony: Agent, 
            max_memory = 10,
            days_till_sampling_mode = 3,
            steps_colony_return = 10, # should be a multiple of steps per day
            bee_age_experience = 5,
            max_pollen_load = 20,
            male_percentage = 0.3,
            new_queens_percentage = 0.3,
            nest_bees_percentage = 0.3,
            #Generally, between 8 and 16 eggs are laid in this first batch.
            # When the first batch of larvae pupate (and hence no longer need feeding), 
            # the queen will generally collect more pollen and lay further batches of eggs
            max_egg = 12, #maximum number of eggs a queen can lay for every deposition
            #update the parameter based on the lifecycle of the queen (early first batch, then another batch when the first pupate and when the workers are out, the queen lay a lot of batch)
            days_per_eggs = 5, #number of days between depositions of eggs
            # In some species, such as the buff-tailed bumblebee (Bombus terrestris), 
            # the production of reproductive brood may not occur until several months after the queen has established her nest.
            queen_male_production_period = 120, #number of days after queen dishibernation for males and queen production
            hibernation_resources = (15, 15),
            stage_days = {
                BeeStage.EGG: 4,
                BeeStage.LARVAE: 13, #10-14 days
                BeeStage.PUPA: 13,
                BeeStage.BEE: {
                    # Estimates of worker longevity also vary between species and between studies, 
                    # from 13.2 days for B. terricola  to 41.3 days for B. morio  (Chapter 5)
                    # 3 to 6 weeks for B. Terrestris
                    BeeType.WORKER: 25,
                    BeeType.NEST_BEE: 30,
                    BeeType.MALE: 10,
                    BeeType.QUEEN: 20
                },
                BeeStage.QUEEN: 130 #almost all the season, then will die or killed from workers
                #BeeStage.HIBERNATION: 10 #days calculated based on days till next false March
            },
            steps_for_consfused_flower_visit = 3
        ):
        """
        Create a new bumblebe agent.

        Args:
           id: Unique identifier for the agent.
           model: model associated.
           max_memory: maximum number of reward remembered by the bee.
        """
        super().__init__(f"bee_{id}", model)

        self.days_till_sampling_mode = days_till_sampling_mode
        self.steps_colony_return = steps_colony_return # should be a multiple of steps per day
        self.bee_age_experience = bee_age_experience
        self.max_pollen_load = max_pollen_load
        self.male_percentage = male_percentage
        self.new_queens_percentage = new_queens_percentage
        self.nest_bees_percentage = nest_bees_percentage
        #Generally, between 8 and 16 eggs are laid in this first batch.
        # When the first batch of larvae pupate (and hence no longer need feeding), 
        # the queen will generally collect more pollen and lay further batches of eggs
        self.max_egg = max_egg #maximum number of eggs a queen can lay for every deposition
        #update the parameter based on the lifecycle of the queen (early first batch, then another batch when the first pupate and when the workers are out, the queen lay a lot of batch)
        self.days_per_eggs = days_per_eggs #number of days between depositions of eggs
        # In some species, such as the buff-tailed bumblebee (Bombus terrestris), 
        # the production of reproductive brood may not occur until several months after the queen has established her nest.
        self.queen_male_production_period = queen_male_production_period #number of days after queen dishibernation for males and queen production
        self.hibernation_resources = hibernation_resources
        self.stage_days = stage_days
        self.steps_for_consfused_flower_visit = steps_for_consfused_flower_visit

        self.queen_foraging_days = self.days_per_eggs + self.stage_days[BeeStage.EGG] + self.stage_days[BeeStage.LARVAE] + self.stage_days[BeeStage.PUPA]


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
        self.days_since_last_egg_batch = 0
        self.batch_laid = 0
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
        if self.bee_type == BeeType.QUEEN and self.bee_stage == BeeStage.QUEEN:
            self.collection_ratio = 1
        else:
            self.collection_ratio = (self.age+1)/self.bee_age_experience if self.age < self.bee_age_experience else 1

    def pesticideConfusion(self):
        #print(f"Bumblebee {self.unique_id} confused")
        self.max_memory = floor(self.max_memory/2)
        self.resetRewardedMemory()
        self.confused = True

    def step(self):
        if(self.bee_stage != BeeStage.HIBERNATION):
            # simulare viaggi (ogni tot step, torna alla colonia e deposita polline e nettare)
            # males never return to the colony
            if (
                (self.model.schedule.steps != 0 and self.model.schedule.steps % self.steps_colony_return == 0 and self.bee_type != BeeType.MALE) or
                (sum(self.pollen.values()) >= self.max_pollen_load)
            ):
                self.returnToColonyStep()
            else:
                #colleziona polline e nettare dalla pianta in cui sono
                # foraging workers, males and new queens
                if(
                    (
                        (self.bee_type != BeeType.NEST_BEE and self.bee_stage == BeeStage.BEE) or
                        (self.bee_type == BeeType.QUEEN and self.age < self.queen_foraging_days and self.bee_stage == BeeStage.QUEEN)
                    ) and
                    (
                        (not self.confused) or 
                        self.model.schedule.steps % self.steps_for_consfused_flower_visit == 0
                    )
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
        self.age += 1
        self.updateStage()
        if(self.bee_stage != BeeStage.HIBERNATION):
            if(self.model.schedule.days % self.days_till_sampling_mode == 0):
                self.sampling_mode = True
                self.resetRewardedMemory()
            self.updateCollectionRatio()
            if(self.bee_type == BeeType.QUEEN and self.bee_stage == BeeStage.QUEEN):
                self.days_since_last_egg_batch += 1
                if self.days_since_last_egg_batch % self.days_per_eggs == 0:
                    self.createNewEggs()
                    self.updateDaysPerEgg()

            if(self.bee_type == BeeType.MALE and self.bee_stage == BeeStage.BEE):
                self.mating()

    def updateDaysPerEgg(self):
        if (self.batch_laid == 1):
            self.days_per_eggs = self.stage_days[BeeStage.EGG]+ self.stage_days[BeeStage.LARVAE]
        elif (self.batch_laid > 1 and self.batch_laid <= 5):
            self.days_per_eggs = 5
        elif (self.batch_laid > 5 and self.batch_laid <= 32):
            self.days_per_eggs = 3
        elif (self.batch_laid > 32):
            self.days_per_eggs = 10

    def mating(self):
        # TODO check plausibility
        available_queens = list(filter(lambda a: a.bee_type == BeeType.QUEEN and a.bee_stage == BeeStage.BEE and (not a.mated), self.model.schedule.agents_by_type[BeeAgent].values()))
        if len(available_queens) > 0:
            self.model.random.shuffle(available_queens)
            queen = available_queens.pop()
            queen.mated = True

    def createNewEggs(self):
        self.batch_laid += 1
        self.days_since_last_egg_batch = 0
        #produzione uova basata su quantità di risorse nella colonia
        (colony_nectar, colony_pollen) = self.colony.getResources()
        (nect_cons, pol_cons) = self.colony.getConsumption()
        eggs = floor(min(min(colony_nectar/(20*nect_cons), self.max_egg), min(colony_pollen/(20*pol_cons), self.max_egg)))
        print(f"producing {eggs} eggs at age {self.age} with days per egg = {self.days_per_eggs}")
        if self.age  < self.queen_male_production_period:
            nest_bee_eggs = floor(self.nest_bees_percentage*eggs)
            worker_eggs = eggs-nest_bee_eggs
            self.model.createNewBumblebees(nest_bee_eggs, BeeType.NEST_BEE, self)
            self.model.createNewBumblebees(worker_eggs, BeeType.WORKER, self)
        else:
            # quantità nuove regine basata su quantità workers nella colonia
            if self.colony.getSize() == ColonySize.SMALL:
                male_percentage = 0
                new_queens_percentage = 0
            elif self.colony.getSize() == ColonySize.MEDIUM:
                male_percentage = self.male_percentage
                new_queens_percentage = 0
            elif self.colony.getSize() == ColonySize.BIG:
                male_percentage = self.male_percentage
                new_queens_percentage = self.new_queens_percentage

            male_eggs = floor(male_percentage*eggs)
            new_queen_eggs = floor(new_queens_percentage*eggs)
            eggs = eggs - male_eggs - new_queen_eggs

            self.model.createNewBumblebees(eggs, BeeType.WORKER, self)
            self.model.createNewBumblebees(male_eggs, BeeType.MALE, self)
            print("created males", male_eggs)
            self.model.createNewBumblebees(new_queen_eggs, BeeType.QUEEN, self)
            print("created new queens", new_queen_eggs)

        
        print(f"colony size: {len(self.colony.population)}")

    def updateStage(self):
        if self.bee_stage == BeeStage.EGG:
            if self.age >= self.stage_days[BeeStage.EGG]:
                self.age = 0
                self.bee_stage = BeeStage.LARVAE

        elif self.bee_stage == BeeStage.LARVAE:
            if self.age >= self.stage_days[BeeStage.LARVAE]:
                self.age = 0
                self.bee_stage =  BeeStage.PUPA
                
        elif self.bee_stage == BeeStage.PUPA:
            if self.age >= self.stage_days[BeeStage.PUPA]:
                self.age = 0
                self.bee_stage =  BeeStage.BEE
                
        elif self.bee_stage == BeeStage.BEE:
            if self.age >= self.stage_days[BeeStage.BEE][self.bee_type]:
                if(self.bee_type == BeeType.QUEEN and self.mated):
                    self.bee_stage = BeeStage.HIBERNATION
                    self.age = 0
                    self.colony.removeBee(self)
                    self.colony = None
                    print(f"New queen {self.unique_id} is hibernating")
                else:
                    self.bee_stage =  BeeStage.DEATH
                    self.setBeeDead()

        elif self.bee_stage == BeeStage.QUEEN:  
            if self.age >= self.stage_days[BeeStage.QUEEN]:
                self.bee_stage =  BeeStage.DEATH
                self.setBeeDead()
                #self.colony.setColonyDead()
        
        elif self.bee_stage == BeeStage.HIBERNATION:
            if self.model.schedule.days == 1: # TODO check
            #if self.age >= STAGE_DAYS[BeeStage.HIBERNATION]:
                # survival based on resources loaded
                # TODO check plausibility
                print("resources: ", self.nectar, sum(self.pollen.values()))
                if(self.nectar >= self.hibernation_resources[0] and sum(self.pollen.values()) >= self.hibernation_resources[1]):
                    print(f"queen {self.unique_id} starts new colony")
                    self.age = 0
                    # new colony in random position
                    colony = self.model.createNewColony(self)
                    self.colony = colony
                    self.model.grid.move_agent(self, self.colony.pos)
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
        neighbors = self.model.grid.get_plant_neighbors(self.pos, True, radius=10)
        plant_types = []
        for plant in neighbors:
            if plant.plant_type not in plant_types:
                plant_types.append(plant.plant_type)

        neighborhood = self.model.grid.get_neighborhood(self.pos, True, radius = 10)
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