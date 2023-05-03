import datetime
from . import CustomAgents
from .CustomDataCollector import CustomDataCollector
from .Model import GreenArea
from .CustomModularServer import CustomModularServer
from .CustomMultiGrid import CustomMultiGrid
from .CustomTime import RandomActivationByTypeOrdered
from .Server import server
from .Utils import ColonySize, PlantStage, BeeType, BeeStage, PlantType, FlowerAreaType, Season, AreaConstructor

__all__ = [
    "CustomAgents",
    "CustomDataCollector",
    "GreenArea",
    "CustomModularServer",
    "CustomMultiGrid",
    "RandomActivationByTypeOrdered",
    "server",
    "ColonySize",
    "PlantStage",
    "BeeType",
    "BeeStage",
    "PlantType",
    "FlowerAreaType",
    "Season",
    "AreaConstructor",
]

__title__ = "bumblebee-pollination-abm"
__version__ = "0.1"
__license__ = "Apache 2.0"
_this_year = datetime.datetime.now(tz=datetime.timezone.utc).date().year
__copyright__ = f"Copyright {_this_year} bumblebee_pollination_abm Thesis"