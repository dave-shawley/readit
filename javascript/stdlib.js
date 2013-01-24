stdlib = (function() {
    var sliceArguments = Array.prototype.slice;
    var iface = Object.create(null);
    function addHelp() {
        var obj = arguments[0];
        var help = sliceArguments.call(arguments, 1);
        obj.help = help.join("\n");
    };
    iface.addHelp = addHelp;

    addHelp(iface,
        "Useful library routines",
        "This object has a bunch of utility methods attached.  All of the",
        "attached methods are free-standing functions that do not modify the",
        "stdlib instance.");

    iface.object = function (proto) {
        function F() {};
        F.prototype = proto || {};
        F.prototype.addMethod = function (name, method) {
            if (typeof this[name] != "function") {
                this[name] = method;
            }
            if (!this.prototype) {
                this.prototype = {};
            }
            this.prototype[name] = method;
            if (arguments.length > 2) {
                method.help = (sliceArguments.call(arguments, 2)).join("\n");
            }
        };
        return new F();
    };
    addHelp(iface.object, 
        "Creates a new object that correctly inherits anothers prototype.",
        "Expects an object and answers a new object using the other as its",
        "prototype.  The new object includes a helper method called addMethod",
        "which can be used to add a new named method to both the instance and",
        "it's prototype.",
        "See http://javascript.crockford.com/prototypal.html");
    
    iface.unwrapJSONRPC = function (value) {
        var propName, encoded, type;
        for (propName in value) {
            if (value[propName] &&
                Array.isArray(value[propName].__jsonclass__))
            {
                encoded = value[propName].__jsonclass__;
                type = encoded.shift();
                if (window.hasOwnProperty(type)) {
                    if (encoded.length === 0) {
                        value[propName] = new window[type]();
                    } else if (encoded.length === 1) {
                        value[propName] = new window[type](encoded[0]);
                    } else {
                        throw { name: 'ConstructorArgumentsTooLong' };
                    }
                }
            }
        }
        return value;
    };
    addHelp(iface.unwrapJSONRPC,
        "Unwrap a JSONRPC encoded object.",
        "Expects an object and answers the same object after modifications.",
        "JSONRPC encoding serializes object instances as objects that contain",
        "a single property named ``__jsonclass__``. The value assigned to this",
        "property is an Array that contains the object's constructor name",
        "followed by the values that should be passed into the constructor.",
        "For example, the following is an encoded Date instance:",
        "  var dateObj = {value: { __jsonclass__: ['Date', '1335298365827']}};",
        "This function will change the ``value`` property as follows:",
        "  dateObj.value = new Date(dateObj.value.__jsonclass__[1]);",
        "See http://json-rpc.org/wiki/specification#a3.JSONClasshinting");

    return iface;
}());

