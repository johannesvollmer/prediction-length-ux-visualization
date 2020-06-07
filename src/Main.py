from Import import load
from lib.throughput.Throughput import throughput

import numpy as num
import scipy.stats as nums
from functools import reduce
import matplotlib.pyplot as plot
percentage = lambda elements, filterLambda: round(100 * len(list(filter(filterLambda, elements))) / len(elements), 2)

print("loading...")
experiments = load()
print("finished.\n")

phrases = [phrase for experiment in experiments for phrase in experiment.phrases]

maxPhraseSelfThroughput = num.max([phrase.selfThroughput for phrase in phrases])
for phrase in phrases: phrase.normalizedSelfThroughput = phrase.selfThroughput / maxPhraseSelfThroughput

phrasesWithTargetSuggestion = list(filter(lambda phrase: phrase.targetWasSuggested, phrases))
phrasesWithSelectableTargetSuggestion = list(filter(lambda phrase: phrase.suggestionDuration != 0, phrasesWithTargetSuggestion))
phrasesWithFullTargetSuggestion = list(filter(lambda phrase: phrase.threshold == 0, phrasesWithTargetSuggestion))
phrasesByThreshold = [[phrase for experiment in experiments for phrase in experiment.byThreshold[index]] for index in range(6)]

throughputByThreshold = [throughput(threshold) for threshold in phrasesByThreshold]
throughputsByThreshold = [[phrase.selfThroughput for phrase in threshold] for threshold in phrasesByThreshold]
# wpmByThreshold = [[phrase.wordsPerMinute for phrase in threshold] for threshold in phrasesByThreshold]
strokesPerCharByThreshold = [[phrase.keyStrokesPerChar for phrase in threshold] for threshold in phrasesByThreshold]

# selectableByThreshold = [list(filter(lambda phrase: phrase.targetWasSuggested, threshold)) for threshold in phrasesByThreshold]
totalTimeByThreshold = [num.median([phrase.duration for phrase in threshold]) for threshold in phrasesByThreshold]
hiddenTimeByThreshold = [num.median([phrase.duration - phrase.suggestionDuration for phrase in threshold]) for threshold in phrasesByThreshold]

lengthByThreshold = [[len(phrase.target) for phrase in threshold] for threshold in phrasesByThreshold]
timeByThreshold = [[phrase.duration for phrase in threshold] for threshold in phrasesByThreshold]

print(f"participants: {len(experiments)}")

print(f"females: {percentage(experiments, lambda experiment: experiment.participant.female)}%")
print(f"left handed: {percentage(experiments, lambda experiment: experiment.participant.left)}%")
print(f"median age: {round(num.median([experiment.participant.age for experiment in experiments]), 4)}")

print(f"percentage of picked suggestions where possible: {percentage(phrasesWithSelectableTargetSuggestion, lambda phrase: phrase.selectedSuggestion is not None)}%")
print(f"percentage of ignored full suggestions: {percentage(phrasesWithFullTargetSuggestion, lambda phrase: phrase.selectedSuggestion is None)}%")
print(f"median levenshtein error rate: {round(num.median([phrase.levenshteinError for phrase in phrases]), 4)}")
print(f"average levenshtein error rate: {round(num.average([phrase.levenshteinError for phrase in phrases]), 4)}")

phrasesWithCorrectlySelectedSuggestions = list(filter(lambda phrase: phrase.selectedSuggestion == phrase.target, phrasesWithSelectableTargetSuggestion))
print(f"redundant suggestions: {percentage(phrasesWithCorrectlySelectedSuggestions, lambda phrase: phrase.typedText == phrase.target)}%")
print(f"median time from first suggestion to finishing: {round(num.median([phrase.suggestionDuration for phrase in phrasesWithSelectableTargetSuggestion]), 2)}s")
print(f"incorrect suggestions: {percentage(phrases, lambda phrase: phrase.selectedSuggestion is not None and phrase.selectedSuggestion != phrase.target)}%")

throughputByPhrase = [phrase.normalizedSelfThroughput for phrase in phrases]
percentagesByPhrase = [(1-phrase.threshold) for phrase in phrases]
correlationThresholdThroughput = num.corrcoef(percentagesByPhrase, throughputByPhrase)[1,0]
t2, p2 = nums.ttest_ind(percentagesByPhrase, throughputByPhrase, equal_var = False)
print(f"total pearson correlation of suggestion percentage and throughput: {round(correlationThresholdThroughput, 4)}")
print(f"   with t: {round(t2, 8)}, p: {p2}") 

