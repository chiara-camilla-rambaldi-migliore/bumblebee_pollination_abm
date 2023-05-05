from mesa.space import MultiGrid
from mesa.agent import Agent
from typing import Tuple, Iterable, List
from bumblebee_pollination_abm.Utils import PlantStage
import bumblebee_pollination_abm.CustomAgents as CustomAgents

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
    
    def get_neighbor_cells_suitable_for_seeds(
        self,
        areaConstructor,
        plantSeason,
        pos: Coordinate,
        moore: bool,
        include_center: bool = False,
        radius: int = 1
    ) -> List[Coordinate]:
        neighborhood = self.get_neighborhood(pos, moore, include_center, radius)
        new_neighborhood = []
        for cell in neighborhood:
            x, y = cell
            plants = list(filter(
                lambda a: (
                    isinstance(a, CustomAgents.PlantAgent) and 
                    a.plant_stage == PlantStage.SEED and
                    a.plant_season == plantSeason
                ), 
                self.grid[x][y]
            ))
            if len(plants) == 0 and areaConstructor.isPointInParkBoundaries((x,y)):
                new_neighborhood.append(cell)
        return new_neighborhood

    def get_custom_neighbors(
        self,
        lambda_func,
        pos: Coordinate,
        moore: bool,
        include_center: bool = False,
        radius: int = 1
    ):
        neighbors = self.get_neighbors(pos, moore, include_center, radius)
        return list(filter(lambda_func, neighbors))

    def get_plant_neighbors(
        self,
        pos: Coordinate,
        moore: bool,
        include_center: bool = False,
        radius: int = 1
    ) -> List[CustomAgents.PlantAgent]:
        lambda_func = lambda n: isinstance(n, CustomAgents.PlantAgent) and n.plant_stage == PlantStage.FLOWER
        return self.get_custom_neighbors(lambda_func, pos, moore, include_center, radius)

    def get_bumblebee_neighbors(
        self,
        pos: Coordinate,
        moore: bool,
        include_center: bool = False,
        radius: int = 1
    ) -> List[CustomAgents.BeeAgent]:
        lambda_func = lambda n: isinstance(n, CustomAgents.BeeAgent)
        return self.get_custom_neighbors(lambda_func, pos, moore, include_center, radius)

    def get_cell_custom_list_contents(
        self, 
        lambda_func, 
        cell_list: Iterable[Coordinate]
    ) -> List[Agent]:
        return list(filter(lambda_func, self.get_cell_list_contents(cell_list)))

    
    def get_cell_plant_list_contents(
        self, 
        cell_list: Iterable[Coordinate]
    ) -> List[CustomAgents.PlantAgent]:
        lambda_func = lambda a: isinstance(a, CustomAgents.PlantAgent) and a.plant_stage == PlantStage.FLOWER
        return self.get_cell_custom_list_contents(lambda_func, cell_list)

    def get_cell_bumblebee_list_contents(
        self, 
        cell_list: Iterable[Coordinate]
    ) -> List[CustomAgents.BeeAgent]:
        lambda_func = lambda a: isinstance(a, CustomAgents.BeeAgent)
        return self.get_cell_custom_list_contents(lambda_func, cell_list)