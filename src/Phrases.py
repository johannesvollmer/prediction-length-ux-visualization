# analyze some phrases
import os
from os import path
import matplotlib.pyplot as plot

dataDir = os.getcwd() + f"\\data"

with open(dataDir + f"\\phrases.txt", 'r') as file:
    contents = file.read()

cleaned = contents.replace(',', ' ').replace('.', ' ').replace('!', ' ').replace('?', ' ')

words = dict()

for word in cleaned.split():
    if word not in words: words[word] = 0
    words[word] += 1

wordTuples = [(key, words[key]) for key in words]
wordTuples.sort(key = lambda tuple: tuple[1], reverse=True)
wordTuples = wordTuples[:(int(len(wordTuples) * 0.02))]

print(f"words: {wordTuples}")

figure, graph = plot.subplots(1,1)
ticks = range(len(wordTuples))
graph.bar(ticks, [tpl[1] for tpl in wordTuples])
graph.set_ylabel('count')
plot.xticks(ticks, [tpl[0] for tpl in wordTuples])
plot.show()