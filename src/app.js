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
const output = element => html.appendChild(element)
const text = (tag, text, attributes) => create(tag, attributes, [document.createTextNode(text)])

const path = (xy, attributes = {}) => {
	const path = `M ${xy[0].x},${xy[0].y} L ` +  xy.slice(1).map(({ x, y }) => `${x},${y}`).join(" ")
	return create("path", { ...attributes, d: path })
}

const create = (tag, attributes = {}, children = []) => {
	const element = document.createElement(tag)
	for (const attribute in attributes) element.setAttribute(attribute, attributes[attribute]) // element[attribute] = attributes[attribute]
	for (const child of children) element.appendChild(child)
	return element
}

const data = cleanPhrases()
const phraseData = data.flatMap(person => person.experiment)
console.log(data)

const blob = window.URL.createObjectURL(new Blob([JSON.stringify(data)], { type: 'text/json' }))
output(create("a", { href: blob, download: "experiment-aufzeichnung.json" }, [ text("p", "Download") ]))


const medianAge = median(data.map(data => +data.participant.age))
const females = data.filter(data => data.participant.gender === "female").length / data.length
const leftHanded = data.filter(data => data.participant.hand === "left").length / data.length

output(text("p", "number of participants: " + data.length))
output(text("p", "median age: " + medianAge))
output(text("p", "females: " + females * 100 + "%"))
output(text("p", "left handed: " + leftHanded * 100 + "%"))


const medianS = median(data.flatMap(point => point.experiment.map(experiment => experiment.duration)))

const medianCPS = median(data.flatMap(point => point.experiment.filter(ex => ex.target == ex.transcribed).map(experiment => 
	experiment.target.length / experiment.duration
)))

const medianGPC = median(data.flatMap(point => point.experiment.filter(ex => ex.target == ex.transcribed).map(experiment => 
	(experiment.keyPressCount + 1) / experiment.target.length
)))

output(text("p", "median phrase seconds: " + medianS))
output(text("p", "median characters per second: " + medianCPS))
output(text("p", "median gestures per character: " + medianGPC))


output(create("svg", { viewBox: "0 0 50 2", width: "50px", height: "50px", style: "width: 100px; height: 100px;", xmlns: "http://www.w3.org/2000/svg" }, [
	... (data.flatMap(data => data.experiment).map(point => {
		
		return create("circle", { cx: point.charThreshold, cy: point.duration, r: 0.2, opacity: 0.01, fill: "black" })
		// return path(
		// 	data.experiment.map(point => ({ x: point.charThreshold, y: point.duration })),
		// 	{ fill: "none", stroke: "red" }
		// )
	}))
]))



// const medianThresholds = [0, 0.2, 0.4, 0.6, 0.8, 1.0].map(x => {
// 	const points = data.flatMap(person => person.experiment)
// 		.filter(point => point.threshold == x)

// 	return ({ 
// 		threshold: x, 
// 		medianDuration: median(points.map(point => point.duration)),
// 		medianDuration: median(points.map(point => point.duration)),
// 		averageLevenshtein: average(points.map(point => levenshtein(point.target, point.transcribed))) 
// 	})
// })

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
					
					currentText = event.text

					// const showSuggestions = currentText.length >= Math.floor(target) && levenshtein(currentText, target) < target.length * 0.4
				}

				if (event.suggestion !== undefined) {
					typedText = currentText
					currentText = event.suggestion
				}

				if (event.suggestion !== undefined || event.next !== undefined) 
					break
			}

			const endEvent = events[events.length - 1]
			const phrase = phrases.shift()

			// collect the phrase
			cleanPhrases.push({
				... phrase,
				selectedSuggestion: endEvent.suggestion,
				keyPressCount: events.length - 2,
				transcribed: currentText,
				duration: (endEvent.time - startEvent.time) * secondsPerMilli,
				deletions, 
				charThreshold: phrase.target.length * (1 - phrase.threshold),
				typedText
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
