"""
A module for analysis of rain gage data. Particularly for event by event analysis
and calculation of storm ARIs
"""
import storms.precip.datasets as datasets
from storms.precip.network import Network
from storms.precip.raingage import Raingage, get_pfds
