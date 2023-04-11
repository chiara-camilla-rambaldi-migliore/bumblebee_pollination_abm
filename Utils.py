from enum import Enum
from math import floor, sqrt, pi
from typing import Tuple

class ColonySize(Enum):
    SMALL = 1
    MEDIUM = 2
    BIG = 3

class PlantStage(Enum):
    SEED = 1
    FLOWER = 2
    DEATH =  3

class BeeType(Enum):
    MALE = 1
    WORKER = 2
    QUEEN = 3
    NEST_BEE = 4

# class syntax
class BeeStage(Enum):
    EGG = 1
    LARVAE = 2
    PUPA = 3
    BEE = 4
    DEATH = 5
    HIBERNATION = 6
    QUEEN = 7
    
class PlantType(Enum):
    SPRING_TYPE1 = 1
    SPRING_TYPE2 = 2
    SPRING_TYPE3 = 3
    SUMMER_TYPE1 = 4
    SUMMER_TYPE2 = 5
    SUMMER_TYPE3 = 6
    AUTUMN_TYPE1 = 7
    AUTUMN_TYPE2 = 8
    AUTUMN_TYPE3 = 9

class FlowerAreaType(Enum):
    CENTER_SQUARE = 1
    CENTER_CIRCLE = 2
    PERIMETRAL = 3
    NORTH_SECTION = 4
    SOUTH_SECTION = 5
    WEST_SECTION = 6
    EAST_SECTION = 7

