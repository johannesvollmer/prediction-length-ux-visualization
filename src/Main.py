from Import import load
import numpy as num
from functools import reduce
import matplotlib.pyplot as plot
flatten = lambda listoflists: [element for alist in listoflists for element in alist]

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


phrasesByThreshold = [[phrase for experiment in experiments for phrase in experiment.byThreshold[index]] for index in range(6)]
throughputByThreshold = [[phrase.throughput for phrase in threshold] for threshold in phrasesByThreshold]
def personImprovement(experiment):
    # averageByThreshold = [num.average([phrase.throughput for phrase in phrases]) for phrases in experiment.byThreshold]
    # improvement = averageByThreshold[0] - averageByThreshold[5]

    thres = [1 - phrase.threshold for phrase in experiment.phrases]
    through = [phrase.throughput for phrase in experiment.phrases]
    correlation = num.corrcoef(thres, through)[1,0]
    # print(f"correlation: {correlation}")
    return correlation


thres = [1 - phrase.threshold for experiment in experiments for phrase in experiment.phrases]
through = [phrase.throughput for experiment in experiments for phrase in experiment.phrases]
print(f"correlation of suggested percentage to throughput: {num.corrcoef(thres, through)[1,0]})")

thresholds = [0, 20, 40, 60, 80, 100]
x = thresholds[::-1]
quantiles = [[num.quantile(threshold, quantile) for threshold in throughputByThreshold] for quantile in [0, 0.25, 0.5, 0.75, 1.0]]

figure, (area, scatter) = plot.subplots(2, 1)
area.fill_between(x, quantiles[0], quantiles[4], color="#ddd")
area.fill_between(x, quantiles[1], quantiles[3], color="#aaa")
area.plot(x, quantiles[2], '-', color="#222")
area.set_ylabel('throughput')
area.set_xlabel('percentage of letters suggested')


improvementPerPerson = [personImprovement(experiment) for experiment in experiments]
improvementPerPerson.sort()

print(f"median correlation (per person) of suggested percentage to throughput: {num.median(improvementPerPerson)}")

scatter.bar(range(len(experiments)), improvementPerPerson, color="#444")
scatter.set_ylabel('correlation of letter percentage to throughput')
scatter.set_xlabel('person')


plot.show()