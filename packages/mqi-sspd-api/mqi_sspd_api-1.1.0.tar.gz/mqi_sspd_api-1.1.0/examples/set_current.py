import sys
import time
import json
import time
import json
sys.path.append("../mqi-api")
from mqi.v1.api import MQI

m = MQI("ws://localhost", "8080", "username", "password")


# Will set current of channel 5 to 1.1
m.set_current(1,[5],0.00003)
print(m.get_current(1, []))
