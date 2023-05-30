from mesa.space import MultiGrid
from mesa.agent import Agent
from typing import Tuple, Iterable, List
from bumblebee_pollination_abm.Utils import PlantStage
import bumblebee_pollination_abm.CustomAgents as CustomAgents

Coordinate = Tuple[int, int]

class CustomMultiGrid(MultiGrid):
    def __init__(self, width: int, height: int, torus: bool) -> None:
        super().__init__(width, height, torus)
    
        
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
            len_plants = sum(
                1 for a in self.grid[x][y] 
                if a.agent_type == "plant" and 
                a.plant_stage in (PlantStage.SEED, PlantStage.FLOWER) and 
                a.plant_season == plantSeason and 
                a.age == 0
            )
            if len_plants == 0 and areaConstructor.isPointInParkBoundaries((x,y)):
                new_neighborhood.append(cell)
        return new_neighborhood


    
    def get_plant_neighbors(
        self,
        pos: Coordinate,
        moore: bool,
        include_center: bool = False,
        radius: int = 1
    ) -> List[CustomAgents.PlantAgent]:
        return [n for n in self.get_neighbors(pos, moore, include_center, radius) if n.agent_type == "plant" and n.plant_stage == PlantStage.FLOWER]

    
    def get_bumblebee_neighbors(
        self,
        pos: Coordinate,
        moore: bool,
        include_center: bool = False,
        radius: int = 1
    ) -> List[CustomAgents.BeeAgent]:
        return [n for n in self.get_neighbors(pos, moore, include_center, radius) if n.agent_type == "bee"]
    
    
    def get_cell_plant_list_contents(
        self, 
        cell_list: Iterable[Coordinate]
    ) -> List[CustomAgents.PlantAgent]:
        return [a for a in self.get_cell_list_contents(cell_list) if a.agent_type == "plant" and a.plant_stage == PlantStage.FLOWER]

    
    def get_cell_bumblebee_list_contents(
        self, 
        cell_list: Iterable[Coordinate]
    ) -> List[CustomAgents.BeeAgent]:
        return [a for a in self.get_cell_list_contents(cell_list) if a.agent_type == "bee"]