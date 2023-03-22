from enum import Enum

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
    TYPE1 = 1
    TYPE2 = 2