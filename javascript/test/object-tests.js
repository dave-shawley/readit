$(document).ready(function() {
	module("Read It Object Tests");
	test("Can be constructed with actions", function() {
		var r = readit({"actions": {
			an_action: {method: "GET", url: "http://some/url"}
		}});
		equal(r.actions.an_action.method, "GET", "method is preserved");
		equal(r.actions.an_action.url, "http://some/url", "URL is preserved");
	});

	test("Reading objects are constructed using createReading", function() {
		var r = readit(),
		    aReading = r.createReading({
		    	title: "reading title",
		    	link: "http://link.to.title"
				});
		equal(aReading.title, "reading title", "title property is recognized");
		equal(aReading.link, "http://link.to.title", "link property is recognized");
		notEqual(aReading.when, undefined, "when property is created");
		equal(aReading.id, undefined, "id property is not created");

		var now = new Date();
		var spec = {
			title: "different title",
			link: "http://other.link",
			when: now.toISOString()
		};
		aReading = r.createReading(spec)
		equal(aReading.title, "different title", "title property is recognized");
		equal(aReading.link, "http://other.link", "link property is recognized");
		deepEqual(aReading.when, now, "when property is recognized");
		equal(aReading.id, undefined, "id property is not created");

	});

	test("Reading objects know how to transform to JSON", function() {
		var r = readit(),
				aReading = r.createReading({
		    	title: "reading title",
		    	link: "http://link.to.title",
				}),
				result = JSON.parse(aReading.jsonify());
		equal(aReading.title, result.title, "title transferred");
		equal(aReading.link, result.link, "link transferred");
		equal(aReading.when.toISOString(), result.when, "when transferred");
	});

});
