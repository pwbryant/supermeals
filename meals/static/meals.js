//tested
var initialize = function () {
	$('input[type="text"]').on('keypress',function() {
		$('.has-error').hide();
	});
};

//tested
var hide_home_header_on_tab_select = function() {
	$('.nav-tabs').on('click',function() {
		$("#id_home_headline").hide();
	});
};

//not tested
var get_my_macros_page_content = function() {
	$('#id_my_macros_tab_label').on('click',function() {
		$.get('/meals/get_my_macros/',function(data) {
			console.log(data);
			$('#id_my_macros_tab').append(data);
		});
	});
};

//tested
var switch_between_imperial_metric = function(height_form_content,unit_type) {
	console.log('switch');
	$('#id_height_div').html(height_form_content);
	
	if (unit_type == 'metric') {
		$('#id_weight').attr('placeholder','kg');		
		$('#id_height').attr('placeholder','cm');		
		$('#id_change_rate').attr('placeholder','kg/wk');
	} else {
		$('#id_weight').attr('placeholder','lb');		
		$('#id_height_0').attr('placeholder','ft');		
		$('#id_height_1').attr('placeholder','in');		
		$('#id_change_rate').attr('placeholder','lb/wk');
	}
}
