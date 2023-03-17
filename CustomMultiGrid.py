from mesa.space import MultiGrid
from mesa.agent import Agent
import CustomAgents
from typing import Tuple, Iterable
from Utils import PlantStage

Coordinate = Tuple[int, int]

class CustomMultiGrid(MultiGrid):
    def __init__(self, width: int, height: int, torus: bool) -> None:
        super().__init__(width, height, torus)

    def is_cell_suitable_for_seed(self, pos: Coordinate) -> bool:
        """Returns a bool of the contents of a cell."""
        x, y = pos
        plants = list(filter(lambda a: (isinstance(a, CustomAgents.PlantAgent) and a.plant_stage != PlantStage.DEATH), self.grid[x][y]))
        if len(plants) > 0:
            return False
            
        return True


    def get_custom_neighbors(
        self,
        agent_type,
        pos: Coordinate,
        moore: bool,
        include_center: bool = False,
        radius: int = 1
    ):
        neighbors = self.get_neighbors(pos, moore, include_center, radius)
        return list(filter(lambda n: isinstance(n, agent_type), neighbors))

    def get_plant_neighbors(
        self,
        pos: Coordinate,
        moore: bool,
        include_center: bool = False,
        radius: int = 1
    ) -> list[CustomAgents.PlantAgent]:
        return self.get_custom_neighbors(CustomAgents.PlantAgent, pos, moore, include_center, radius)

    def get_bumblebee_neighbors(
        self,
        pos: Coordinate,
        moore: bool,
        include_center: bool = False,
        radius: int = 1
    ) -> list[CustomAgents.BeeAgent]:
        return self.get_custom_neighbors(CustomAgents.BeeAgent, pos, moore, include_center, radius)

    def get_cell_custom_list_contents(
        self, 
        agent_type, 
        cell_list: Iterable[Coordinate]
    ) -> list[Agent]:
        return list(filter(lambda a: isinstance(a, agent_type), self.get_cell_list_contents(cell_list)))

    
    def get_cell_plant_list_contents(
        self, 
        cell_list: Iterable[Coordinate]
    ) -> list[CustomAgents.PlantAgent]:
        return self.get_cell_custom_list_contents(CustomAgents.PlantAgent, cell_list)

    def get_cell_bumblebee_list_contents(
        self, 
        cell_list: Iterable[Coordinate]
    ) -> list[CustomAgents.BeeAgent]:
        return self.get_cell_custom_list_contents(CustomAgents.BeeAgent, cell_list)