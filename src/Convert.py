# convert the raw captured data to a simplified format, merging all experiments and demographic data into a single file


from lib.throughput.Throughput import Throughput
import json
import os
from os import path

dataDir = os.getcwd() + f"\\data"

class Phrase:
    def __init__(self, events, phrases):
        startEvent = events.pop(0)
        self.ownEvents = [ startEvent ]
        self.transcribed = ""
        self.deletions = 0
        self.typedText = ""

        while True:
            event = events.pop(0)
            self.ownEvents.append(event)

            if "text" in event:
                if len(event["text"]) < len(self.transcribed): 
                    self.deletions += 1

                self.typedText = event["text"]
                self.transcribed = event["text"]

            if "suggestion" in event:
                self.transcribed = event["suggestion"]

            if "next" in event or "suggestion" in event:
                break

        endEvent = self.ownEvents[-1]
        phrase = phrases.pop(0)
        self.target = phrase["target"]
        self.suggestions = phrase["suggestions"]
        self.threshold = phrase["threshold"]
        self.durationMillis = endEvent["time"] - startEvent["time"]
        self.duration = self.durationMillis * 0.001
        self.keyPresses = len(self.ownEvents) - 2
        self.charsThreshold = len(self.target) * (1 - self.threshold)

        throughput = Throughput(target = self.target, transcribed = self.transcribed, time = self.durationMillis)
        self.throughput = throughput.throughput
        self.charsPerSecond = throughput.cps
        self.wordsPerMinute = 12 * self.charsPerSecond


class Experiment:
    def __init__(self, events, participant):
        firstEvent = events.pop(0)
        phrases = firstEvent["phrases"]
        self.blocks = []

        for _ in range(4):
            block = []
            
            for _ in range(6):
                block.append(Phrase(events, phrases))

            self.blocks.append(block)

        self.warmup = self.blocks.pop(0)
        self.participant = participant



participants = json.load(open(dataDir + "\\demographic.json"))
experiments = []

while True:
    file = dataDir + f"\\experiment\\{len(experiments)}.json"
    if not path.exists(file): break # no more files in directory

    print (f"analyzing file #{len(experiments)}")

    events = json.load(open(file))
    experiments.append(Experiment(events, participants.pop(0)))

with open(dataDir + '\\merged.json', 'w', encoding='utf-8') as file:
    json.dump(experiments, file, ensure_ascii=False, indent=4)

print("finished conversion")