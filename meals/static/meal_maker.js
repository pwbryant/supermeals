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
		} else { obj.CAL_GOAL = 0;
		}	
	},
	set_macro_bar_vars = function(obj) {
		obj.SCALE_CAL_TO_HEIGHT.domain([0,obj.CAL_GOAL]);
		obj.SCALE_CAL_TO_HEIGHT.range([0,obj.CAL_BAR_HEIGHT]);
		obj.MACROS_SVG =d3.select('#id_goal_macros_svg') 
		obj.MACROS= {};
		var svg_width = $('#id_goal_macros_svg').width(),
		max_bar_height =$('#id_goal_macros_svg').height() * .5, 
		space = svg_width * .1,
		bar_space = space / 3.0,
		bar_width = (svg_width - space) / 4.0,
		macro_names = ['cals','fat','carbs','protein'];

		for(i=0; i<macro_names.length;i++) {
			var macro = macro_names[i];
			if (macro === 'cals') {
				obj.MACROS[macro] = {'ratio':1}
			} else {
				obj.MACROS[macro] = {'ratio':$('#id_goal_meal_' + macro  + '_percent').val()/100.0}
			}
			obj.MACROS[macro]['height'] = max_bar_height * obj.MACROS[macro]['ratio'];
			obj.MACROS[macro]['width'] = bar_width;
			obj.MACROS[macro]['x'] = i * (bar_width + bar_space);
			obj.MACROS[macro]['y'] = max_bar_height - obj.MACROS[macro]['height'];
			obj.MACROS[macro]['macro'] = macro;
		}
	},
	create_macro_bars = function(obj) {
		var macro_data = Object.values(obj.MACROS);
		obj.MACROS_SVG.selectAll(".goal_bars").data(macro_data)
			.enter()
			.append('rect')
			.attr({
				"height": function(d) { return d.height; },
				"width": function(d) { return d.width; },
				"x": function(d) { return d.x; },
				"y": function(d) { return d.y; },
				'class': '.goal_macro_bars',
				'fill':'red',
				'stroke':'black',
				'id': function(d) { return 'id_goal_' + d.macro + '_bar'; }
			});
	};

	//macro breakdown functions 
	return {
		CAL_GOAL: 0,//initialize value
		CAL_BAR_HEIGHT: 200,
		CAL_BAR_WIDTH: 200,
		SCALE_CAL_TO_HEIGHT : d3.scale.linear().domain([0,1]).range([0,1]),//initialize value
		create_macro_button_trigger : function() {
			mm_funk_obj = this;
			$('#id_create_macro_bars_button').on('click',function() {
				set_macro_bar_vars(mm_funk_obj);
				create_macro_bars(mm_funk_obj);
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
	var create_macro_bar = function(macro_name,macro_amt,) {
	}
	*/
})();
