import os

from storms.precip.datasets._asos import ASOS
from storms.precip.datasets._globalhourly import GlobalHourly
from storms.precip.datasets._nexrad import NEXRAD

# from storms.precip.datasets._asos_http import ASOS_http

_dataDir = os.path.dirname(os.path.realpath(__file__))
LoganFreeForm = os.path.join(_dataDir, "Logan.1h")
