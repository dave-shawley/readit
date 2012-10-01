(function($) {
	$.ajaxMock = function (my) {
		var ajaxData = my || {},
			responses = [],
			lastAjaxOptions = {},
			lastRequestHeaders = {},
			wasCalled = false;

		//
		// Public methods that will be exported
		//
		var reset = function () {
			lastAjaxOptions = {};
			lastRequestHeaders = {};
			wasCalled = false;
			responses = [];
		};
		var getHeader = function (headerName) {
			var n, matches = [];
			for (n in lastRequestHeaders) {
				if (lastRequestHeaders.hasOwnProperty(n)) {
					if (n.toLowerCase() == headerName.toLowerCase()) {
						matches.push(lastRequestHeaders[n]);
					}
				}
			}
			if (matches.length > 1) {
				return matches.join(", ");
			}
			return matches[0];
		};
		var addResponse = function (code, phrase, headers, data) {
			responses.push({
				status: code, phrase: phrase,
				headers: headers || [],
				data: data || {}
			});
		};

		//
		// Private functions
		//
		var debug = function () {
			if (my && my.debug) {
				var args = [].splice.call(arguments, 0);
				args.unshift("-");
				args.unshift("DEBUG");
				console.log(args.join(" "));
			}
		};

		//
		// Export the public API
		//   Note that simple "getters" are added inline
		//
		ajaxData.reset = reset;
		ajaxData.getHeader = getHeader;
		ajaxData.addResponse = addResponse;
		ajaxData.wasCalled = function () { return wasCalled; };
		ajaxData.getUrl = function () { return lastAjaxOptions.url; };
		ajaxData.getMethod = function () { return lastAjaxOptions.type; };
		ajaxData.getData = function () { return lastAjaxOptions.data; };
		ajaxData.getLast = function () { return lastAjaxOptions; };
	
		//
		// Insert the new object into the AJAX and QUnit chains
		//
		$.ajaxTransport("+*", function (merged, original, jqXHR) {
			lastAjaxOptions = merged;
			return {
				send: function (headers, transportDone) { 
					lastRequestHeaders = headers;
					wasCalled = true;
					var response = responses.shift() || {
						status: 599,
						phrase: "No Response Set",
						data: {},
						headers: []
					};
					debug("firing transportDone:", response.status, response.phrase);
					transportDone(response.status, response.phrase,
							response.data, response.headers.join("\r\n"));
				},
				abort: function () {}
			};
		});

		if (QUnit) {
			var otherStart = QUnit.testStart;
			QUnit.testStart = function (info) {
				if (otherStart) {
					otherStart(info);
				}
				ajaxData.reset();
			};
		}
	
		return ajaxData;
	};
})(jQuery);
