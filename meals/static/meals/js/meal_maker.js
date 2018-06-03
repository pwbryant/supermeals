var MM_FUNK = (function() { 
	var MACRO_FACTORS = {
		'fat':9,
		'carbs':4,
		'protein':4
	},
    enable_disable_create_macro_bars_button = function(obj) {
		var pct_amt = parseFloat($('#goal-meal-macro-percent-total').html());
		if (pct_amt == 0 && obj.CAL_GOAL != 0) {
			$('#create-macro-bars-button').attr('disabled',false)
		} else {
			$('#create-macro-bars-button').attr('disabled',true)
		}
	},
    goal_meal_macro_percent_totaler = function(this_) {
		let new_macro_percent = parseFloat($(this_).val());
		const old_macro_percent = parseFloat($(this_).attr('data-value'));

		if (isNaN(new_macro_percent)) {
			new_macro_percent = 0;
		} 

		const percent_diff = new_macro_percent - old_macro_percent;
		const old_percent_total = parseFloat($('#goal-meal-macro-percent-total').html());
		const new_percent_total = old_percent_total - percent_diff;

		$('#goal-meal-macro-percent-total').html(new_percent_total);
		$(this_).attr('data-value',new_macro_percent);

	},
    get_goal_meal_cals_and_set_grams= function(this_) {
		if ($.trim(this_.value) != 'header' && $.trim(this_.value) != '' && isNaN(this_.value) == false) {
			var cals = parseFloat(this_.value),
			fat_percent = parseFloat($('#goal-meal-fat-percent').val()),
			carbs_percent = parseFloat($('#goal-meal-carbs-percent').val()),
			protein_percent = parseFloat($('#goal-meal-protein-percent').val()),
			fat_grams = Math.round(fat_percent / 100 * cals / 9),
			carbs_grams = Math.round(carbs_percent / 100 * cals / 4),
			protein_grams = Math.round(protein_percent / 100 * cals / 4)
			;
			$('#goal-meal-fat-g').val(fat_grams);
			$('#goal-meal-carbs-g').val(carbs_grams);
			$('#goal-meal-protein-g').val(protein_grams);
		} else {
			$('#goal-meal-fat-g').val('-');
			$('#goal-meal-carbs-g').val('-');
			$('#goal-meal-protein-g').val('-');
		}
	},
	convert_macro_pct_grams = function(this_) {
		let cals = $('#goal-meal-cals').val();
		if (cals == '') {
			cals = parseFloat($('#goal-meal-cals-select').find(':selected').val());
		} else {
			cals = parseFloat(cals);
		}
        
		const input_array = this_.id.split('-');
		const macro_value = parseFloat(this_.value);
		const macro = input_array[2];
		const type = input_array[3];
		const macro_factor = MACRO_FACTORS[macro];
        let return_id = '#goal-meal-' + macro;
        let return_value;

		if (type == 'percent') {
			return_value = (cals * macro_value / 100.0 / macro_factor).toFixed(0);
			return_id += '-g';
		} else {
			return_value = (macro_value * macro_factor / cals * 100).toFixed(0);	
			return_id += '-percent';
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
	create_macros_obj = function(obj) {
		obj.SCALE_CAL_TO_HEIGHT.domain([0,obj.CAL_GOAL]);
		obj.SCALE_CAL_TO_HEIGHT.range([0,obj.CAL_BAR_HEIGHT]);
		obj.MACROS_SVG =d3.select('#goal-macros-svg') 
		obj.MACROS= {};
		var svg_width = $('#goal-macros-svg').width(),
		max_bar_height =$('#goal-macros-svg').height() * .85, 
		macro_label_y = $('#goal-macros-svg').height() * .90, 
		space = svg_width * .1,
		bar_space = space / 3.0,
		bar_width = (svg_width - space) / 4.0,
		macro_names = ['cals','fat','carbs','protein'];

		for(i=0; i<macro_names.length;i++) {
			var macro = macro_names[i];
			if (macro === 'cals') {
				obj.MACROS[macro] = {'ratio':1}
			} else {
				obj.MACROS[macro] = {'ratio':$('#goal-meal-' + macro  + '-percent').val()/100.0}
			}
			obj.MACROS[macro]['height'] = max_bar_height * obj.MACROS[macro]['ratio'];
			obj.MACROS[macro]['width'] = bar_width;
			obj.MACROS[macro]['x'] = i * (bar_width + bar_space);
			obj.MACROS[macro]['y'] = max_bar_height - obj.MACROS[macro]['height'];
			obj.MACROS[macro]['macro'] = macro;
			obj.MACROS[macro]['label'] = macro.charAt(0).toUpperCase() + macro.slice(1);
			obj.MACROS[macro]['label_y'] = macro_label_y; 
			obj.MACROS[macro]['error'] = max_bar_height * .1;
		}
	},
	create_macro_bars = function(obj) {
		var macro_data = Object.values(obj.MACROS);
		obj.MACROS_SVG.selectAll(".goal-bars").data(macro_data)
			.enter()
			.append('rect')
            .attr("height", function(d) { 
                return d.height; 
            })
            .attr("width", function(d) { return d.width; })
            .attr("x", function(d) { return d.x; })
            .attr("y", function(d) { return d.y; })
            .attr('class', '.goal-macro-bars')
            .attr('fill','red')
            .attr('stroke','black')
			.attr(	'id', function(d) {  
                    return 'goal-' + d.macro + '-bar'; }
			);
	},
	create_macro_error_bars = function(obj) {
		
		var macros_copy = Object.assign({},obj.MACROS);
		delete macros_copy['cals']; 
		macro_data = Object.values(macros_copy);
		obj.MACROS_SVG.selectAll(".goal-error-bars").data(macro_data)
			.enter()
			.append('rect')
            .attr('height', function(d) { return d.error; })
            .attr('width',  function(d) { return d.width * .1; })
            .attr('x', function(d) { return d.x + (d.width / 2) - (5/2); })
			.attr('y', function(d) { return d.y - (d.error / 2); })
			.attr('class', '.goal-error-bars')
			.attr('fill','green')
			.attr('id', function(d) { return 'goal-' + d.macro + '-error-bar'; }
			);
	},
	create_macro_bar_labels = function(obj) {
		var macro_data = Object.values(obj.MACROS);
		obj.MACROS_SVG.selectAll(".goal-bar-labels").data(macro_data)
			.enter()
			.append('text')
			.text(function(d) {
				if (d.macro != 'cals') {
					return d.label + ': 0g';
				} else {
					return d.label + ': 0';
				}
			})
            .attr('x', function(d) { return d.x; })
            .attr('y', function(d) { return d.label_y; })
            .attr('fill','black')
            .attr('id', function(d) { 
                return 'goal-' + d.macro + '-bar-label';
            })
            .attr('class', '.goal-macro-bar-label');
		
	},
	format_food_search_results = function(search_results) {

		var search_results_html = '';	
		search_results.forEach(function(e,i) {
			search_results_html += "<div class='search-result'><span>" + e.name + "</span><button id='search-result-food-" + i + "' class='icon'><i class='fa fa-plus'></i></button></div>"; 
		});
		return search_results_html;
	},
	meal_maker_food_search = function(obj) { var search_terms = $.trim($('#meal-maker-food-search-input').val());
		if(search_terms != '') {
			$.get('/meals/search-foods/',{'search_terms':search_terms},function(data) {
				var search_results = data['search-results'],
				search_results_html = '';
				if(search_results.length > 0) {
					obj.SEARCH_RESULTS = search_results; 
					search_results_html = format_food_search_results(search_results);
					$('#meal-maker-food-search-results-container').html(search_results_html);
					obj.add_search_result_button_trigger();
					obj.SEARCH_RESULT_ADD_BUTTON_LISTENER_EXISTS = true;
				} else {
					search_results_html = '<span>No Foods Found</span>';
					$('#meal-maker-food-search-results-container').html(search_results_html);
				}

			});
		} else {
			$('#meal-maker-food-search-input').val('');
			$('#meal-maker-food-search-results-container').html('');
		}
	},
	create_food_macros_obj = function(search_add_button,obj) {
		var search_result_index = parseFloat(search_add_button.id[search_add_button.id.length-1]),
		search_result_obj = obj.SEARCH_RESULTS[search_result_index];
        console.log(search_result_obj);
        return search_result_obj;
        
	},
    create_result_html_svg = function(food_macros_obj) {
        console.log('in html svg funk');
        let food_div = "<div class='ingredient-container'>";
        food_div += '</div>';
        $('#meal-maker-ingredient-content').append(food_div);
    }
    ;

	//macro breakdown functions 
	return {
		CAL_GOAL: 0,//initialize value
		CAL_BAR_HEIGHT: 200,
		CAL_BAR_WIDTH: 200,
		SCALE_CAL_TO_HEIGHT : d3.scaleLinear().domain([0,1]).range([0,1]),//initialize value
		SEARCH_RESULT_ADD_BUTTON_LISTENER_EXISTS: 0,
		add_search_result_button_trigger : function() {
			mm_funk_obj = this;
			$('.search-result>button').on('click',function() {
				const food_macros_obj = create_food_macros_obj(this,mm_funk_obj);
                create_result_html_svg(food_macros_obj);

			});
		},
		meal_maker_food_search_trigger: function() {
			mm_funk_obj = this;
			$('#food-search-icon-button').on('click',function() {
				meal_maker_food_search(mm_funk_obj);
			});
		},
		create_macro_button_trigger : function() {
			mm_funk_obj = this;
			$('#create-macro-bars-button').on('click',function() {
				create_macros_obj(mm_funk_obj);
				create_macro_bars(mm_funk_obj);
				create_macro_error_bars(mm_funk_obj);
				create_macro_bar_labels(mm_funk_obj);
			});
		},
		goal_cal_inputs_trigger : function() {
			mm_funk_obj = this;
			$('.goal-cal-inputs').on('keyup change',function() {
				set_mm_funk_goal_cals(mm_funk_obj,this);
				get_goal_meal_cals_and_set_grams(this);
				enable_disable_create_macro_bars_button(mm_funk_obj);
				if ($(this).attr('id') == 'goal-meal-cals') {
					$('#goal-meal-cals-select>option:eq(0)').prop('selected',true);
				} else {
					$('#goal-meal-cals').val('');
				}
			});
		},
		goal_meal_choose_macro_handler : function() {
			mm_funk_obj = this;
			$('.choose-macros').on('keyup',function() {	
				convert_macro_pct_grams(this);
				goal_meal_macro_percent_totaler(this);
				enable_disable_create_macro_bars_button(mm_funk_obj);
			});
		},
		set_initial_macro_percent_tally : function() {
			var fat = parseFloat($('#goal-meal-fat-percent').val()),
			carbs = parseFloat($('#goal-meal-carbs-percent').val()),
			protein = parseFloat($('#goal-meal-protein-percent').val());
			if(isNaN(fat)) {
				$('#goal-meal-macro-percent-total').html('100');
			} else {
				var total = 100 - (fat + carbs + protein);
				$('#goal-meal-macro-percent-total').html(total);
			}
		}
	};
})();
