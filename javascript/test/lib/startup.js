$(document).ready(function() {
	if (!$.hasOwnProperty("debug")) {
		$.debug = false;
	}

	// mockedAjax is a global instance!!!
	mockedAjax = $.ajaxMock({debug: $.debug});
	if ($.debug) {
		QUnit.testDone = function (info) {
			if (console && console.log) {
				if (info.failed > 0) {
					console.log("FAIL " + info.name);
				} else {
					console.log("PASS " + info.name);
				}
			}
		};
	}
});
