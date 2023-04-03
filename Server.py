import mesa
import random
from Model import GreenArea
from CustomAgents import PlantAgent, BeeAgent, ColonyAgent, TreeAgent
from Utils import BeeStage, BeeType, PlantStage, PlantType
from CustomModularServer import CustomModularServer


def agents_draw(agent):
    portrayal_bee = {
        BeeType.MALE: {"Shape": "circle", "r": 0.4, "Filled": "true", "Layer": 1, "Color": "#FFDC00"},
        BeeType.NEST_BEE: {"Shape": "circle", "r": 0.3, "Filled": "true", "Layer": 1, "Color": "#FFF000"},
        BeeType.WORKER: {"Shape": "circle", "r": 0.4, "Filled": "true", "Layer": 1, "Color": "#FEEA00"},
        BeeType.QUEEN: {"Shape": "circle", "r": 0.5, "Filled": "true", "Layer": 2, "Color": "#FFCC00"}
    }
    portrayal_flower = {
        PlantStage.SEED: {
            PlantType.TYPE1: {"Shape": "circle", "r": 0.3, "Filled": "true", "Layer": 0, 'Color': '#222200'},
            PlantType.TYPE2: {"Shape": "circle", "r": 0.3, "Filled": "true", "Layer": 0, 'Color': '#222200'}
        },
        PlantStage.FLOWER: {
            PlantType.TYPE1: {'Shape': 'circle', 'r': 0.3, 'Filled': 'true', 'Layer': 0, 'Color': '#FF5050'},
            PlantType.TYPE2: {'Shape': 'circle', 'r': 0.3, 'Filled': 'true', 'Layer': 0, 'Color': '#3366FF'}
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
    "height": size[0],
    "width": size[1],
    "plant_density": mesa.visualization.Slider("Plant density", 0.8, 0.1, 1.0, 0.1),
    "queens_density": mesa.visualization.Slider("Queens density", 0.003, 0, 0.01, 0.001),
    "no_mow_pc": mesa.visualization.Slider("No mow percentage", 0.2, 0, 1, 0.1),
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

server = CustomModularServer(
    GreenArea,
    [canvas_element],
    #[canvas_element, total_pollen_chart, seed_prob_chart, plant_pollen_average, nectar_chart],
    "GreenArea",
    model_params,
    verbose=False,
    max_steps=200000
)