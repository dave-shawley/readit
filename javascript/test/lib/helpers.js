var createReading = function (id) {
		return {
			id: id,
			title: "title " + id,
			link: "http://link/" + id,
			when: new Date()
		};
	},

	createJsonRpcReading = function (id) {
		return {
			id: id,
			title: "title " + id,
			link: "http://link/" + id,
			when: "2012-02-29T23:59:59.999Z"
		};
	},

	addAction = function (obj, name, method, url) {
		var actions = {};
		actions[name] = { method: method, url: url };
		$.extend(true, obj, {"actions": actions});
	},

	addReaditActions = function (obj) {
		addAction(obj, "add-reading", "POST", "http://add/reading");
		addAction(obj, "get-readings", "GET", "http://readings");
	},

	verifyElementMatchesReading = function($displayItem, aReading) {
		expect(4);
		$displayItem.find(".title").each(function (index, element) {
			equal($(element).text(), aReading.title, "title element");
		});
		$displayItem.find(".when").each(function (index, element) {
			equal($(element).text(), aReading.when.toDateString(), "when element");
		});
		$displayItem.find(".link").each(function (index, element) {
			equal($(element).prop("href"), aReading.link, "link href");
		});
		$displayItem.find(".url").each(function (index, element) {
			equal($(element).text(), aReading.link, "link text");
		});
	}
;


