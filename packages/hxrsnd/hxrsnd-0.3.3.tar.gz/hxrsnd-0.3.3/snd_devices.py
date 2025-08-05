# from bluesky import RunEngine

from pcdsdevices.areadetector.detectors import PCDSAreaDetector

from hxrsnd.sequencer import SeqBase
from hxrsnd.sndmotor import SamMotor
from hxrsnd.sndsystem import SplitAndDelay

# Base PV
pv_base = "XCS:SND"

# Instantiate the whole system
snd = SplitAndDelay(pv_base, name="snd")
daq = snd.daq

# Additional Devices
seq = SeqBase("ECS:SYS0:4", desc="Sequencer Channel 4")
sam_x = SamMotor("XCS:USR:MMN:01", name="sam_x")
sam_y = SamMotor("XCS:USR:MMN:02", name="sam_y")
opal_1 = PCDSAreaDetector("XCS:USR:O1000:01", name="Opal 1")
