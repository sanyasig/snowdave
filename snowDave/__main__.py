import sys
from os import path

from hotWordDetection.snowDave import SnowDave

sys.path.insert(0, path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

snow = SnowDave()
snow.startSnowDave()
