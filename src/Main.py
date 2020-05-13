from Import import load
import numpy as num
from functools import reduce
import matplotlib.pyplot as plot
percentage = lambda elements, filterLambda: round(100 * len(list(filter(filterLambda, elements))) / len(elements), 2)

print("loading...")
experiments = load()
phrases = [phrase for experiment in experiments for phrase in experiment.phrases]
print("finished.\n")

print(f"participants: {len(experiments)}")

print(f"females: {percentage(experiments, lambda experiment: experiment.participant.female)}%")
print(f"left handed: {percentage(experiments, lambda experiment: experiment.participant.left)}%")

print(f"median age: {round(num.median([experiment.participant.age for experiment in experiments]), 4)}")
print(f"median error rate: {round(num.median([phrase.uncorrectedErrorRate for phrase in phrases]), 4)}")
print(f"average error rate: {round(num.average([phrase.uncorrectedErrorRate for phrase in phrases]), 4)}")
print(f"median wpm: {round(num.median([phrase.wordsPerMinute for phrase in phrases]), 4)}")
print(f"average wpm: {round(num.average([phrase.wordsPerMinute for phrase in phrases]), 4)}")

print(f"incorrect suggestions: {percentage(phrases, lambda phrase: phrase.selectedSuggestion is not None and phrase.selectedSuggestion != phrase.target)}%")
print(f"redundant suggestions: {percentage(phrases, lambda phrase: phrase.selectedSuggestion == phrase.target and phrase.typedText == phrase.target)}%")

phrasesByThreshold = [[phrase for experiment in experiments for phrase in experiment.byThreshold[index]] for index in range(6)]
throughputByThreshold = [[phrase.throughput for phrase in threshold] for threshold in phrasesByThreshold]
wpmByThreshold = [[phrase.wordsPerMinute for phrase in threshold] for threshold in phrasesByThreshold]
errorsByThreshold = [[phrase.uncorrectedErrorRate for phrase in threshold] for threshold in phrasesByThreshold]

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
thresholdQuantiles = [[num.quantile(throughputs, quantile) for throughputs in throughputByThreshold] for quantile in [0, 0.25, 0.5, 0.75, 1.0]]

figure, ((area, bars), (wpm, errors)) = plot.subplots(2, 2)
area.fill_between(x, thresholdQuantiles[0], thresholdQuantiles[4], color="#ddd")
area.fill_between(x, thresholdQuantiles[1], thresholdQuantiles[3], color="#aaa")
area.plot(x, thresholdQuantiles[2], '-', color="#222")
area.set_ylabel('throughput')
area.set_xlabel('percentage of letters suggested')


improvementPerPerson = [personImprovement(experiment) for experiment in experiments]
improvementPerPerson.sort()

print(f"median correlation (per person) of suggested percentage to throughput: {num.median(improvementPerPerson)}")

bars.bar(range(len(experiments)), improvementPerPerson, color="#444")
bars.set_ylabel('correlation of letter percentage to throughput')
bars.set_xlabel('person')

wpmQuantiles = [[num.quantile(throughputs, quantile) for throughputs in wpmByThreshold] for quantile in [0, 0.25, 0.5, 0.75, 1.0]]
wpm.fill_between(x, wpmQuantiles[0], wpmQuantiles[4], color="#ddd")
wpm.fill_between(x, wpmQuantiles[1], wpmQuantiles[3], color="#aaa")
wpm.plot(x, wpmQuantiles[2], '-', color="#222")
wpm.set_ylabel('words per minute')
wpm.set_xlabel('percentage of letters suggested')

errorQuantiles = [[num.quantile(throughputs, quantile) for throughputs in errorsByThreshold] for quantile in [0, 0.25, 0.5, 0.75, 1.0]]
errors.fill_between(x, errorQuantiles[0], errorQuantiles[4], color="#ddd")
errors.fill_between(x, errorQuantiles[1], errorQuantiles[3], color="#aaa")
errors.plot(x, errorQuantiles[2], '-', color="#222")
errors.set_ylabel('uncorrected error rate')
errors.set_xlabel('percentage of letters suggested')


plot.show()