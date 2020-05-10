const secondsPerMilli = 0.001
const sum = array => array.reduce((a, b) => a + b)
const average = array => sum(array) / array.length

const median = array => {
	const sorted = [...array].sort()
	const left = sorted[Math.floor(array.length / 2)]
	const right = sorted[Math.ceil(array.length / 2)]
	return (left + right) / 2
}


const html = document.querySelector('#contents')
const namespace = "http://www.w3.org/2000/svg"

const output = element => html.appendChild(element)
const text = (tag, text, attributes) => create(tag, attributes, [document.createTextNode(text)])

const path = (xy, attributes = {}) => {
	const path = `M ${xy[0].x},${xy[0].y} L ` +  xy.slice(1).map(({ x, y }) => `${x},${y}`).join(" ")
	return create("path", { ...attributes, namespace, d: path })
}

const create = (tag, attributes = {}, children = []) => {
	const element = attributes.namespace? document.createElementNS(attributes.namespace, tag) : document.createElement(tag)
	if (attributes.style) attributes.style = Object.entries(attributes.style).map(pair => pair.join(": ")).join("; ")
	delete attributes.namespace

	for (const attribute in attributes) element.setAttribute(attribute, attributes[attribute]) // element[attribute] = attributes[attribute]
	for (const child of children) element.appendChild(child)
	return element
}

const blobRaw = window.URL.createObjectURL(new Blob([JSON.stringify(window.data)], { type: 'text/json' }))
output(create("a", { href: blobRaw, download: "merged-augmented.json" }, [ text("p", "Download") ]))


const data = cleanPhrases()
const phraseData = data.flatMap(person => person.experiment)
const dataNoSuggestions = phraseData.filter(experiment => experiment.threshold == 1)
const dataFullSuggestions = phraseData.filter(experiment => experiment.threshold == 0)
console.log(data)

const blob = window.URL.createObjectURL(new Blob([JSON.stringify(data)], { type: 'text/json' }))
output(create("a", { href: blob, download: "experiment-aufzeichnung.json" }, [ text("p", "Download") ]))

const asThroughput = (phrase, index) => ({
	"Transcribe": phrase.transcribed,
	"Time": phrase.milliDuration,
	"Trial": index,
	"Present": phrase.target
})

const blobThroughputNone = window.URL.createObjectURL(new Blob([JSON.stringify(dataNoSuggestions.map(asThroughput))], { type: 'text/json' }))
output(create("a", { href: blobThroughputNone, download: "throughput-data-none.json" }, [ text("p", "Download Throughput None") ]))

const blobThroughputAll = window.URL.createObjectURL(new Blob([JSON.stringify(dataFullSuggestions.map(asThroughput))], { type: 'text/json' }))
output(create("a", { href: blobThroughputAll, download: "throughput-data-all.json" }, [ text("p", "Download Throughput All") ]))


const medianAge = median(data.map(data => +data.participant.age))
const females = data.filter(data => data.participant.gender === "female").length / data.length
const leftHanded = data.filter(data => data.participant.hand === "left").length / data.length

output(text("p", "number of participants: " + data.length))
output(text("p", "median age: " + medianAge))
output(text("p", "females: " + females * 100 + "%"))
output(text("p", "left handed: " + leftHanded * 100 + "%"))


const medianS = median(data.flatMap(point => point.experiment.map(experiment => experiment.duration)))
const medianCPS = median(data.flatMap(point => point.experiment.filter(ex => ex.target == ex.transcribed).map(experiment => experiment.charsPerSecond)))

const medianNoneCPS = median(dataNoSuggestions.map(experiment => experiment.charsPerSecond))
const medianFullCPS = median(dataFullSuggestions.map(experiment => experiment.charsPerSecond))

const averageNoneCPS = average(dataNoSuggestions.map(experiment => experiment.charsPerSecond))
const averageFullCPS = average(dataFullSuggestions.map(experiment => experiment.charsPerSecond))

const medianGPC = median(data.flatMap(point => point.experiment.filter(ex => ex.target == ex.transcribed).map(experiment => 
	(experiment.keyPressCount + 1) / experiment.target.length
)))

output(text("p", "median phrase seconds: " + medianS))
output(text("p", "median characters per second: " + medianCPS))
output(text("p", "median gestures per character: " + medianGPC))
output(text("p", `full suggestions: average = ${averageFullCPS} median = ${medianFullCPS}`))
output(text("p", `no suggestions: average = ${averageNoneCPS} median = ${medianNoneCPS}`))

const sortedPhrases = data.flatMap(data => data.experiment).filter(phrase => phrase.targetWasSuggested).sort((a, b) => a.charsPerSecond - b.charsPerSecond)
const phrasesQuantile = sortedPhrases // .slice(sortedPhrases.length * 0.1, sortedPhrases.length * 0.8)

