$(document).ready(function() {
	module("Read It Object Tests");
	test("Can be constructed with actions", function() {
		var r = readit({"actions": {
			an_action: {method: "GET", url: "http://some/url"}
		}});
		equal(r.actions.an_action.method, "GET", "method is preserved");
		equal(r.actions.an_action.url, "http://some/url", "URL is preserved");
	});

	test("createReading can build a Reading object from title+link", function() {
		var r = readit(),
		    aReading = r.createReading({
		    	title: "reading title",
		    	link: "http://link.to.title"
		    });
		equal(aReading.title, "reading title", "title property is recognized");
		equal(aReading.link, "http://link.to.title", "link property is recognized");
		notEqual(aReading.when, undefined, "when property is created");
		equal(aReading.id, undefined, "id property is not created");
	});

	test("createReading accepts an ISO 8601 date string", function() {
		var r = readit(),
		    now = new Date(),
		    aReading = r.createReading({
		    	title: "different title",
		    	link: "http://other.link",
		    	when: now.toISOString()
		    });
		equal(aReading.title, "different title", "title property is recognized");
		equal(aReading.link, "http://other.link", "link property is recognized");
		deepEqual(aReading.when, now, "when property is recognized");
		equal(aReading.id, undefined, "id property is not created");
	});

	test("createReading uses id attribute", function() {
		var r = readit(),
		    aReading = r.createReading({
		    	title: "different title",
		    	link: "http://other.link",
		    	id: 42
		    });
		equal(aReading.title, "different title", "title property is recognized");
		equal(aReading.link, "http://other.link", "link property is recognized");
		notEqual(aReading.when, undefined, "when property is created");
		equal(aReading.id, "42", "reading id property is derived from JSON id");
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
