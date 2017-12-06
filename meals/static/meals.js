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
		console.log(this);
		var post_data = {
			'choose_unit_type':$('input[name=choose_unit_type]:checked').val(),
			'gender':$('input[name=gender]:checked').val(),
			'age':$('#id_age').val(),
			'activity':$('input[name=activity]:checked').val(),
			'direction':$('input[name=direction]:checked').val(),
			'protein_percent':$('#id_protein_percent').val(),
			'fat_percent':$('#id_fat_percent').val(),
			'carbs_percent':$('#id_carbs_percent').val(),
			'protein_g':$('#id_protein_g').val(),
			'fat_g':$('#id_fat_g').val(),
			'carbs_g':$('#id_carbs_g').val(),
			'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
		};
		if (post_data['choose_unit_type'] == 'imperial') {
			post_data['i_weight'] = $('input[name=i_weight]').val();
			post_data['i_height_0'] = $('input[name=i_height_0]').val();
			post_data['i_height_1'] = $('input[name=i_height_1]').val();
			post_data['i_change_rate'] = $('input[name=i_change_rate]').val();
		} else {
			post_data['m_weight'] = $('input[name=m_weight]').val();
			post_data['m_height'] = $('input[name=m_height]').val();
			post_data['m_change_rate'] = $('input[name=m_change_rate]').val();
		}
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