output(create("svg", { namespace, viewBox: "0 0 1000 1000", xmlns: namespace }, [
	... (phrasesQuantile.map(point => 
		create("circle", { namespace, cx: 1000*(1 - point.threshold), cy: 1000-1000*point.charsPerSecond/20, r: "20", style: { fill: "#0001" } })
	)),

	path([ {x:0, y:1000}, {x:1000, y:1000} ], { style: { stroke: "red", "stroke-width": "1", fill: "none" } }),
	path([ {x:0, y:0}, {x:0, y:1000} ], { style: { stroke: "blue", "stroke-width": "1", fill: "none" } }),
]))



// const medianThresholds = data.map(person => [0, 0.2, 0.4, 0.6, 0.8, 1.0].map(x => {
// 	const points = person.experiment.slice(12).filter(phrase => phrase.threshold == x)

// 	return ({ 
// 		threshold: x, 
// 		medianCPS: median(points.map(point => point.charsPerSecond)),
// 		averageCPS: average(points.map(point => point.charsPerSecond)),
// 		averageLevenshtein: average(points.map(point => levenshtein(point.target, point.transcribed))) 
// 	})
// }))

const all01Runs = data
	.flatMap(person => {
		const segmented = [ person.experiment.slice(0,6), person.experiment.slice(6,12), person.experiment.slice(12,18) ]
		for (array of segmented) array.sort((a,b) => a.threshold - b.threshold)
		return segmented
	})
	.map(phrases => phrases.filter(phrase => phrase.targetWasSuggested)) // filter out phrases that did not suggest the target phrase

// const all01RunsAverage = all01Runs.map(person => )

output(create("svg", { namespace, viewBox: "0 0 1000 1000", xmlns: namespace }, [
	... (all01Runs.map(run => 
		path(run.map(phrase => ({ x: 1000*(1 - phrase.threshold), y: 1000-1000*phrase.charsPerSecond/20})), { namespace, style: {
			stroke: "#0001", strokeWidth: "5", fill: "none" }
		})
	)),

	path([ {x:0, y:1000}, {x:1000, y:1000} ], { style: { stroke: "red", "stroke-width": "1", fill: "none" } }),
	path([ {x:0, y:0}, {x:0, y:1000} ], { style: { stroke: "blue", "stroke-width": "1", fill: "none" } }),
]))

// console.log(medianThresholds)

// output(text("p", "correlation of suggested chars and duration: " + spearman.calc(phraseData.map(x => x.charThreshold), phraseData.map(x => x.duration))))

// output(text("p", "correlation of suggested chars and median duration: " + spearman.calc(medianThresholds.map(x => x.charThreshold), medianThresholds.map(x => x.medianDuration))))
// output(text("p", "correlation of suggested chars and average levenshtein: " + spearman.calc(medianThresholds.map(x => x.charThreshold), medianThresholds.map(x => x.averageLevenshtein))))



// parse events into a data structure that is easier to handle
function cleanPhrases () { return window.data.map(experiment => {
	let remainingEvents = experiment.events

	const phrases = experiment.events[0].phrases
	remainingEvents = experiment.events.slice(1)

	const cleanPhrases = []

	// parse events for all blocks
	for (let block = 0; block < 4; block++){
		remainingEvents = remainingEvents.slice(1) // skip block start event

		// parse events for all phrases in this block
		for (let phrase = 0; phrase < 6; phrase++){
			const startEvent = remainingEvents.shift()
			let events = [ startEvent ]
			let currentText = ""
			let deletions = 0
			let typedText = null

			// drain all events until the phrase is finished
			while (true) {
				const event = remainingEvents.shift()
				events.push(event)

				if (event.text !== undefined) {
					if (event.text.length < currentText.length) 
						deletions++
					
					typedText = currentText
					currentText = event.text

					// const showSuggestions = currentText.length >= Math.floor(target) && levenshtein(currentText, target) < target.length * 0.4
				}

				if (event.suggestion !== undefined) {
					currentText = event.suggestion
				}

				if (event.suggestion !== undefined || event.next !== undefined) 
					break
			}

			const endEvent = events[events.length - 1]
			const phrase = phrases.shift()
			const milliDuration = endEvent.time - startEvent.time 
			const duration = milliDuration * secondsPerMilli 
			const charThreshold = phrase.target.length * (1 - phrase.threshold)
			const keyPressCount = events.length - 2
			const charsPerSecond = currentText.length / duration 

			// collect the phrase
			cleanPhrases.push({
				... phrase,
				selectedSuggestion: endEvent.suggestion,
				keyPressCount,
				transcribed: currentText,
				duration, deletions, 
				charThreshold, typedText,
				charsPerSecond,
				milliDuration,
				targetWasSuggested: phrase.suggestions.includes(phrase.target),
				rawEvents: events
			})
		}
	}

	return {
		participant: {
			age: experiment.age,
			gender: experiment.gender,
			hand: experiment.hand,
		},

		warmup: cleanPhrases.slice(0, 6),
		experiment: cleanPhrases.slice(6)
	}
}) }
