from Import import load
import numpy as num
from functools import reduce
import matplotlib.pyplot as plot

print("loading...")
experiments = load()
print("finished.\n")

print(f"participants: {len(experiments)}")

females = list(filter(lambda experiment: experiment.participant["gender"] == "female", experiments))
print(f"females: {len(females)} ({100 * len(females) / len(experiments)}%)")

left = list(filter(lambda experiment: experiment.participant["hand"] == "left", experiments))
print(f"left handed: {len(left)} ({100 * len(left) / len(experiments)}%)")

medianAge = num.median(num.array(list(map(lambda exp: exp.participant["age"], experiments))))
print(f"median age: {medianAge}")

byThreshold = [ [], [], [], [], [], [] ]
for experiment in experiments:
    for block in experiment.blocks:
        for phrase in block:
            # if phrase.target in phrase.suggestions: # filter out phrases where the suggestions did not contain the target phrase
                byThreshold[int((phrase.threshold + 0.001) * 5)].append(phrase)
            
throughputByThreshold = [[phrase.throughput for phrase in phrases] for phrases in byThreshold]


thresholds = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
x = thresholds[::-1]

quantiles = [[num.quantile(threshold, quantile) for threshold in throughputByThreshold] for quantile in [0, 0.25, 0.5, 0.75, 1.0]]

figure, axes = plot.subplots()
axes.plot(x, quantiles[2], '-')
axes.fill_between(x, quantiles[0], quantiles[4], alpha=0.2)
axes.fill_between(x, quantiles[1], quantiles[3], alpha=0.2)

plot.show()