
$(document).ready(function() {
	module("Standard Library Tests");
	test("stdlib.object includes addMethod on new object", function() {
		var obj = stdlib.object(), m, methods = [];
		equal(typeof obj.addMethod, "function", "addMethod method exists");
		for (m in obj) {
			methods.push(m);
		}
		equal(methods.length, 1, "stdlib.object has one method");
	});

	test("stdlib.addHelp creates help property", function() {
		var func = function () {},
		    help = [ "line one", "line two" ].join("\n");
		stdlib.addHelp(func, "line one", "line two");
		ok(func.hasOwnProperty("help"), "func.help property is created");
		equal(func.help, help, "each help argument is a separate line");
	});

	test("obj.addMethod creates prototype property", function() {
		var o = stdlib.object();
		delete o.prototype;
		equal(o.prototype, undefined, "prototype does not exist");
		o.addMethod("newFunction", function() { return 1; });
		ok(o.hasOwnProperty("prototype"), "prototype was created");
		ok(o.prototype.hasOwnProperty("newFunction"),
			"method was added to prototype");
	});

	test("obj.addMethod creates method on instance", function() {
		var o = stdlib.object();
		o.addMethod("newFunction", function() { return 42; });
		ok(o.hasOwnProperty("newFunction"), "method was created");
		equal(o.newFunction(), 42, "method is callable");
	});

	test("obj.addMethod creates help as well", function() {
		var o = stdlib.object();
		o.addMethod("newFunction", function() { return 1; },
			"additional arguments", "are treated as help", "lines");
		equal(o.newFunction.help,
			"additional arguments\nare treated as help\nlines",
			"additional arguments to addMethod create newFunction.help");
	});

	test("stdlib.unwrapJSONRPC unwraps millisecond Date instances", function() {
		var encoded = { then: { __jsonclass__: [ "Date", 1335298365827 ] } };
		var decoded = stdlib.unwrapJSONRPC(encoded);
		equal(decoded.then.getTime(), 1335298365827,
				 "parameterized Date constructor returns millisecond-based Date");
	});

	test("stdlib.unwrapJSONRPC unwraps 'now' Date instances", function() {
		var now = new Date();
		var encoded = { then: { __jsonclass__: [ "Date" ] } };
		var decoded = stdlib.unwrapJSONRPC(encoded);
		equal(Math.round(decoded.then.getTime() / 10000),
			Math.round(now.getTime() / 10000),
			"parameterless Date constructor returns now");
	});

	test("stdlib.unwrapJSONRPC unwraps ObjectId instances", function() {
		ObjectId = function (value) {
			return new String(value.toString());
		}
		var encoded = { oid: { __jsonclass__: [
			"ObjectId", "4f78d1f94e02d89ba0000000" ] } };
		var decoded = stdlib.unwrapJSONRPC(encoded);
		equal(decoded.oid, "4f78d1f94e02d89ba0000000");
		delete window.ObjectId;
	});

	test("stdlib.unwrapJSONRPC ignores unencoded properties", function() {
		var encoded = { then: { __jsonclass__: [ "Date", 1335298365827 ] },
			simple: "a string", other: { number: 42 }, value: 13.0,
			flag: false, nothing: undefined };
		var decoded = stdlib.unwrapJSONRPC(encoded);
		var x;
		for (x in decoded) {
			if (encoded.hasOwnProperty(x)) {
				if (x !== "then") {
					equal(decoded[x], encoded[x],
						(typeof decoded[x]) + " was unmolested");
				}
			}
		}
	});

	test("stdlib.unwrapJSONRPC fails for long constructors", function() {
		var encoded = { obj: { __jsonclass__: [ "Date", 99, 12, 31 ] }};
		raises(
			function () {
				stdlib.unwrapJSONRPC(encoded);
			},
			function (thrown) {
				return thrown.name == 'ConstructorArgumentsTooLong';
			},
			"error thrown when more than one constructor argument is specified");
	});

});

