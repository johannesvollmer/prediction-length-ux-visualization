# convert the raw captured data to a simplified format, merging all experiments and demographic data into a single file


from lib.throughput.Throughput import Throughput
import json
import os
from os import path

dataDir = os.getcwd() + f"\\data"

class Phrase: 
    def __init__(self, events, phrase):
        startEvent = events.pop(0)
        ownEvents = [ startEvent ]
        transcribed = ""
        deletions = 0
        typedText = None
        suggestion = None

        while True:
            event = events.pop(0)
            ownEvents.append(event)

            if "text" in event:
                if len(event["text"]) < len(transcribed): 
                    deletions += 1

                typedText = event["text"]
                transcribed = typedText

            if "suggestion" in event:
                suggestion = event["suggestion"]
                transcribed = suggestion

            if "next" in event or "suggestion" in event:
                break

        endEvent = ownEvents[-1]
        target = phrase["target"]
        durationMillis = endEvent["time"] - startEvent["time"]
        throughput = Throughput(target = target, transcribed = transcribed, time = durationMillis)

        self.target = target
        self.durationMillis = durationMillis
        self.transcribed = transcribed
        self.deletions = deletions
        self.typedText = typedText
        self.selectedSuggestion = suggestion

        self.threshold = phrase["threshold"]
        self.suggestions = phrase["suggestions"]
        self.targetWasSuggested = target in self.suggestions
        
        self.duration = durationMillis * 0.001
        self.keyPresses = len(ownEvents) - 2
        self.suggestedChars = int(len(target) * (1 - phrase["threshold"]))
        self.throughput = throughput.throughput
        self.charsPerSecond = throughput.cps
        self.wordsPerMinute = 12 * throughput.cps
        self.uncorrectedErrorRate = throughput.totalINF / (throughput.totalINF + throughput.totalC)
        
        self.plausible = len(transcribed) > 0
        # TODO actual number of letters saved (compared to possible savings per threshold)
        # TODO per person, improvement with suggestions

class Participant:
    def __init__(self, participant):
        self.age = participant["age"]
        self.experience = participant["experience"]
        self.left = participant["hand"] == "left"
        self.female = participant["gender"] == "female"

class Experiment: 
    def __init__(self, events, participant):
        firstEvent = events.pop(0)
        phrases = firstEvent["phrases"]
        blocks = []

        for _ in range(4):
            _next_button = events.pop(0)
            block = []
            
            for _ in range(6):
                phrase = Phrase(events, phrases.pop(0))
                if phrase.plausible: block.append(phrase)

            blocks.append(block)
        _warmup = blocks.pop(0)
        
        self.participant = Participant(participant)
        self.blocks = blocks
        self.phrases = [phrase for block in blocks for phrase in block]

        # additionally, sort all phrases by their threshold
        self.byThreshold = [ [], [], [], [], [], [] ]
        for phrase in self.phrases: 
            self.byThreshold[int((phrase.threshold + 0.001) * 5)].append(phrase)



def load():
    participants = json.load(open(dataDir + "\\demographic.json"))
    experiments = []

    for index in range(len(participants)):
        events = json.load(open(dataDir + f"\\experiment\\{index}.json"))
        experiments.append(Experiment(events, participants.pop(0)))

    return experiments