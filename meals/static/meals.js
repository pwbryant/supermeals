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
		console.log(post_data);
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