phraseWords = [phrase.target.replace('.',' ').replace('!',' ').replace(',',' ').replace('?',' ').split() for phrase in phrases]
print(f"median phrase words: {round(num.median([len(words) for words in phraseWords]), 2)}")
print(f"median word length: {round(num.median([len(word) for words in phraseWords for word in words]), 2)}")
print(f"median word length variance: {round(num.var([len(word) for words in phraseWords for word in words]), 2)}")
print(f"median char quintets: {round(num.median([len(phrase.target) / 5.0 for phrase in phrases]), 2)}")

print(f"average backspace percentage: {round(num.average([phrase.deletions/phrase.keyPresses for phrase in phrases if phrase.keyPresses != 0])*100, 2)}")

# print(f"max wpm for no suggestions: {round(num.max([phrase.wpm for phrase in phrasesByThreshold[5]]), 2)}")
# print(f"max wpm for full suggestions: {round(num.max([phrase.wpm for phrase in phrasesByThreshold[0]]), 2)}")

def personImprovement(experiment):
    # averageByThreshold = [num.average([phrase.throughput for phrase in phrases]) for phrases in experiment.byThreshold]
    # improvement = averageByThreshold[0] - averageByThreshold[5]

    thres = [1 - phrase.threshold for phrase in experiment.phrases]
    through = [phrase.normalizedSelfThroughput for phrase in experiment.phrases]
    correlation = num.corrcoef(thres, through)[1,0]
    # print(f"correlation: {correlation}")
    return correlation

thresholds = [0, 20, 40, 60, 80, 100]
x = thresholds[::-1]
thresholdQuantiles = [[num.quantile(throughputs, quantile) for throughputs in throughputsByThreshold] for quantile in [0, 0.25, 0.5, 0.75, 1.0]]

figure, ((area, bars, lengthtime), (wpm, errors, errrors2)) = plot.subplots(2, 3)
area.fill_between(x, thresholdQuantiles[0], thresholdQuantiles[4], color="#ddd")
area.fill_between(x, thresholdQuantiles[1], thresholdQuantiles[3], color="#aaa")
area.plot(x, thresholdQuantiles[2], '-', color="#777")
# area.plot(x, throughputByThreshold, '-', color="#000")
area.set_ylabel('throughput per phrase quantiles')
area.set_xlabel('percentage of letters suggested')


lengthtime.scatter(lengthByThreshold[0], timeByThreshold[0], color="blue", alpha=0.2)
lengthtime.scatter(lengthByThreshold[5], timeByThreshold[5], color="orange", alpha=0.2)
b1, m1 = num.polyfit(lengthByThreshold[0], timeByThreshold[0], 1) # fit line through scatter with polyfit
b2, m2 = num.polyfit(lengthByThreshold[5], timeByThreshold[5], 1) # fit line through scatter with polyfit
y1 = [m1 * x + b1 for x in lengthByThreshold[0]]
y2 = [m2 * x + b2 for x in lengthByThreshold[5]]

lengthtime.plot(lengthByThreshold[0], y1, '-', color="blue")
lengthtime.plot(lengthByThreshold[5], y2, '-', color="orange")

lengthtime.set_xlabel('phrase length')
lengthtime.set_ylabel('input duration')


improvementPerPerson = [personImprovement(experiment) for experiment in experiments]
# improvementPerPerson.sort()

print(f"median correlation (per person) of suggested percentage to throughput: {num.median(improvementPerPerson)}")

# bars.bar(range(len(experiments)), improvementPerPerson, color="#444")
bars.hist(improvementPerPerson, bins = 6)
bars.set_ylabel('number of persons')
bars.set_xlabel('correlation of letter percentage to throughput')


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
wpm.set_ylabel('median seconds')
wpm.set_xlabel('percentage of letters suggested')

gpcQuantiles = [[num.quantile(throughputs, quantile) for throughputs in strokesPerCharByThreshold] for quantile in [0, 0.25, 0.5, 0.75, 1.0]]
errors.fill_between(x, gpcQuantiles[0], gpcQuantiles[4], color="#ddd")
errors.fill_between(x, gpcQuantiles[1], gpcQuantiles[3], color="#aaa")
errors.plot(x, gpcQuantiles[2], '-', color="#777")
errors.set_ylabel('key strokes per character quantiles')
errors.set_xlabel('percentage of letters suggested')


errrors2.hist([phrase.levenshteinError for phrase in phrases], bins = 100)
errrors2.set_ylabel('number of phrases')
errrors2.set_xlabel('levenshtein error rate')



plot.show()