function launch_reading(event) {
	var link = $(this).attr('link');
	if (link) {
		console.log('launching to ' + link);
		//window.location = link;
	}
}

function create_reading_callback(data, text_status, jq_xhr) {
	console.log(data);
	var $new_reading = $('#_template_').clone();
	var when = new Date(data.when);
	$new_reading.prop('id', data._id)
	            .attr('link', data.link)
	            .addClass($('div.reading').length % 2 == 0 ? 'even' : 'odd')
	            .click(launch_reading)
	            .mouseenter(show_menu);
	$new_reading.children('div.title').html(data.title);
	$new_reading.children('div.details')
		        .children('span[rel="link"]').html(data.link);
	$new_reading.children('div.details')
		        .children('span[rel="when"]')
		        .html(when.toGMTString());
	$new_reading.click(launch_reading)
	            .insertBefore($('#add_reading_form'))
	            .fadeIn('slow');
	reset_form();
}

function show_menu(event) {
	$('#menu').css('top', $(this).prop('offsetTop') + 5)
		      .attr('target', $(this).attr('id'))
		      .show();
}

function show_error_callback(jq_xhr, text_status, error_thrown) {
	console.log('status ' + text_status);
	console.log('error_thrown ' + error_thrown);
}

function remove_context_element() {
	$('#menu').hide();
	$(this).fadeOut('slow', function() { $(this).remove(); });
}

function clear_if_defaulted() {
	if ($(this).val() == $(this).prop('defaultValue')) {
		$(this).val('');
	}
}

function reset_if_empty(target) {
	if (target.value == '') {
		target.value = target.defaultValue;
	}
}

function remove_reading(event) {
	var reading_id = $(this).attr('target');
	var div_element = document.getElementById(reading_id);
	console.log('removing reading ' + reading_id);
	$.ajax({
		url: '/readings/' + reading_id,
		context: jQuery(div_element),
		success: remove_context_element,
		error: show_error_callback,
		type: 'DELETE'
	});
}

function reset_form() {
	$("input").each(function(index, element) {
		element.value = element.defaultValue;
	});
}


