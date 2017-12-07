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
			$('#id_my_macros_form_container').html(data);
		});
	});
};

//not tested
var post_my_macros_form = function() {
	$('#id_save_my_macros').on('click',function() {
		var post_data = {};
		$("#id_my_macros_form_container").find(":input[type=text],:input[type=hidden],:input[type=radio]:checked").each(function() {
		    post_data[this.name] = $(this).val();
		});
		$.post('/meals/save_my_macros',post_data,function(data) {
			
			if (data == '1') {
				$.get('/meals/get_my_macros/',function(data) {
					$('#id_my_macros_form_container').html(data);
				});
			} else {
				$('#id_my_macros_form_container').html(data);
			}
			
		});
	});
}



//tested
var switch_between_imperial_metric = function() {
	$('input[name=choose_unit_type]').on('click',function() {	
		var unit_type = $('input[name=choose_unit_type]:checked').val();
		if (unit_type == 'metric') {
			$('#id_weight_cell').html('<input id="id_m_weight" type="text" name="m_weight" class="form-control input-sm" placeholder="kg"/>');		
			$('#id_height_row').html('<td><span id="id_height_label"><b>Height:</b></span></td><td><input id="id_m_height" type="text" name="m_height" class="form-control input-sm" placeholder="cm"/></td>');		
			$('#id_change_rate_div').html('<input id="id_m_change_rate" type="text" name="m_change_rate" class="form-control input-sm" placeholder="kg/wk"/>');		
		} else {
			$('#id_weight_cell').html('<input id="id_i_weight" type="text" name="i_weight" class="form-control input-sm" placeholder="lb"/>');		
			$('#id_height_row').html('<td><span id="id_height_label"><b>Height:</b></span></td><td><input id="id_i_height_0" type="text" name="i_height_0" class="form-control input-sm" placeholder="ft"/></td><td><input id="id_i_height_1" type="text" name="i_height_1" class="form-control input-sm" placeholder="in"/></td>');		
			$('#id_change_rate_div').html('<input id="id_i_change_rate" type="text" name="i_change_rate" class="form-control input-sm" placeholder="lb/wk"/>');		
		}
	});

}

var convert_to_metric = function(imperial_value,conversion) {

	
	if (conversion == 'in_to_cm') {
		return imperial_value/0.39370;	
	}
	if (conversion == 'lb_to_kg') {
		return imperial_value * 0.45359237;	
	}
}

var calc_tdee = function() {
	
	$('#id_calc_tdee').on('click',function() {	
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
			if (tdee_data['choose_unit_type'] == 'imperial') {
				tdee_data['weight'] = convert_to_metric(tdee_data['i_weight'],'lb_to_kg');
				tdee_data['height'] = convert_to_metric(tdee_data['i_height_0'] * 12 + tdee_data['i_height_1'],'in_to_cm');
				tdee_data['change_rate'] = convert_to_metric(tdee_data['i_change_rate'],'lb_to_kg');
			} else {
				tdee_data['weight'] = tdee_data['m_weight'];
				tdee_data['height'] = tdee_data['m_height_0'];
				tdee_data['change_rate'] = tdee_data['m_change_rate'];
			}
			var formula_data_by_gender = {
				"f": {
					'base_add':655,
					'weight':9.6 * tdee_data['weight'],
					'height':1.8 * tdee_data['height'],
					'age':4.7 * tdee_data['age']
				},
				'm': {
					'base_add':66,
					'weight':13.7 * tdee_data['weight'],
					'height':5 * tdee_data['height'],
					'age':6.8 * tdee_data['age']
				}
			},
			activity_data = {
				"none":1.2,
				"light":1.375,
				"medium":1.55,
				"high":1.725,
				"very high":1.9
			},
			formula_data = formula_data_by_gender[tdee_data['gender']],
			tdee_return_value = (formula_data['base_add'] + formula_data['weight'] + formula_data['height'] - formula_data['age']) * activity_data[tdee_data['activity']];
			
		} else {
			tdee_return_value = 'Missing Value. Check Form.';
		}
		$('#id_tdee_result').html(Math.round(tdee_return_value));
	});
}
