import mesa
import random
from Model import GreenArea
from CustomAgents import PlantAgent, BeeAgent, ColonyAgent
from Utils import BeeStage, BeeType, PlantStage, PlantType
from CustomModularServer import CustomModularServer


PORTRAYAL_BEE = {
    BeeType.MALE: {"Shape": "circle", "r": 0.4, "Filled": "true", "Layer": 0, "Color": ["#FFDC00"]},
    BeeType.NEST_BEE: {"Shape": "circle", "r": 0.3, "Filled": "true", "Layer": 0, "Color": ["#FFF000"]},
    BeeType.WORKER: {"Shape": "circle", "r": 0.3, "Filled": "true", "Layer": 0, "Color": ["#FEEA00"]},
    BeeType.QUEEN: {"Shape": "circle", "r": 0.5, "Filled": "true", "Layer": 0, "Color": ["#FFCC00"]}
}
PORTRAYAL_FLOWER = {
    PlantType.TYPE1: {'Shape': 'circle', 'r': 0.3, 'Filled': 'true', 'Layer': 0, 'Color': ['#FF5050']},
    PlantType.TYPE2: {'Shape': 'circle', 'r': 0.3, 'Filled': 'true', 'Layer': 0, 'Color': ['#3366FF']}
}

def agents_draw(agent):
    """
    Portrayal Method for canvas
    """
    if agent is None:
        return
    portrayal = {"Shape": "circle", "r": 0.3, "Filled": "true", "Layer": 0}

    if isinstance(agent, PlantAgent):
        if agent.plant_stage == PlantStage.SEED:
            portrayal["Color"] = ['#222200']
        elif agent.plant_type == PlantType.TYPE1:
            portrayal["Color"] = ["#FF5050"]
        else:
            portrayal["Color"] = ["#3366FF"]
    elif isinstance(agent, BeeAgent):
        if agent.bee_type == BeeType.QUEEN:
            portrayal = {"Shape": "circle", "r": 0.5, "Filled": "true", "Layer": 0, "Color": ["#FFCC00"]}
        elif agent.bee_type == BeeType.WORKER:
            portrayal = {"Shape": "circle", "r": 0.5, "Filled": "true", "Layer": 0, "Color": ["#FEEA00"]}
        elif agent.bee_type == BeeType.MALE:
            portrayal = {"Shape": "circle", "r": 0.4, "Filled": "true", "Layer": 0, "Color": ["#FFDC00"]}
        elif agent.bee_type == BeeType.NEST_BEE:
            portrayal = {"Shape": "circle", "r": 0.3, "Filled": "true", "Layer": 0, "Color": ["#FFF000"]}
    elif isinstance(agent, ColonyAgent):
        portrayal = {"Shape": "circle", "r": 0.5, "Filled": "true", "Layer": 0, "Color": "#993300"}
    return portrayal

def new_agents_draw(agent):
    # TODO fix colors
    """
    Portrayal Method for canvas
    """
    if agent is None:
        return
    
    portrayal = {}

    if isinstance(agent, PlantAgent):
        portrayal = PORTRAYAL_FLOWER[agent.plant_type]
    elif isinstance(agent, BeeAgent):
        portrayal = PORTRAYAL_BEE[agent.bee_type]

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
    [{"Label": "Total pollen", "Color": "Blue"}],
    data_collector_name='datacollector'
)

class BeeNectarBarChart(mesa.visualization.BarChartModule):
    def __init__(
        self,
        fields,
        scope="model",
        sorting="none",
        sort_by="none",
        canvas_height=400,
        canvas_width=800,
        data_collector_name="datacollector",
    ):
        super().__init__(fields, scope, sorting, sort_by, canvas_height, canvas_width, data_collector_name)

    def render(self, model):
        current_values = []
        data_collector = getattr(model, self.data_collector_name)

        df = data_collector.get_agent_vars_dataframe().astype("float")
        latest_step = df.index.levels[0][-1]
        labelStrings = [f["Label"] for f in self.fields]
        dic = df.loc[latest_step].T.loc[labelStrings].to_dict()
        dic = dict(filter(lambda el: "bee" in el[0],dic.items()))
        current_values = list(dic.values())
        return current_values

nectar_chart = BeeNectarBarChart(
    [{"Label": "Nectar", "Color": f"#00ffcc"}],
    scope="agent",
    data_collector_name='datacollector'
)

server = CustomModularServer(
    GreenArea,
    #[canvas_element, total_pollen_chart, nectar_chart],
    [canvas_element],
    "GreenArea",
    model_params,
    verbose=False,
    max_steps=200000
)