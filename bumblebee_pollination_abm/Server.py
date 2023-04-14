import mesa
import random
from bumblebee_pollination_abm.Model import GreenArea
from bumblebee_pollination_abm.CustomAgents import PlantAgent, BeeAgent, ColonyAgent, TreeAgent
from bumblebee_pollination_abm.Utils import BeeStage, BeeType, PlantStage, PlantType, FlowerAreaType
from bumblebee_pollination_abm.CustomModularServer import CustomModularServer


def agents_draw(agent):
    portrayal_bee = {
        BeeType.MALE: {"Shape": "circle", "r": 0.4, "Filled": "true", "Layer": 1, "Color": "#FFDC00"},
        BeeType.NEST_BEE: {"Shape": "circle", "r": 0.3, "Filled": "true", "Layer": 1, "Color": "#FFF000"},
        BeeType.WORKER: {"Shape": "circle", "r": 0.4, "Filled": "true", "Layer": 1, "Color": "#FEEA00"},
        BeeType.QUEEN: {"Shape": "circle", "r": 0.5, "Filled": "true", "Layer": 2, "Color": "#FFCC00"}
    }
    portrayal_flower = {
        PlantStage.SEED: {
            PlantType.SPRING_TYPE1: {"Shape": "circle", "r": 0.1, "Filled": "true", "Layer": 0, 'Color': '#222200'},
            PlantType.SPRING_TYPE2: {"Shape": "circle", "r": 0.1, "Filled": "true", "Layer": 0, 'Color': '#222200'},
            PlantType.SPRING_TYPE3: {"Shape": "circle", "r": 0.1, "Filled": "true", "Layer": 0, 'Color': '#222200'},
            PlantType.SUMMER_TYPE1: {"Shape": "circle", "r": 0.1, "Filled": "true", "Layer": 0, 'Color': '#222200'},
            PlantType.SUMMER_TYPE2: {"Shape": "circle", "r": 0.1, "Filled": "true", "Layer": 0, 'Color': '#222200'},
            PlantType.SUMMER_TYPE3: {"Shape": "circle", "r": 0.1, "Filled": "true", "Layer": 0, 'Color': '#222200'},
            PlantType.AUTUMN_TYPE1: {"Shape": "circle", "r": 0.1, "Filled": "true", "Layer": 0, 'Color': '#222200'},
            PlantType.AUTUMN_TYPE2: {"Shape": "circle", "r": 0.1, "Filled": "true", "Layer": 0, 'Color': '#222200'},
            PlantType.AUTUMN_TYPE3: {"Shape": "circle", "r": 0.1, "Filled": "true", "Layer": 0, 'Color': '#222200'}
        },
        PlantStage.FLOWER: {
            PlantType.SPRING_TYPE1: {'Shape': 'circle', 'r': 0.3, 'Filled': 'true', 'Layer': 1, 'Color': '#FF5050'},
            PlantType.SPRING_TYPE2: {'Shape': 'circle', 'r': 0.3, 'Filled': 'true', 'Layer': 1, 'Color': '#3366FF'},
            PlantType.SPRING_TYPE3: {"Shape": "circle", "r": 0.3, "Filled": "true", "Layer": 1, 'Color': '#FF66FF'},
            PlantType.SUMMER_TYPE1: {"Shape": "circle", "r": 0.3, "Filled": "true", "Layer": 1, 'Color': '#99ddff'},
            PlantType.SUMMER_TYPE2: {"Shape": "circle", "r": 0.3, "Filled": "true", "Layer": 1, 'Color': '#d580ff'},
            PlantType.SUMMER_TYPE3: {"Shape": "circle", "r": 0.3, "Filled": "true", "Layer": 1, 'Color': '#ff80aa'},
            PlantType.AUTUMN_TYPE1: {"Shape": "circle", "r": 0.3, "Filled": "true", "Layer": 1, 'Color': '#ff4d4d'},
            PlantType.AUTUMN_TYPE2: {"Shape": "circle", "r": 0.3, "Filled": "true", "Layer": 1, 'Color': '#ff8533'},
            PlantType.AUTUMN_TYPE3: {"Shape": "circle", "r": 0.3, "Filled": "true", "Layer": 1, 'Color': '#ffcccc'}
        }
    }
    portrayal_colony = {"Shape": "circle", "r": 0.5, "Filled": "true", "Layer": 1, "Color": "#993300"}
    portrayal_tree = {"Shape": "rect", "h": 1, "w": 1, "Filled": "true", "Layer": 0, "Color": "#009900"}

    """
    Portrayal Method for canvas
    """
    if agent is None:
        return

    if isinstance(agent, PlantAgent):
        portrayal = portrayal_flower[agent.plant_stage][agent.plant_type]
    elif isinstance(agent, BeeAgent):
        portrayal = portrayal_bee[agent.bee_type]
    elif isinstance(agent, ColonyAgent):
        portrayal = portrayal_colony
    else:
        portrayal = portrayal_tree

    return portrayal

size = (50, 50)

canvas_element = mesa.visualization.CanvasGrid(agents_draw, size[0], size[1], 600, 600)

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
    "flower_area_type": FlowerAreaType.SOUTH_SECTION.value,
    "bumblebee_params": {
        "days_till_sampling_mode": 3,
        "steps_colony_return": 10,
        "bee_age_experience": 10,
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
        },
        "steps_for_consfused_flower_visit": 3
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

total_pollen_chart = mesa.visualization.ChartModule(
    [{"Label": "Intra/inter pollen", "Color": "Blue"}],
    data_collector_name='datacollector_bumblebees'
)


seed_prob_chart = mesa.visualization.ChartModule(
    [{"Label": "Seed Probability", "Color": "Res"}],
    data_collector_name='datacollector_plants'
)

nectar_chart = mesa.visualization.BarChartModule(
    [{"Label": "Nectar", "Color": f"#00ffcc"}, {"Label": "Pollen", "Color": f"#ff0066"}],
    scope="agent",
    data_collector_name='datacollector_colonies'
)

plant_pollen_average = mesa.visualization.ChartModule(
    [{"Label": "Plant Nectar Average", "Color": "#00ffcc"}, {"Label": "Plant Pollen Average", "Color": "#ff0066"}],
    data_collector_name='datacollector_plants'
)

class TimeElement(mesa.visualization.TextElement):
    def __init__(self):
        pass

    def render(self, model):
        return f"Days: {model.schedule.days} \tYears: {model.schedule.years}"
    
time_element = TimeElement()

server = CustomModularServer(
    GreenArea,
    [canvas_element, time_element],
    #[canvas_element, time_element, total_pollen_chart, seed_prob_chart, plant_pollen_average, nectar_chart],
    "GreenArea",
    model_params,
    verbose=False,
    max_steps=200000
)