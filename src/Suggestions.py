# analyze some phrases
import os
from os import path
import numpy as num

dataDir = os.getcwd() + f"\\data"

with open(dataDir + f"\\suggestions.txt", 'r') as file:
    contents = file.read()

lines = contents.splitlines()
wordLines = [line.replace(',', ' ').replace('.', ' ').replace('!', ' ').replace('?', ' ').split() for line in lines]

print(f"median word count: {num.median([len(line) for line in wordLines])}")
print(f"median word len: {num.median([len(word) for line in wordLines for word in line])}")
