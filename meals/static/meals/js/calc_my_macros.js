
MACRO_FACTORS = {
	'fat': 9,
	'protein':4,
	'carbs':4
};
//tested
var key_press_hides_error = function () {
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
	$('#my-macros-tab').on('click',function() {
		$.get('/meals/get-my-macros/',function(data) {
			$('#my-macros-container').removeClass("hide");
			$('#my-macros-container').html(data);
		});
	});
};

//not tested
var get_meal_maker_page_content = function() {
	$('#meal-maker-tab').on('click',function() {
		$.get('/meals/meal-maker/',function(data) {
			$('#id-meal-maker-container').html(data);
		});
	});
};

//not tested
var save_my_macros_button_posts_form = function() {
	$('#id_save_my_macros_button').on('click',function() {
		var form_validated = form_validation('id_my_macros_form_container');
		if (form_validated) {
			var post_data = {};
			$("#id_my_macros_form_container").find(":input[type=text],:input[type=hidden],:input[type=radio]:checked").each(function() {
			    post_data[this.name] = $(this).val();
			});
			$.post('/meals/save_my_macros',post_data,function(data) {
				if (data == '1') {
					$('#id_my_macros_successful_save_div').show();
				} else {
					$('#id_my_macros_form_container').html(data);
				}
				
			});
		}
	});
}



//tested
var switch_between_imperial_metric = function() {
	$('input[name=unit_type]').on('click',function() {	
		var unit_type = $(this).val();
		if (unit_type == 'metric') {
			$('#id_weight_div').html('<label for=id_weight>Weight:</label><span id="id_weight"><input id="id_m_weight" type="text" name="m_weight" class="form-control input-sm" placeholder="kg" data-type="number" />');	
			$('#id_height_div').html('<label for="id_height">Height:</label><span id="id_height"><input id="id_m_height" type="text" name="m_height" class="form-control input-sm" placeholder="cm" data-type="number"/>');		
			$('#id_change_rate_div').html('<label for="id_change_rate">Rate of Change</label><span id="id_change_rate"><input id="id_m_change_rate" type="text" name="m_change_rate" class="form-control input-sm" placeholder="kg/wk" data-type="number"/></span>');		
		} else {
			$('#id_weight_div').html('<label for=id_weight>Weight:</label><span id="id_weight"><input id="id_i_weight" type="text" name="i_weight" class="form-control input-sm" placeholder="lb" data-type="number"/>');
			$('#id_height_div').html('<label for="id_height">Height:</label><span id="id_height"><input id="id_i_height_0" type="text" name="i_height_0" class="form-control input-sm" placeholder="ft" data-type="number"/><input id="id_i_height_1" type="text" name="i_height_1" class="form-control input-sm" placeholder="in" data-type="number"/></span>');
			$('#id_change_rate_div').html('<label for="id_change_rate">Rate of Change</label><span id="id_change_rate"><input id="id_i_change_rate" type="text" name="i_change_rate" class="form-control input-sm" placeholder="lb/wk" data-type="number"/></span>');		
		}
	});

}
//tested
var convert_between_metric_english = function(unit_value,conversion) {

	
	if (conversion == 'in_to_cm') {
		return unit_value/0.39370;	
	}
	if (conversion == 'lb_to_kg') {
		return unit_value * 0.45359237;	
	}
	if (conversion == 'kg_to_lb') {
		return unit_value / 0.45359237;	
	}
}
//tested
var calc_tdee = function() {
	
	$('#id_calc_tdee').on('click',function() {	
		var form_validated = form_validation('id_tdee_form_container');
		if (form_validated) {
			var status_ = 1,
			tdee_data = {};
			$("#id_tdee_form_container").find(":input[type=text],:input[type=radio]:checked").each(function() {
				
				if ($(this).val() == '') {
					status_ = 0;	
				} else {
					if (isNaN($(this).val())) {
						tdee_data[this.name] = $(this).val();
					} else {
						tdee_data[this.name] = parseFloat($(this).val());
					}	
				}		
			});
			if (status_ == 1) {
				var weight_change_direction = {
					'maintain': 0,
					'lose': -1,
					'gain': 1,
				}[tdee_data['direction']];
				if (tdee_data['unit_type'] == 'imperial') {
					tdee_data['weight'] = convert_between_metric_english(tdee_data['i_weight'],'lb_to_kg');
					tdee_data['height'] = convert_between_metric_english(tdee_data['i_height_0'] * 12 + tdee_data['i_height_1'],'in_to_cm');
					tdee_data['change_rate'] = tdee_data['i_change_rate'] * weight_change_direction * 500;
				} else {
					tdee_data['weight'] = tdee_data['m_weight'];
					tdee_data['height'] = tdee_data['m_height'];
					tdee_data['change_rate'] = convert_between_metric_english(tdee_data['m_change_rate'],'kg_to_lb') * weight_change_direction * 500;
				}
				var formula_data = {
					"f":-161,
					'm':5,
					'weight':10 * tdee_data['weight'],
					'height':6.25 * tdee_data['height'],
					'age':5 * tdee_data['age']
				},
				activity_data = {
					"none":1.2,
					"light":1.375,
					"medium":1.55,
					"high":1.725,
					"very high":1.9
				},
				tdee_return_value = (formula_data['weight'] + formula_data['height'] - formula_data['age']  + formula_data[tdee_data['gender']]) * activity_data[tdee_data['activity']],
				change_tdee_return_value = ((formula_data['weight'] + formula_data['height'] - formula_data['age']  + formula_data[tdee_data['gender']]) * activity_data[tdee_data['activity']]) + tdee_data['change_rate'];
				
			} else {
				tdee_return_value = 'Missing Value. Check Form.';
			}
			$('#id_tdee_result').html(Math.round(tdee_return_value));
			$('#id_change_tdee_result').html(Math.round(change_tdee_return_value));
			$('#id_hidden_tdee').val(Math.round(change_tdee_return_value));
			
			$('#id_choose_macros_form_container').show();
		}
	});
}

