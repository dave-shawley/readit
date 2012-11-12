$(document).ready(function() {
	module("ReadIt UI Tests");
	test("Create Read It instance", function() {
		var r = readit();
		ok(r !== undefined, "creation function returns an object");
	});

	test("Update uses readings array", function() {
		var r = readit();
		r.update();
		equal($("#readinglist ul li").length, r.readings.length + 1,
			"reading instances are not required");
		r.readings = [ createReading("1"), createReading("2") ];
		r.update();
		equal($("#readinglist ul li").length, r.readings.length + 1,
			"every reading creates a new entry");
	});

	test("Cloned reading is cleaned", function() {
		var r = readit();
		r.readings = [ createReading("1") ];
		r.update();
		var $clonedItem = $("#" + r.readings[0].id);
		equal($clonedItem.length, 1, "item was cloned with reading id");
		ok(!$clonedItem.hasClass("template"), "template class should be removed");
	});

	test("Reading populates all fields", function() {
		var r = readit(), aReading = createReading('1');
		r.readings.push(aReading);
		r.update();
		
		expect(4); // each of the following should fire once
		var $readingItem = $("#" + r.readings[0].id);
		$readingItem.find(".title").each(function (index, element) {
			equal($(element).text(), aReading.title, "title element");
		});
		$readingItem.find(".when").each(function (index, element) {
			equal($(element).text(), aReading.when.toDateString(), "when element");
		});
		$readingItem.find(".link").each(function (index, element) {
			equal($(element).prop("href"), aReading.link, "link href");
		});
		$readingItem.find(".url").each(function (index, element) {
			equal($(element).text(), aReading.link, "link text");
		});
	});

	test("addReading() modifies readings property", function() {
		var r = readit(),
				aReading = {
					title: 'reading title',
					link: 'http://link.to.reading',
					when: new Date()
				};
		mockedAjax.addResponse(200, "OK", [], {
			json: {
				new_reading: {
					title: aReading.title,
					id: 'readingid',
					link: aReading.link,
					when: aReading.when.toISOString()
				}
			}
		});
		addReaditActions(r);
		r.addReading(aReading);
		equal(r.readings.length, 1, "readings list length changed");
		equal(r.readings[0].id, "readingid", "reading IDs match");
		equal(r.readings[0].title, aReading.title, "reading titles match");
		equal(r.readings[0].link, aReading.link, "reading links match");
		deepEqual(r.readings[0].when, aReading.when, "reading timestamps match");
	});

	test("update() updates existing elements", function() {
		var r = readit(), aReading = createReading('1');
		r.readings.push(aReading);
		r.update();
		var expectedLen = $("#readinglist .reading").length;
		aReading.title = 'title 2';
		r.update();
		equal($("#readinglist .reading").length, expectedLen,
				"no element was added");
	});

	test("update() identifies elements by id", function() {
		var r = readit(),
		    aReading = createReading('1'),
		    anotherReading = createReading('2');
		r.readings.push(aReading);
		r.update();
		var expectedLen = $("#readinglist .reading").length;
		
		aReading.title = anotherReading.title;
		r.update();
		equal($("#" + aReading.id + " .title").text(), aReading.title,
				"title was changed");
		equal($("#readinglist .reading").length, expectedLen,
				"no element was added");
		
		aReading.link = anotherReading.link;
		r.update();
		equal($("#" + aReading.id + " .link").prop("href"), aReading.link,
				"link href was changed");
		equal($("#readinglist .reading").length, expectedLen,
				"no element was added");
		
		aReading.when = new Date(aReading.when.getTime() + (24 * 60 * 60 * 1000));
		r.update();
		equal($("#" + aReading.id + " .when").text(),
			aReading.when.toDateString(), "when was changed");
		equal($("#readinglist .reading").length, expectedLen,
				"no element was added");
		
		r.readings.push(anotherReading);
		r.update();
		
		equal(r.readings.length, 2, "readings array grew");
		equal($("#readinglist .reading").length, expectedLen + 1,
				"an element was added");
	});

	test("AJAX error from addReading displays a message", function() {
		var r = readit(), aReading = createReading('1');
		mockedAjax.addResponse(403, "Forbidden");
		addReaditActions(r);
		$("#message").hide();
		
		r.addReading(aReading);
		ok($("#message").css("display") != "none", "message was shown");
	});

	test("AJAX error from fetchReadings displays a message", function() {
		var r = readit(), $message = $("#message");
		mockedAjax.addResponse(403, "Forbidden");
		addReaditActions(r);
		$message.hide();
		
		r.fetchReadings();
		ok($message.css("display") != "none", "message was shown");
		equal($message.find(".status").text(), "403");
		equal($message.find(".phrase").text(), "Forbidden");
		equal($message.find(".error").text(), "Forbidden");
	});

	// helper used in the following two tests
	var verifyItem = function($item, aReading, sel, test_descr) {
		equal($item.find(sel.title_selector).text(), aReading.title,
				test_descr + " title was changed");
		equal($item.find(sel.link_selector).prop("href"), aReading.link,
				test_descr + " link href was changed");
		equal($item.find(sel.url_selector).text(), aReading.link,
				test_descr + " url was changed");
		equal($item.find(sel.when_selector).text(),
				aReading.when.toDateString(), test_descr + " when was changed");
	};

	test("CSS selectors are parameters", function() {
		var selectors = {
					template_class: "p-template",
					reading_li_selector: "#p-reading",
					title_selector: ".p-title",
					when_selector: ".p-when",
					link_selector: ".p-link",
					url_selector: "#p-url",
					reading_info_selector: "#p-reading-info"
				},
				r = readit(selectors),
				aReading = createReading("readingid");
		
		r.readings.push(aReading);
		r.update();
		
		var $item = $("#parameterized-list li:first");
		equal($item.prop("id"), aReading.id, "list item id was changed");
		verifyItem($item, aReading, selectors, "list item");
	});

	test("CSS selectors are honored by showReading", function() {
		var selectors = {
					template_class: "p-template",
					reading_li_selector: "#p-reading",
					title_selector: ".p-title",
					when_selector: ".p-when",
					link_selector: ".p-link",
					url_selector: "#p-url",
					reading_info_selector: "#p-reading-info"
				},
				r = readit(selectors),
				aReading = createReading("readingid");
		r.showReading(aReading);
		verifyItem($("#p-reading-info"), aReading, selectors, "reading info");
	});

	test("AJAX error uses CSS selectors", function() {
		var selectors = {
				selector: "#parameterized-message",
				status: "#p-status",
				phrase: "p:eq(1)",
				error: ".p-error"
			},
			r = readit({message_selectors: selectors}),
			$message = $(selectors.selector);

			$message.hide();
			mockedAjax.addResponse(599, "Induced Error");
			addReaditActions(r);
			r.fetchReadings();

			ok($message.css("display") != "none", "message was shown");
			equal($message.find(selectors.status).text(), "599");
			equal($message.find(selectors.phrase).text(), "Induced Error");
			equal($message.find(selectors.error).text(), "Induced Error");
	});

	test("showReading updates all fields", function() {
		var r = readit(), aReading = createReading('1');
		r.showReading(aReading);
		verifyElementMatchesReading($("#readinginfo"), aReading);
	});

	test("clicking on a reading updates reading info", function() {
		var r = readit(), aReading = createReading('1');
		r.readings.push(aReading);
		r.update(); // <-- this updates the list
		var $readingItem = $("#" + r.readings[0].id),
		    $readingLink = $readingItem.find("a");
		$readingLink.click();
		verifyElementMatchesReading($("#readinginfo"), aReading);
	});

	test("addReading() updates the UI on success", function() {
		var r = readit(),
				aReading = {
					title: 'reading title',
					link: 'http://link.to.reading/',
					when: new Date()
				};
		mockedAjax.addResponse(200, "OK", [], {
			json: {
				new_reading: {
					title: aReading.title,
					id: 'id12345',
					link: aReading.link,
					when: aReading.when.toISOString()
				}
			}
		});
		addReaditActions(r);
		r.addReading(aReading);
		verifyElementMatchesReading($("#" + r.readings[0].id), r.readings[0]);
	});

	test("addReading() marks outside links with rel='external'", function() {
		var r = readit({debug: true}),
				aReading = {
					title: 'reading title',
					link: 'http://link.to.reading/',
					when: new Date(),
					id: 'id12345'
				};
		mockedAjax.addResponse(200, "OK", [], {
			json: {
				new_reading: {
					title: aReading.title,
					id: aReading.id,
					link: aReading.link,
					when: aReading.when.toISOString()
				}
			}
		});
		addReaditActions(r);
		r.addReading(aReading);
		equal($("#" + aReading.id + " .link").prop("rel"), "external");
	});

});