class AreaConstructor():
    def __init__(self, area_type: FlowerAreaType, height, width, no_mow_pc) -> None:
        self.no_mow_pc = no_mow_pc
        self.height = height
        self.width = width
        self.area_type = area_type
        self.getCoordinateFunction = getattr(self, f"getCoordForPlants{self.area_type.value}")
        self.coords = self.getCoordinateFunction()
        self.isPointInFlowerArea = getattr(self, f"isPointInFlowerArea{self.area_type.value}")
        self.parkBoundaries = self.getParkBoundaries()

    def getWoodBoundsAndSurface(self):
        r_max = 5
        t_max = 5
        l_max = 5
        d_max = 5

        wood_surface = ((r_max+l_max)*self.height)+((t_max+d_max)*(self.width-l_max-r_max))

        return (r_max, t_max, l_max, d_max), wood_surface

    def getCoordForPlants1(self):
        (r_max, t_max, l_max, d_max), wood_surface = self.getWoodBoundsAndSurface()
        total_area = (self.width*self.height)-wood_surface
        no_mow_area = self.no_mow_pc*total_area
        no_mow_area_height = floor((self.height*sqrt(no_mow_area)*2)/(self.width+self.height))
        no_mow_area_width = floor(no_mow_area/no_mow_area_height)
        center = (floor(self.width/2), floor(self.height/2))
        return (
            (center[0]-floor(no_mow_area_width/2), center[1]-floor(no_mow_area_height/2)), 
            (center[0]-1+floor(no_mow_area_width/2), center[1]-1+floor(no_mow_area_height/2))
        )
    
    def getCoordForPlants2(self):
        _, wood_surface = self.getWoodBoundsAndSurface()
        total_area = (self.width*self.height)-wood_surface
        no_mow_area = self.no_mow_pc*total_area
        no_mow_area_radius = sqrt(no_mow_area/pi)
        center = (floor(self.width/2), floor(self.height/2))
        return (center, no_mow_area_radius)
    
    def getCoordForPlants3(self):
        (r_max, t_max, l_max, d_max), wood_surface = self.getWoodBoundsAndSurface()
        total_area = (self.width*self.height)-wood_surface
        no_mow_area = self.no_mow_pc*total_area
        no_mow_area_height = floor(no_mow_area/(2*(self.width-r_max-l_max)))
        start_of_no_mow_area = self.height-no_mow_area_height-t_max-1
        return ((l_max,start_of_no_mow_area), (self.width-1-r_max, self.height-1-t_max),
                (l_max,d_max), (self.width-1-r_max, no_mow_area_height-1+d_max))

    def getCoordForPlants4(self):
        (r_max, t_max, l_max, d_max), wood_surface = self.getWoodBoundsAndSurface()
        total_area = (self.width*self.height)-wood_surface
        no_mow_area = self.no_mow_pc*total_area
        no_mow_area_height = floor(no_mow_area/(self.width-r_max-l_max))
        start_of_no_mow_area = self.height-no_mow_area_height-t_max-1
        return ((l_max,start_of_no_mow_area), (self.width-1-r_max, self.height-1-t_max))
    
    def getCoordForPlants5(self):
        (r_max, t_max, l_max, d_max), wood_surface = self.getWoodBoundsAndSurface()
        total_area = (self.width*self.height)-wood_surface
        no_mow_area = self.no_mow_pc*total_area
        no_mow_area_height = floor(no_mow_area/(self.width-r_max-l_max))
        return ((l_max,d_max), (self.width-1-r_max, no_mow_area_height-1+d_max))

    def getCoordForPlants6(self):
        (r_max, t_max, l_max, d_max), wood_surface = self.getWoodBoundsAndSurface()
        total_area = (self.width*self.height)-wood_surface
        no_mow_area = self.no_mow_pc*total_area
        no_mow_area_width = floor(no_mow_area/(self.width-t_max-d_max))
        return ((l_max,d_max), (no_mow_area_width+l_max, self.height-1-t_max))
    
    def getCoordForPlants7(self):
        (r_max, t_max, l_max, d_max), wood_surface = self.getWoodBoundsAndSurface()
        total_area = (self.width*self.height)-wood_surface
        no_mow_area = self.no_mow_pc*total_area
        no_mow_area_width = floor(no_mow_area/(self.width-t_max-d_max))
        start_of_no_mow_area = self.width-no_mow_area_width-r_max-1
        return ((start_of_no_mow_area, d_max), (self.width-1-r_max, self.height-1-t_max))
    
    def inside_circle(self, point, center, radius) :
        dx = center[0] - point[0]
        dy = center[1] - point[1]
        distance = sqrt(dx*dx + dy*dy)
        return distance <= radius
    
    def inside_square(self, point: Tuple[int, int], left_down: Tuple[int, int], right_up: Tuple[int, int]):
        if ((point[0] >= left_down[0] and point[0] <= right_up[0]) and
            (point[1] >= left_down[1] and point[1] <= right_up[1])):
            return True
        else:
            return False
    
    def isPointInFlowerArea1(self, point):
        return self.inside_square(point, self.coords[0], self.coords[1])
    
    def isPointInFlowerArea2(self, point):
        return self.inside_circle(point, self.coords[0], self.coords[1])
    
    def isPointInFlowerArea3(self, point):
        if (self.inside_square(point, self.coords[0], self.coords[1]) or
            self.inside_square(point, self.coords[2], self.coords[3])):
            return True
        else:
            return False
        
    def isPointInFlowerArea4(self, point):
        return self.inside_square(point, self.coords[0], self.coords[1])
    
    def isPointInFlowerArea5(self, point):
        return self.inside_square(point, self.coords[0], self.coords[1])
    
    def isPointInFlowerArea6(self, point):
        return self.inside_square(point, self.coords[0], self.coords[1])
    
    def isPointInFlowerArea7(self, point):
        return self.inside_square(point, self.coords[0], self.coords[1])
    
    def getParkBoundaries(self) -> Tuple[Tuple[int,int], Tuple[int,int]]:
        (r_max, t_max, l_max, d_max), _ = self.getWoodBoundsAndSurface()
        return ((l_max,d_max), (self.width-1-r_max, self.height-1-t_max))


    def isPointInParkBoundaries(self, point):
        return self.inside_square(point, self.parkBoundaries[0], self.parkBoundaries[1])
    
    def isPointInWoodsArea(self, point: Tuple[int, int]):
        (r_max, t_max, l_max, d_max), wood_surface = self.getWoodBoundsAndSurface()
        x, y = point
        return (x <= l_max-1 or x >= self.width-r_max or y <= d_max-1 or y >= self.height-t_max)

    def getRandomPositionInWoods(self, random):
        (r_max, t_max, l_max, d_max), wood_surface = self.getWoodBoundsAndSurface()
        rand = random.random()
        if rand < 0.25:
            x = random.randint(self.width-r_max, self.width-1)
            y = random.randint(0, self.height-1)
        elif rand < 0.5: 
            x = random.randint(0, l_max-1)
            y = random.randint(0, self.height-1)
        elif rand < 0.75:
            x = random.randint(0, self.width-1)
            y = random.randint(self.height-t_max, self.height-1)
        else: 
            x = random.randint(0, self.width-1)
            y = random.randint(0, d_max-1)
        
        return (x,y)