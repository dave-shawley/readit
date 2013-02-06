(function (jQuery, window, console) {
    readit = function (spec) {
        var that = stdlib.object();
        var args = spec || {};

        //
        // CSS selectors
        //
        var sel = {
            reading_li: args.reading_li_selector || "#reading",
            reading_info: args.reading_info_selector || "#readinginfo",
            template: args.template_class || "template",
            title: args.title_selector || ".title",
            when: args.when_selector || ".when",
            link: args.link_selector || ".link",
            url: args.url_selector || ".url",
            message: args.message_selectors || {}
        };

        //
        // Instance variables
        //
        var actions = args.actions || {};
        var debug = args.debug || false;

        //
        // Optional *helper* hooks
        //
        var setLocation = args.setLocation || function (url) {
            window.location.href = url;
        };

        // Patch the message selector defaults
        sel.message.selector = sel.message.selector || "#message";
        sel.message.status = sel.message.status || ".status";
        sel.message.phrase = sel.message.phrase || ".phrase";
        sel.message.error = sel.message.error || ".error";

        //
        // This is used as a constructor function to create new Reading objects
        //
        function Reading(data) {
            data = data || {};
            this.id = data.id;
            this.title = data.title;
            this.link = data.link;
            this.when = new Date();
            if (data.when) {
                try {
                    var d = new Date(data.when); // could throw an exception
                    d.toISOString(); // should Error out if date is invalid
                    this.when = d; // yippeeee! should have a valid data here
                } catch (e) {
                    // nothing to really do here... already assigned this.when
                }
            }
            this.jsonify = function () {
                return JSON.stringify({
                    title: this.title,
                    link: this.link,
                    when: this.when
                });
            };
        };

        //
        // Now for a few private/utility methods.
        //
        function updateUiForReading($uiElement, aReading) {
            $uiElement.find(sel.title).text(aReading.title);
            $uiElement.find(sel.when).text(aReading.when.toDateString());
            $uiElement.find(sel.link).prop({
                "href": aReading.link,
                "rel": "external"
            });
            $uiElement.find(sel.url).text(aReading.link);
        };

        function debugMessage() {
            if (!debug) {
                return;
            }
            console.log(">> DEBUG");
            var i;
            for (i=0; i<arguments.length; i+=1) {
                console.log(arguments[i]);
            }
            console.log("<< DEBUG");
        };

        function wasRedirected(ajaxData) {
            if (ajaxData && ajaxData.hasOwnProperty("redirect_to")) {
                debugMessage("handling redirect to " + ajaxData.redirect_to);
                setLocation(ajaxData.redirect_to);
                return true;
            }
            return false;
        };

        //
        // Public Methods
        //    These are exported by attaching them to ``that`` as we go.
        //
        function showReading(aReading) {
            updateUiForReading(jQuery(sel.reading_info), aReading);
        };
        that.addMethod("showReading", showReading,
            "Updates the UI to match a reading.");

        function update() {
            var $template = jQuery(sel.reading_li);
            $template
                .parent()
                .children()
                .filter(":not([class~=" + sel.template + "])")
                .remove();
            that.readings.forEach(function (aReading) {
                var $elm = jQuery("#" + aReading.id);
                if ($elm.length === 0) {
                    $elm = $template.clone();
                    $elm.prop("id", aReading.id);
                    $elm.removeClass(sel.template)
                        .insertBefore($template);
                }
                $elm.click(function () { showReading(aReading); });
                updateUiForReading($elm, aReading);
            });
        };
        that.addMethod("update", update,
            "Update the UI to match ``this.readings``.",
            "No parameters, no answer.");

        function addReading(aReading) {
            if (!actions['add-reading']) {
                debugMessage('no add-reading action defined');
                return;
            }
            jQuery.ajax({
                url: actions['add-reading'].url,
                type: actions['add-reading'].method,
                data: JSON.stringify(aReading),
                dataType: "json",
                contentType: "application/json;charset=UTF-8",
                success: function (data) {
                    debugMessage("addReading() success", data);
                    if (!wasRedirected(data)) {
                        that.readings.unshift(new Reading(data.new_reading));
                        that.update();
                        if (document.jqt) {
                            document.jqt.goBack();
                        }
                    }
                }
            });
        };
        that.addMethod("addReading", addReading,
            "Adds a reading to the list of readings.",
            "Requires a *reading* object that is sent to the server as-is.",
            "Answers by pushing the response onto ``this.readings``.");

        function fetchReadings() {
            if (!actions['get-readings']) {
                debugMessage('no get-readings action defined');
                return;
            }
            jQuery.ajax({
                url: actions['get-readings'].url,
                type: actions['get-readings'].method,
                dataType: "json",
                success: function (data) {
                    debugMessage("success", data);
                    that.readings = [];
                    data.readings.forEach(function (r) {
                        that.readings.push(new Reading(r));
                    });
                    that.update();
                }
            });
        };
        that.addMethod("fetchReadings", fetchReadings);

        function createReading(attrs) {
            return new Reading(attrs);
        };
        that.addMethod("createReading", createReading,
            "Creates a new Reading instance");

        //
        // Private methods & Helpers
        //
        function deserializeReading(aReading) {
            if (aReading.when) {
                aReading.when = new Date(aReading.when);
            }
            return aReading;
        };

        // Register an AJAX error handler to display messages if the
        // message div exists.
        var $messageBox = jQuery(sel.message.selector);
        if ($messageBox) {
            $messageBox.ajaxError(
                function (event, jqXHR, ajaxSettings, errorThrown) {
                    var $this = jQuery(this);
                    debugMessage("AJAX Error", jqXHR, errorThrown);
                    $this.find(sel.message.status).text(jqXHR.status);
                    $this.find(sel.message.phrase).text(jqXHR.statusText);
                    $this.find(sel.message.error).text(errorThrown);
                    $this.show();
                });
        }

        that.actions = actions;
        that.readings = args.readings || [];

        return that;
    };
}(jQuery, window, console));

