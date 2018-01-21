var MM_FUNK = (function() { 
	var MACRO_FACTORS = {
		'fat':9,
		'carbs':4,
		'protein':4
	},enable_disable_create_macro_bars_button = function(obj) {
		var pct_amt = parseFloat($('#id_goal_meal_macro_percent_total').html());
		if (pct_amt == 0 && obj.CAL_GOAL != 0) {
			$('#id_create_macro_bars_button').attr('disabled',false)
		} else {
			$('#id_create_macro_bars_button').attr('disabled',true)
		}
		
	},goal_meal_macro_percent_totaler = function(this_) {
		var percent_id = 'id_goal_meal_' + $(this_).attr('id').split('_')[3]  + '_percent', 
		new_macro_percent = parseFloat($('#' + percent_id).val());

		if (isNaN(new_macro_percent)) {
			new_macro_percent = 0;
		} 
		var old_macro_percent = parseFloat($('#' + percent_id).attr('data-value')),
		percent_diff = new_macro_percent - old_macro_percent,
		old_percent_total = parseFloat($('#id_goal_meal_macro_percent_total').html()),
		new_percent_total = old_percent_total - percent_diff;
		$('#id_goal_meal_macro_percent_total').html(new_percent_total);
		$('#' + percent_id).attr('data-value',new_macro_percent);
	},get_goal_meal_cals_and_set_grams= function(this_) {
		if ($.trim(this_.value) != 'header' && $.trim(this_.value) != '' && isNaN(this_.value) == false) {
			var cals = parseFloat(this_.value),
			fat_percent = parseFloat($('#id_goal_meal_fat_percent').val()),
			carbs_percent = parseFloat($('#id_goal_meal_carbs_percent').val()),
			protein_percent = parseFloat($('#id_goal_meal_protein_percent').val()),
			fat_grams = Math.round(fat_percent / 100 * cals / 9),
			carbs_grams = Math.round(carbs_percent / 100 * cals / 4),
			protein_grams = Math.round(protein_percent / 100 * cals / 4)
			;
			$('#id_goal_meal_fat_g').val(fat_grams);
			$('#id_goal_meal_carbs_g').val(carbs_grams);
			$('#id_goal_meal_protein_g').val(protein_grams);
		} else {
			$('#id_goal_meal_fat_g').val('-');
			$('#id_goal_meal_carbs_g').val('-');
			$('#id_goal_meal_protein_g').val('-');
		}
	},
	convert_macro_pct_grams = function(this_) {
		var cals = $('#id_goal_meal_cals').val();
		if (cals == '') {
			cals = parseFloat($('#id_goal_meal_cals_select').find(':selected').val());
		} else {
			cals = parseFloat(cals);
		}
		var input_array = this_.id.split('_'),
		macro_value = parseFloat(this_.value),
		macro = input_array[3],
		type = input_array[4],
		macro_factor = MACRO_FACTORS[macro];

		if (type == 'percent') {
			return_value = (cals * macro_value / 100.0 / macro_factor).toFixed(0);
			var return_id = '#id_goal_meal_' + macro + '_g';
		} else {
			return_value = (macro_value * macro_factor / cals * 100).toFixed(0);	
			var return_id = '#id_goal_meal_' + macro + '_percent';
		}
		if (isNaN(macro_value)) {
			$(return_id).val('');
		} else {
			$(return_id).val(return_value);
		}

	},
	set_mm_funk_goal_cals = function(obj,this_) {
		if ($.trim(this_.value) != 'header' && $.trim(this_.value) != '' && isNaN(this_.value) == false) {
			obj.CAL_GOAL = parseFloat(this_.value);
		} else {
			obj.CAL_GOAL = 0;
		}	
	};

	//macro breakdown functions
	return {
		CAL_GOAL: 0,//initialize value
		CAL_BAR_HEIGHT: 200,
		SCALE_CAL_TO_HEIGHT : d3.scale.linear().domain([0,1]).range([0,1]),//initialize value
		create_macro_button_sets_bar_vars : function() {
			mm_funk_obj = this;
			$('#id_create_macro_bars_button').on('click',function() {
				mm_funk_obj.SCALE_CAL_TO_HEIGHT.domain([0,mm_funk_obj.CAL_GOAL]);
				mm_funk_obj.SCALE_CAL_TO_HEIGHT.range([0,mm_funk_obj.CAL_BAR_HEIGHT]);
			});
		},
		goal_cal_inputs_trigger : function() {
			mm_funk_obj = this;
			$('.goal_cal_inputs').on('keyup change',function() {
				set_mm_funk_goal_cals(mm_funk_obj,this);
				get_goal_meal_cals_and_set_grams(this);
				enable_disable_create_macro_bars_button(mm_funk_obj);
				if ($(this).attr('id') == 'id_goal_meal_cals') {
					$('#id_goal_meal_cals_select>option:eq(0)').prop('selected',true);
				} else {
					$('#id_goal_meal_cals').val('');
				}
			});
		},
		goal_meal_choose_macro_handler : function() {
			mm_funk_obj = this;
			$('.choose_macros').on('keyup',function() {	
				convert_macro_pct_grams(this);
				goal_meal_macro_percent_totaler(this);
				enable_disable_create_macro_bars_button(mm_funk_obj);
			});
		},
		set_initial_macro_percent_tally : function() {
			var fat = parseFloat($('#id_goal_meal_fat_percent').val()),
			carbs = parseFloat($('#id_goal_meal_carbs_percent').val()),
			protein = parseFloat($('#id_goal_meal_protein_percent').val());
			if(isNaN(fat)) {
				$('#id_goal_meal_macro_percent_total').html('100');
			} else {
				var total = 100 - (fat + carbs + protein);
				$('#id_goal_meal_macro_percent_total').html(total);
			}
		}
	};
	//macro bar functions
	//scope function
	//constants
	/*
	var GOAL_BAR_HEIGHT = '100px',
		GOAL_BAR_WIDTH = '50px',
		SCALE_GOAL_MACRO_TO_HEIGHT = d3.scale.linear().domain()
	var create_macro_bar = function(macro_name,macro_amt,) {
		var svg = d3.select('#id_goal_cal_bar_div').append('svg')
				.attr('width','50px')
				.attr('height','100px')
				.attr('id','id_goal_cal_bar')
		
		svg.selectAll(".goal_bars").data([macro_amt])
			.enter()
			.append('rect')
			.attr({
				'height':'100%',
				'weight':'100%'
			})
	}
	*/
})();