//tested
var change_change_rate_display = function() {
	$('input[name=direction]').on('click',function() {
		if (this.value == 'maintain') {
			$('#id_change_rate_div').css('display','none');
			$('.change_rate').val('');
		} else {
			$('#id_change_rate_div').css('display','block');
		}	
	});
}

//tested
var choose_macro_handler = function() {
	$('.choose_macros').on('keyup',function() {	
		if ($('#id_change_tdee_result') != '') {	
			var tdee_result = $('#id_change_tdee_result').html();
		} else {
			var tdee_result = $('#id_tdee_result').html();
		}
		var input_array = this.id.split('_'),
		macro_value = parseFloat(this.value),
		macro = input_array[1],
		type = input_array[2],
		macro_factor = MACRO_FACTORS[macro];
		if (type == 'percent') {
			return_value = (tdee_result * macro_value / 100.0 / macro_factor).toFixed(0);
			var return_id = '#id_' + macro + '_g';
		} else {
			return_value = (macro_value * macro_factor / tdee_result * 100).toFixed(0);	
			var return_id = '#id_' + macro + '_percent';
		}
		if (isNaN(macro_value)) {
			$(return_id).val('');
		} else {
			$(return_id).val(return_value);
		}
		macro_percent_totaler('id_' + macro + '_percent')
	});
}

//tested
var macro_percent_totaler = function(percent_id) {
	var new_macro_percent = parseFloat($('#' + percent_id).val());

	if (isNaN(new_macro_percent)) {
		new_macro_percent = 0;

	} 
	old_macro_percent = parseFloat($('#' + percent_id).attr('data-value')),
	percent_diff = new_macro_percent - old_macro_percent,
	old_percent_total = parseFloat($('#id_macro_percent_total').html()),
	new_percent_total = old_percent_total - percent_diff;
	$('#id_macro_percent_total').html(new_percent_total);
	$('#' + percent_id).attr('data-value',new_macro_percent);
	if (new_percent_total == 0) {
		$('#id_choose_macros_continue_button').prop('disabled',false);
	} else {
		$('#id_choose_macros_continue_button').prop('disabled',true);
	}
}

//tested
var continue_button_displays_meal_snack_num_div = function() {
	$('#id_choose_macros_continue_button').on('click', function() {
		var form_validated = form_validation('id_choose_macros_form_container');
		if (form_validated) {
			$('#id_meal_template_meals_number_form_container').show();
		}
	});

}

