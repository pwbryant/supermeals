var MM_FUNK = (function() { 
	const MACRO_FACTORS = {
		'fat':9,
		'carbs':4,
		'protein':4
	};
    const MACRO_NAMES = ['cals', 'fat', 'carbs', 'protein'];
    const enable_disable_create_macro_bars_button = function(obj) {
		var pct_amt = parseFloat($('#goal-meal-macro-percent-total').html());
		if (pct_amt == 0 && obj.CAL_GOAL != 0) {
			$('#create-macro-bars-button').attr('disabled',false)
		} else {
			$('#create-macro-bars-button').attr('disabled',true)
		}
	};
    const goal_meal_macro_percent_totaler = function(this_) {
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

	};
    const get_goal_meal_cals_and_set_grams= function(this_) {
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
	};
	const convert_macro_pct_grams = function(this_) {
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

	};
	const set_mm_funk_goal_cals = function(obj,this_) {
		if ($.trim(this_.value) != 'header' && $.trim(this_.value) != '' && isNaN(this_.value) == false) {
			obj.CAL_GOAL = parseFloat(this_.value);
		} else { obj.CAL_GOAL = 0;
		}	
	};
	const create_macros_obj = function(obj) {
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
	};
	const create_macro_bars = function(obj) {
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
	};
	const create_macro_error_bars = function(obj) {
		
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
	};
	const create_macro_bar_labels = function(obj) {
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
		
	};
	const format_food_search_results = function(search_results) {

		var search_results_html = '';	
		search_results.forEach(function(e,i) {
			search_results_html += "<div class='search-result'><span>" + e.name + "</span><button id='search-result-food-" + i + "' class='icon'><i class='fa fa-plus'></i></button></div>"; 
		});
		return search_results_html;
	};
	const meal_maker_food_search = function(obj) { var search_terms = $.trim($('#meal-maker-food-search-input').val());
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
	};
	const create_food_macros_obj = function(search_add_button,obj) {
		var search_result_index = parseFloat(search_add_button.id[search_add_button.id.length-1]),
		search_result_obj = obj.SEARCH_RESULTS[search_result_index];
        return search_result_obj;
        
	};
    const create_ingredient_macro_containers = function(food_macros_obj) {
        
        let food_div = `<div id='ingredient-${food_macros_obj.id}-container' class='ingredient-container'>`;
        food_div += `<div class='ingredient-container-header'>header</div>`;
        food_div += `<div id='ingredient-${food_macros_obj.id}-bars' class='ingredient-container-bars'>`;
        for (let i=0; i<4; i++) {
            food_div += `<svg id='ingredient-${food_macros_obj.id}-${MACRO_NAMES[i]}-svg' class='ingredient-${food_macros_obj.id}-svg ingredient-macro-svg' style='height:100%;width:20%'></svg>`;

        }
        food_div += '</div>';
        food_div += "<div class='ingredient-container-footer'>footer</div>";
        food_div += '</div>'; 
            
        $('#meal-maker-ingredient-content').append(food_div);
    };
    const create_ingredient_macros_bars = function(food_macros_obj) {


        const cals_per_gram = food_macros_obj['cals_per_gram'];

        $(`.ingredient-${food_macros_obj.id}-svg`).each(function(i,e) {
            let svg = d3.select(`#${e.id}`);
            const svg_height = $(`#${e.id}`).height();
            const macro = e.id.split('-')[2]; //id format ingrdient-id-macro-svg
            const macro_per_gram = food_macros_obj[`${macro}_per_gram`];
            const macro_to_cal_ratio = macro_per_gram / cals_per_gram;
            const rect_height = svg_height * macro_to_cal_ratio;
            svg.selectAll('.rects')
                .data([food_macros_obj])
                .enter()
                .append('rect')
                .attr('height', rect_height)
                .attr('width', '100%')
                .attr('y', svg_height - rect_height)
                .attr('fill', 'black');
        });
    };
    

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
                create_ingredient_macro_containers(food_macros_obj);
                create_ingredient_macros_bars(food_macros_obj);
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
