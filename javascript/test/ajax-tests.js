$(document).ready(function() {
	module("AJAX Test Cases");

	test("addReading() follows hypermedia action", function() {
		var r = readit(),
		    aReading = createReading('1');
		addAction(r, "add-reading", "POST", "http://add/reading");
		
		r.addReading(aReading);
		
		ok(mockedAjax.wasCalled(), "$.ajax was called");
		equal(mockedAjax.getUrl(), r.actions["add-reading"].url,
			"URL matches hypermedia action");
		equal(mockedAjax.getMethod(), r.actions["add-reading"].method,
			"HTTP method matches hypermedia action");
		equal(mockedAjax.getData(), JSON.stringify(aReading),
			"JSONified Reading was sent");
		equal(mockedAjax.getHeader("Content-Type").split(";")[0],
			"application/json", "Content-Type header is set");
		ok($.inArray("application/json", mockedAjax.getHeader("Accept").split(",")) > -1,
			"Accept header is set");
	});

	test("JSON-encoded redirect is followed", function() {
		mockedAjax.addResponse(200, "Redirect", [], {
			json: {redirect_to: "http://go/to/here"}
		});
		
		var saved, r = readit({
			setLocation: function(url) {
				saved = url;
			}
		});
		addAction(r, "add-reading", "POST", "http://add/reading");
		
		r.addReading(createReading("1"));
		
		ok(mockedAjax.wasCalled(), "$.ajax was called");
		ok(saved !== undefined, "new location was set");
		equal(saved, "http://go/to/here", "redirect was followed");
	});

	test("addReading() is a no-op without actions", function() {
		var r = readit(), aReading = createReading('1');
		r.addReading(aReading);
		ok(!mockedAjax.wasCalled(), "$.ajax was not called");
	});

	test("fetchReadings() populates readings array", function() {
		var r = readit(),
		    expected = [
		        createJsonRpcReading("1"),
		        createJsonRpcReading("2"),
		        createJsonRpcReading("3")
		    ];
		mockedAjax.addResponse(200, "OK", [], { json: {readings: expected} });
		addAction(r, "get-readings", "GET", "http://fetch/readings");
		
		r.fetchReadings();
		equal(r.readings.length, expected.length, "readings were retrieved");
		equal(r.readings[0].when.toISOString(), expected[0].when);
	});

	test("fetchReadings() follows hypermedia action", function() {
		var r = readit();
		addAction(r, "get-readings", "GET", "http://readings");
		mockedAjax.addResponse(200, "OK", [], {json: {readings: []}});
		
		r.fetchReadings();
		
		ok(mockedAjax.wasCalled(), "$.ajax was called");
		equal(mockedAjax.getUrl(), r.actions["get-readings"].url,
			"URL matches hypermedia action");
		equal(mockedAjax.getMethod(), r.actions["get-readings"].method,
			"HTTP method matches hypermedia action");
	});

	test("fetchReadings() is a no-op without actions", function() {
		var r = readit();
		r.fetchReadings();
		ok(!mockedAjax.wasCalled(), "$.ajax was not called");
	});

});