//tested
var set_cals_continue_button_is_enabled_upon_input_keyup = function() {

	$('#id_meal_template_meals_number').on('keyup',function() {
		var input_value = $(this).val();
		if (!(isNaN(input_value) | input_value == 0)) {
			$('#id_meal_template_set_cals_continue_button').prop('disabled',false);
		} else {

			$('#id_meal_template_set_cals_continue_button').prop('disabled',true);
		}
	});
}

//tested
var display_set_cals_form = function() {

	$('#id_meal_template_set_cals_continue_button').on('click',function() {
		var tdee = $('#id_change_tdee_result').html(),
		meal_num = $('#id_meal_template_meals_number').val();
		if (tdee == '') {
			tdee = $('#id_tdee_result').html();
		}
		var equal_cals = tdee / meal_num,
		set_cals_form = '';

		for (i=0;i<meal_num;i++) {
			set_cals_form += '<div id="id_meal_' + i + '_div"><label for="meal_' + i + '">Meal ' + (i + 1) + '</label><input name="meal_' + i + '" type="text" value="' + equal_cals + '" data-value="' + equal_cals + '" data-type="number"/></div><br>';
		}
		set_cals_form += '<label for="remaining_cals">Remaining Cals</label><span id="id_meal_template_set_cals_total" name="remaining_cals">0</span>';
		set_cals_form += '<br><button id="id_save_my_macros_button" class="btn">Save Macro Info</button>';
		$('#id_meal_template_set_meal_cals_form_container').html(set_cals_form)
		save_my_macros_button_posts_form();
		meal_template_set_cals_totaler();//start lister on new inputs 

	});
}

//tested
var meal_template_set_cals_totaler = function() {

	$('#id_meal_template_set_meal_cals_form_container input').on('keyup',function() {
		current_cal_total = $('#id_meal_template_set_cals_total').html();
		var new_cal = parseFloat($(this).val());
		if (isNaN(new_cal)) {
			new_cal = 0;

		} 
		var old_cal = parseFloat($(this).attr('data-value')),
		cal_diff = new_cal - old_cal,
		old_cal_total = parseFloat($('#id_meal_template_set_cals_total').html()),
		new_cal_total = old_cal_total - cal_diff,
		tdee = $('#id_change_tdee_result').html();
		if (tdee === '') {
			tdee = $('#id_tdee_result').html();
		}
		
		$('#id_meal_template_set_cals_total').html(new_cal_total);
		$(this).attr('data-value',new_cal);
		if (new_cal_total == 0) {
			$('#id_save_my_macros_button').prop('disabled',false);
			$('#id_meal_template_set_cals_total').css('color','black');
		} else {
			$('#id_save_my_macros_button').prop('disabled',true);
			$('#id_meal_template_set_cals_total').css('color','red');
		}
	});
}

var form_validation = function(form_id) {
	var errors = [],
	radio_names = [];
	$('#' + form_id).find(':input[type=text],input[type=radio]:checked').each(function(index,element) {
		var value = $(element).val(),
		type = $(element).prop('type'),
		data_type = $(element).attr('data-type'),
		label = $(element).closest('div').find('label').text().replace(/[^a-zA-Z0-9_ ]/g,''),
		error = '';
		if (type == 'text' && value == '') {
			error = 'Missing ' + label + ' Value';
		} 
		if (type == 'text' && data_type == 'number'  && isNaN(value)) {
			error = label + ' Field Forbids Non-Numeric Values';
		}
		if (type == 'radio') {
			var name = $(element).prop('name');
			radio_names.push(name);
		} 
		if (error != '') {
			errors.push(error);
		}
	});

	$('#' + form_id).find('input[type=radio]').each(function(index,element) {
		var name = $(element).prop('name');
		if (!(radio_names.includes(name))) {
			var title_name = '';
			name.split('_').forEach(function(chunk) {
				title_name += chunk[0].toUpperCase() + chunk.slice(1) + ' ';
			});
			error = title_name.trim() + ' Option Needs To Be Selected';
			if (!(errors.includes(error))) {
				errors.push(error);
			}
		}
	});
	if (errors.length > 0) {
		var error_html = '<ul>';
		errors.forEach(function(error) {
			error_html += '<li>' + error + '</li>';
		});
		error_html += '</ul>';
		//$('#id_calc_tdee_errors').html(error_html);
		$('#id_client_side_form_errors').html(error_html);
		return 0;
	} else {
		//$('#id_calc_tdee_errors').html('');
		$('#id_client_side_form_errors').html('');
		return 1;
	}	
}
