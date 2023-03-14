import mesa
import random
from Model import Schelling, BeeAgent, PlantAgent


def agents_draw(agent):
    """
    Portrayal Method for canvas
    """
    if agent is None:
        return
    portrayal = {"Shape": "circle", "r": 0.5, "Filled": "true", "Layer": 0}

    if isinstance(agent, PlantAgent):
        if agent.plant_type == 0:
            portrayal["Color"] = ["#AA0000"]
        else:
            portrayal["Color"] = ["#0000AA"]
    else:
        portrayal["Color"] = ["#FFFF00"]
    return portrayal

size = (100, 100)

canvas_element = mesa.visualization.CanvasGrid(agents_draw, size[0], size[1], 500, 500)

model_params = {
    "height": size[0],
    "width": size[1],
    "plant_density": mesa.visualization.Slider("Plant density", 0.8, 0.1, 1.0, 0.1),
    "bee_density": mesa.visualization.Slider("Bee density", 0.1, 0.00, 1.0, 0.02),
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
    [{"Label": "Nectar", "Color": f"#{random.randint(0, 0xFFFFFF):06x}"}],
    scope="agent",
    data_collector_name='datacollector'
)

server = mesa.visualization.ModularServer(
    Schelling,
    [canvas_element, total_pollen_chart, nectar_chart],
    "Schelling",
    model_params,
)