# convert the raw captured data to a simplified format, merging all experiments and demographic data into a single file


import json
import os
from os import path
from Levenshtein import distance
from lib.throughput.Throughput import throughput

dataDir = os.getcwd() + f"\\data"

def showSuggestions(transcription, phrase):
    requiredLetters = int(phrase.threshold * len(phrase.target))
    requiredPart = phrase.target[:requiredLetters]
    transcribedPart = transcription[:requiredLetters] 
    if phrase.threshold == 0: return True
    elif phrase.threshold == 1: return False
    else: return len(transcription) >= requiredLetters and distance(requiredPart, transcribedPart) <= len(phrase.target) * 0.4

class Phrase: 
    def __init__(self, events, phrase):
        self.target = phrase["target"]
        self.threshold = phrase["threshold"]
        self.suggestions = phrase["suggestions"]

        startEvent = events.pop(0)
        ownEvents = [ startEvent ]
        transcribed = ""
        deletions = 0
        typedText = None
        suggestion = None

        if showSuggestions(transcribed, self): firstSuggestionTime = startEvent["time"]
        else: firstSuggestionTime = None

        while True:
            event = events.pop(0)
            ownEvents.append(event)

            if "text" in event:
                newText = event["text"]
                previousText = transcribed

                if firstSuggestionTime is None and showSuggestions(newText, self):
                    firstSuggestionTime = event["time"]

                if len(newText) < len(previousText): 
                    deletions += 1

                typedText = newText
                transcribed = typedText


            if "suggestion" in event:
                suggestion = event["suggestion"]
                transcribed = suggestion

            if "next" in event or "suggestion" in event:
                break

        endEvent = ownEvents[-1]
        durationMillis = endEvent["time"] - startEvent["time"]
        

        self.suggestionDuration = 0
        if firstSuggestionTime is not None:
            self.suggestionDuration = (endEvent["time"] - firstSuggestionTime) * 0.001

        self.durationMillis = durationMillis
        self.transcribed = transcribed
        self.deletions = deletions
        self.typedText = typedText
        self.selectedSuggestion = suggestion

        self.targetWasSuggested = self.target in self.suggestions
        
        self.duration = durationMillis * 0.001
        self.keyPresses = len(ownEvents) - 2
        self.suggestedChars = int(len(self.target) * (1 - phrase["threshold"]))
        
        self.distance = distance(self.target, self.transcribed)
        self.keyStrokesPerChar = self.keyPresses / len(self.target)
        self.levenshteinError = self.distance / max(len(self.target), len(self.transcribed))

        self.wpm = (len(self.target) / 5) / (self.duration / 60)

        self.plausible = len(transcribed) > 0 and self.durationMillis > 300
        # TODO actual number of letters saved (compared to possible savings per threshold)
        # TODO per person, improvement with suggestions

        self.selfThroughput = throughput([self])


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