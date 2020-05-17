from Import import load
from lib.throughput.Throughput import throughput

import numpy as num
from functools import reduce
import matplotlib.pyplot as plot
percentage = lambda elements, filterLambda: round(100 * len(list(filter(filterLambda, elements))) / len(elements), 2)

print("loading...")
experiments = load()
print("finished.\n")

phrases = [phrase for experiment in experiments for phrase in experiment.phrases]
phrasesWithSuggestion = list(filter(lambda phrase: phrase.targetWasSuggested, phrases))
phrasesWithSelectableSuggestion = list(filter(lambda phrase: phrase.suggestionDuration != 0, phrasesWithSuggestion))
phrasesByThreshold = [[phrase for experiment in experiments for phrase in experiment.byThreshold[index]] for index in range(6)]

throughputByThreshold = [throughput(threshold) for threshold in phrasesByThreshold]
throughputsByThreshold = [[throughput([phrase]) for phrase in threshold] for threshold in phrasesByThreshold]
# wpmByThreshold = [[phrase.wordsPerMinute for phrase in threshold] for threshold in phrasesByThreshold]
strokesPerCharByThreshold = [[phrase.keyStrokesPerChar for phrase in threshold] for threshold in phrasesByThreshold]

# selectableByThreshold = [list(filter(lambda phrase: phrase.targetWasSuggested, threshold)) for threshold in phrasesByThreshold]
totalTimeByThreshold = [num.average([phrase.duration for phrase in threshold]) for threshold in phrasesByThreshold]
hiddenTimeByThreshold = [num.average([phrase.duration - phrase.suggestionDuration for phrase in threshold]) for threshold in phrasesByThreshold]


print(f"participants: {len(experiments)}")

print(f"females: {percentage(experiments, lambda experiment: experiment.participant.female)}%")
print(f"left handed: {percentage(experiments, lambda experiment: experiment.participant.left)}%")
print(f"median age: {round(num.median([experiment.participant.age for experiment in experiments]), 4)}")

print(f"percentage of picked suggestions where possible: {percentage(phrasesWithSelectableSuggestion, lambda phrase: phrase.selectedSuggestion is not None)}%")
print(f"median levenshtein error rate: {round(num.median([phrase.distance for phrase in phrases]), 4)}")
print(f"average levenshtein error rate: {round(num.average([phrase.distance for phrase in phrases]), 4)}")


print(f"median time from first suggestion to finishing: {round(num.median([phrase.suggestionDuration for phrase in phrasesWithSelectableSuggestion]), 2)}s")

print(f"incorrect suggestions: {percentage(phrases, lambda phrase: phrase.selectedSuggestion is not None and phrase.selectedSuggestion != phrase.target)}%")
print(f"redundant suggestions: {percentage(phrases, lambda phrase: phrase.selectedSuggestion == phrase.target and phrase.typedText == phrase.target)}%")
print(f"unused full suggestions: {percentage(phrases, lambda phrase: phrase.threshold == 0 and phrase.selectedSuggestion is None)}%")
print(f"total correlation of suggestion percentage and throughput: {round(num.corrcoef([(1-phrase.threshold) for phrase in phrases], [throughput([phrase]) for phrase in phrases])[1,0], 4)}%")

def personImprovement(experiment):
    # averageByThreshold = [num.average([phrase.throughput for phrase in phrases]) for phrases in experiment.byThreshold]
    # improvement = averageByThreshold[0] - averageByThreshold[5]

    thres = [1 - phrase.threshold for phrase in experiment.phrases]
    through = [throughput([phrase]) for phrase in experiment.phrases]
    correlation = num.corrcoef(thres, through)[1,0]
    # print(f"correlation: {correlation}")
    return correlation

thresholds = [0, 20, 40, 60, 80, 100]
x = thresholds[::-1]
thresholdQuantiles = [[num.quantile(throughputs, quantile) for throughputs in throughputsByThreshold] for quantile in [0, 0.25, 0.5, 0.75, 1.0]]

figure, ((area, bars), (wpm, errors)) = plot.subplots(2, 2)
area.fill_between(x, thresholdQuantiles[0], thresholdQuantiles[4], color="#ddd")
area.fill_between(x, thresholdQuantiles[1], thresholdQuantiles[3], color="#aaa")
area.plot(x, thresholdQuantiles[2], '-', color="#777")
# area.plot(x, throughputByThreshold, '-', color="#000")
area.set_ylabel('throughput')
area.set_xlabel('percentage of letters suggested')


improvementPerPerson = [personImprovement(experiment) for experiment in experiments]
improvementPerPerson.sort()

print(f"median correlation (per person) of suggested percentage to throughput: {num.median(improvementPerPerson)}")

bars.bar(range(len(experiments)), improvementPerPerson, color="#444")
bars.set_ylabel('correlation of letter percentage to throughput')
bars.set_xlabel('person')


# bar = [percentage(experiment.phrases, lambda phrase: phrase.selectedSuggestion is not None and phrase.targetWasSuggested) for experiment in experiments]
# bar.sort()

# bars.bar(range(len(experiments)), bar, color="#444")
# bars.set_ylabel('correlation of letter percentage to throughput')
# bars.set_xlabel('person')

# wpmQuantiles = [[num.quantile(throughputs, quantile) for throughputs in wpmByThreshold] for quantile in [0, 0.25, 0.5, 0.75, 1.0]]
# wpm.fill_between(x, wpmQuantiles[0], wpmQuantiles[4], color="#ddd")
# wpm.fill_between(x, wpmQuantiles[1], wpmQuantiles[3], color="#aaa")
# wpm.plot(x, wpmQuantiles[2], '-', color="#222")
# wpm.set_ylabel('words per minute')
# wpm.set_xlabel('percentage of letters suggested')


wpm.fill_between(x, totalTimeByThreshold, color="#333", label="total time")
wpm.fill_between(x, hiddenTimeByThreshold, color="#bbb", label="time spent before suggestions appeared")
wpm.set_ylabel('seconds')
wpm.set_xlabel('percentage of letters suggested')

gpcQuantiles = [[num.quantile(throughputs, quantile) for throughputs in strokesPerCharByThreshold] for quantile in [0, 0.25, 0.5, 0.75, 1.0]]
errors.fill_between(x, gpcQuantiles[0], gpcQuantiles[4], color="#ddd")
errors.fill_between(x, gpcQuantiles[1], gpcQuantiles[3], color="#aaa")
errors.plot(x, gpcQuantiles[2], '-', color="#777")
errors.set_ylabel('key strokes per character')
errors.set_xlabel('percentage of letters suggested')


plot.show()