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


# averagePersonImprovement = 
throughputByLetterCount = dict()
byThreshold = [ [], [], [], [], [], [] ]
for experiment in experiments:
    for block in experiment.blocks:
        for phrase in block:
                byThreshold[int((phrase.threshold + 0.001) * 5)].append((phrase, experiment))

                if phrase.suggestedChars not in throughputByLetterCount: throughputByLetterCount[phrase.suggestedChars] = []
                throughputByLetterCount[phrase.suggestedChars].append(phrase.throughput)


throughputByThreshold = [[phrase.throughput for (phrase, _) in phrases] for phrases in byThreshold]
# experiencedByThreshold = [num.median([phrase.throughput for (phrase, _) in list(filter(lambda tuple: tuple[1].participant["experience"] == 3, phrases))]) for phrases in byThreshold]
# inexperiencedByThreshold = [num.median([phrase.throughput for (phrase, _) in list(filter(lambda tuple: tuple[1].participant["experience"] < 3, phrases))]) for phrases in byThreshold]

thresholds = [0, 20, 40, 60, 80, 100]
x = thresholds[::-1]

quantiles = [[num.quantile(threshold, quantile) for threshold in throughputByThreshold] for quantile in [0, 0.25, 0.5, 0.75, 1.0]]

figure, (area, scatter) = plot.subplots(2, 1)
area.fill_between(x, quantiles[0], quantiles[4], color="#ddd")
area.fill_between(x, quantiles[1], quantiles[3], color="#aaa")
area.plot(x, quantiles[2], '-', color="#222")
# area.plot(x, experiencedByThreshold, '-', color="#888")
# area.plot(x, inexperiencedByThreshold, '-', color="#444")
area.set_ylabel('throughput')
area.set_xlabel('percentage of letters suggested')


keys = list(throughputByLetterCount.keys())
keys.sort()

scatter.fill_between(
    keys,
    [num.min(throughputByLetterCount[key]) for key in keys], 
    [num.max(throughputByLetterCount[key]) for key in keys],
    color="#ddd"
)

scatter.plot(keys, [num.median(throughputByLetterCount[key]) for key in keys], '-', color="#ddd")


scatter.set_ylabel('throughput')
scatter.set_xlabel('letters suggested')


plot.show()