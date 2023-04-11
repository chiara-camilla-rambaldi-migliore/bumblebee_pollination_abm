from Model import GreenArea
import concurrent.futures as futures
import time
from Utils import PlantType, BeeType, BeeStage, FlowerAreaType

def getModels():
    size = (50, 50)

    model_params = {
        "width": size[0], 
        "height": size[1], 
        "queens_quantity": 2, 
        "no_mow_pc": 0.2,
        "steps_per_day": 40,
        "mowing_days": 30,
        "pesticide_days": 60,
        "false_year_duration": 190, #false duration of the year withouth hibernation period
        "seed_max_age": {
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
        "plant_reward": {
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
        "woods_drawing": True,
        "flower_area_type": FlowerAreaType.SOUTH_SECTION,
        "bumblebee_params": {
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
            }
        },
        "plant_params": {
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
        "colony_params": {
            "days_till_death": 4
        }
    }

    models = []
    for _ in range(5):
        models.append(GreenArea(**model_params))

    return models


def startModel(model):
    for i in range(7600):
        model.step()


def processJobs():
    models = getModels()

    # Multiprocessing
    proc_res = []
    MAX_CORES = 8


    start_time = time.time()

    with futures.ProcessPoolExecutor(max_workers=MAX_CORES) as executor:
        for model in models:
            proc_res.append(
                executor.submit(
                    startModel, model
                )
            )

    for i in range(len(proc_res)):
        try:
            proc_res[i].result()
            print(f"Process {i} terminated correctly")
        except Exception as ex:
            print(f"Error in process {i}: [{ex}]")

    print(f"Elapsed time: {time.time() - start_time}")
if __name__ == '__main__':
    processJobs()