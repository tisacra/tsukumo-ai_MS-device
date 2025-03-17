from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from datetime import datetime

# Load and initialize the BirdNET-Analyzer models.
analyzer = Analyzer()

recording = Recording(
    analyzer,
    "sample.wav",
    #lat=-1,
    #lon=-1,
    #date=datetime(year=2024, month=5, day=10), # use date or week_48
    min_conf=0.01,
)
recording.analyze()
print(recording.detections)