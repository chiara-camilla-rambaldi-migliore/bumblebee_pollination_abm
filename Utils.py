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

    @staticmethod
    def newStage(stage, days):
        stage_days = {
                BeeStage.EGG: 4,
                BeeStage.LARVAE: 4,
                BeeStage.PUPA: 8,
                BeeStage.BEE: 20,
                BeeStage.HIBERNATION: 180
            }
        if stage == BeeStage.EGG:
            if days >= stage_days[BeeStage.EGG]:
                return BeeStage.LARVAE
            else:
                return BeeStage.EGG
        elif stage == BeeStage.LARVAE:
            if days >= stage_days[BeeStage.EGG]+stage_days[BeeStage.LARVAE]:
                return BeeStage.PUPA
            else:
                return BeeStage.LARVAE
        elif stage == BeeStage.PUPA:
            if days >= stage_days[BeeStage.EGG]+stage_days[BeeStage.LARVAE]+stage_days[BeeStage.PUPA]:
                return BeeStage.BEE
            else:
                return BeeStage.PUPA
        elif stage == BeeStage.BEE:
            if days >= stage_days[BeeStage.EGG]+stage_days[BeeStage.LARVAE]+stage_days[BeeStage.PUPA]+stage_days[BeeStage.BEE]:
                return BeeStage.DEATH
            else:
                return BeeStage.BEE
        elif stage == BeeStage.HIBERNATION:
            if days >= stage_days[BeeStage.HIBERNATION]:
                return BeeStage.BEE
            else:
                return BeeStage.HIBERNATION