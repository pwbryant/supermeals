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

	const create_macro_bars_obj = function() {
        let macros_bar_obj = {};
        macros_bar_obj.cal_bar_height = $('#goal-macros-bar-container').height() * .9;
		MACRO_NAMES.forEach(function(macro) {
            macros_bar_obj[macro] = {'name':macro};
			if (macro === 'cals') {
				macros_bar_obj[macro]['ratio'] = 1;
			} else {
				macros_bar_obj[macro]['ratio'] = $('#goal-meal-' + macro  + '-percent').val()/100.0
			}
		});
        return macros_bar_obj;
	};

    const create_macro_bar_container = function(macro) {

        macro_div = `<div id='${macro}-bar-container' class='macro-bar-container'>`;

        macro_div += `<svg id='${macro}-bar-svg' class='macro-bar-svg' style='height:90%;width:100%'></svg>`;

        macro_div += `<div id='${macro}-label-container' class='macro-label-container'></div>`

        macro_div += '</div>';
            
        $('#goal-macros-bar-container').append(macro_div);
    };

	const create_macro_bar = function(macro, macro_bars_obj) {

        macro_bars_obj[macro].svg = d3.select('#' + macro + '-bar-svg');
        macro_bars_obj[macro].macro_bar_height = macro_bars_obj.cal_bar_height * macro_bars_obj[macro].ratio;
        macro_bars_obj[macro].macro_y = macro_bars_obj.cal_bar_height - macro_bars_obj[macro].macro_bar_height 

		macro_bars_obj[macro].svg
            .selectAll(".goal-bars").data([macro_bars_obj[macro]])
			.enter()
			.append('rect')
            .attr("height", function(d) {
                return d.macro_bar_height
            }) 
            .attr('width', '100%')
            .attr('y', function(d) { 
                return d.macro_y;
            })
            .attr('id', `${macro}-goal-macro-bar`)
            .attr('class', '.goal-macro-bar')
            .attr('fill','white')
            .attr('stroke','black')
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

	const create_macro_bar_labels = function(macro, macro_bars_obj) {

        const macro_title = macro[0].toUpperCase() + macro.slice(1,);
        const label = `<span class='macro-label'>${macro_title}: </span>`;
        const amt = `<span id='${macro}-amt' class='macro-amt'>0</span>`;
        const unit = `<span class='macro-unit'>g</span>`;

        $(`#${macro}-label-container`).html(label + amt + unit);
		
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
					obj.add_food();
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
		food_macros_obj = obj.SEARCH_RESULTS[search_result_index];
        food_macros_obj.food_order = obj.FOOD_COUNT;
        food_macros_obj.cal_goal = obj.CAL_GOAL;
        food_macros_obj.food_amt = 0;
		MACRO_NAMES.forEach(function(macro) {
            food_macros_obj[macro] = {};
            food_macros_obj[macro].name = macro;
            food_macros_obj[macro].food_id = food_macros_obj.id;
            const macro_per_gram = `${macro}_per_gram`;
            food_macros_obj[macro][macro_per_gram] = food_macros_obj[macro_per_gram];
            food_macros_obj[macro].food_order = obj.FOOD_COUNT;
            food_macros_obj[macro].color_count = 10;
			if (macro === 'cals') {
				food_macros_obj[macro]['goal_ratio'] = 1;
			} else {
				food_macros_obj[macro]['goal_ratio'] = $('#goal-meal-' + macro  + '-percent').val()/100.0
			}

		});
        return food_macros_obj;
	};

    const add_scales_to_food_macros_obj = function(food_macros_obj) {

        const goal_cal_bar_height = $('#cals-bar-svg').height();
        food_macros_obj['cal_to_goal_cal_height_scale']= d3
            .scaleLinear()
            .domain([0,food_macros_obj.cal_bar_height])
            .range([0,goal_cal_bar_height]);

        const food_g_in_goal_cals = food_macros_obj.cal_goal / food_macros_obj.cals_per_gram; 
        food_macros_obj['cal_bar_height_to_unit_scale']= d3
            .scaleLinear()
            .domain([0,food_macros_obj.cal_bar_height])
            .range([0,food_g_in_goal_cals]);
    };

    const create_food_macro_containers = function(food_macros_obj) {
        const food_id = food_macros_obj.id;
        let food_div = `<div id='food-${food_id}-container' class='food-container'>`;
        let food_name = food_macros_obj.name;
        if (food_name.length > 20) {
            food_name = food_name.slice(0,20) + '...';
        }
        food_div += `<div class='food-container-header'>${food_name}</div>`;
        food_div += `<div id='food-${food_id}-bars' class='food-container-bars'></div>`;
        food_div += `<div id='food-container-footer-${food_id}' class='food-container-footer'>`;


        food_div += `<span id='food-amt-${food_id}' class='food-amt'></span>`;
        food_div += `<span id='food-amt-unit-${food_id}' class='food-amt-unit'>g</span>`;
            
        food_div += "</div>";
        food_div += '</div>'; 
            
        $('#meal-maker-food-content').append(food_div);

        d3.select(`#food-amt-${food_id}`)
            .data([{'food_amt':food_macros_obj.food_amt}])
            .text(function(d) { return d.food_amt; });
    };

    const assign_food_macros_obj_bar_attrs = function(svg_id ,macro, food_macros_obj) {

        const svg_element = $(`#${svg_id}`);

        food_macros_obj.svg_height = svg_element.height();
        food_macros_obj.svg_width = svg_element.width();
        food_macros_obj.cal_bar_height = food_macros_obj.svg_height * .9;
        food_macros_obj.bar_width = food_macros_obj.svg_width * .5;
        food_macros_obj.bar_margin_left = (food_macros_obj.svg_width - food_macros_obj.bar_width) / 2;
        food_macros_obj.slider_height = food_macros_obj.svg_height - food_macros_obj.cal_bar_height;  
        food_macros_obj.slider_width = food_macros_obj.svg_width * .8;  
        food_macros_obj.slider_margin_left = (food_macros_obj.svg_width - food_macros_obj.slider_width) / 2;

    };

    const draw_food_bar = function(macro, svg, food_macros_obj) {

        food_macros_obj[macro].macro_to_cal_ratio = food_macros_obj[`${macro}_per_gram`] / food_macros_obj['cals_per_gram'];

        food_macros_obj[macro].food_bar_height = food_macros_obj.cal_bar_height * food_macros_obj[macro].macro_to_cal_ratio; 
        food_macros_obj[macro].food_y = food_macros_obj.svg_height - food_macros_obj[macro].food_bar_height - food_macros_obj.slider_height;

        svg.selectAll('.rects')
            .data([food_macros_obj[macro]])
            .enter()
            .append('rect')
            .attr('height', function(d) { 
                return d.food_bar_height; 
            })

            .attr('width', food_macros_obj.bar_width)
            .attr('x', food_macros_obj.bar_margin_left)
            .attr('y', function(d) { 
                return d.food_y;
            })
            .attr('fill', function(d) { 
                return d3.schemeCategory10[d.food_order % d.color_count];
            })
            .attr('id', `${macro}-food-macro-bar`)
            .attr('class', 'food-macro-bar');
    };

    const draw_slider_bar = function(macro, svg, food_macros_obj) {
        
        svg.selectAll('.slider')
            .data([food_macros_obj]).enter()
            .append('rect')
            .attr('height', function(d) { return d.slider_height; })
            .attr('width', function(d) { return d.slider_width; })
            .attr('x', function(d) { return d.slider_margin_left; })
            .attr('y', function(d) { return d.cal_bar_height; })
            .attr('fill','green')
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', function(d) {
                    const y_delta = dragged(d,this);
                    update_food_amt_label(y_delta, d);
                    move_these_macro_bars(y_delta, d);
                    move_other_macro_bars(y_delta, d);
                })
                .on('end', dragended));
    };

    const create_food_goal_macros_bars = function(macro, food_macros_obj) {
    
        const svg = d3.select(`#${macro}-bar-svg`);
        const svg_element = $(`#${macro}-bar-svg`);

        food_macros_obj[macro].food_goal_y = svg_element.height();
        food_macros_obj[macro].food_goal_bar_height = 0;

        svg.selectAll('.rects')
            .data([food_macros_obj[macro]])
            .enter()
            .append('rect')
            .attr('height', function(d) { return d.food_goal_bar_height; })
            .attr('width', svg_element.width())
            .attr('x', 0)
            .attr('y', function(d) { return d.food_goal_y; })
            .attr('fill', function(d) {
                return d3.schemeCategory10[d.food_order % d.color_count];
             })
            .attr('id', `${macro}-${food_macros_obj.id}-goal-macro-bar`)
            .attr('class', 
                    `food-${food_macros_obj.id}-goal-macro-bar ${macro}-goal-macro-bar`)
    };
    
    const update_food_amt_label = function(y_delta, food_macros_obj) {
        // food_amt is negative y_delat due to nature of
        // d3 y values
        const food_amt_delta = -1*food_macros_obj['cal_bar_height_to_unit_scale'](y_delta);

        d3.select(`#food-amt-${food_macros_obj.id}`)
            .text(function(d) {
                d.food_amt += food_amt_delta;
                return Math.round(d.food_amt);
            });

    };

    const move_these_macro_bars = function(y_delta, food_macros_obj) {
        
        const cal_goal_y_delta = food_macros_obj.cal_to_goal_cal_height_scale(y_delta);

        MACRO_NAMES.forEach(function(macro) {
            const bar_id = `#${macro}-${food_macros_obj.id}-goal-macro-bar`; 
            d3.select(bar_id).attr('y', function(d) {

                d.food_goal_y += (cal_goal_y_delta * food_macros_obj[macro].macro_to_cal_ratio);
                return d.food_goal_y;
            });
            d3.select(bar_id).attr('height', function(d) {
                d.food_goal_bar_height -= (cal_goal_y_delta * food_macros_obj[macro].macro_to_cal_ratio);
                if (d.food_goal_bar_height < 0) {
                    d.food_goal_bar_height = 0;
                }
                return d.food_goal_bar_height;
            });
        });
    };

    const move_other_macro_bars = function(y_delta, food_macros_obj) {
        
        const cal_goal_y_delta = food_macros_obj.cal_to_goal_cal_height_scale(y_delta);

        MACRO_NAMES.forEach(function(macro) {
            const bar_class = `.${macro}-goal-macro-bar`; 
            d3.selectAll(bar_class).attr('y', function(d) {
                if (d.food_id != food_macros_obj.id & d.food_order < food_macros_obj.food_order) {
                    d.food_goal_y += (cal_goal_y_delta * food_macros_obj[macro].macro_to_cal_ratio);
                    return d.food_goal_y;
                }
                return d.food_goal_y;
            });
        });
    };


    const dragstarted = function() {
        d3.select(this).raise().classed('slider-active', true);
    };

    const dragged = function(d,this_) {
        const old_y = d3.select(this_).attr('y');
 
        d3.select(this_).attr('y', function() {
            const y = d3.event.y;
            if (y < 0) {
                return 0;
            } else if (y > d.cal_bar_height) {
                return d.cal_bar_height;
            } else {
                return y;
            }
        });
        const new_y = d3.select(this_).attr('y');
        const y_delta = new_y - old_y;
        return y_delta;
    };

    const dragended = function() {
        d3.select(this).raise().classed('slider-active', false);
    };

    const create_food_macro_svg = function(svg_id, macro, food_macros_obj) {

        const svg_html = `<svg id='${svg_id}' class='food-${food_macros_obj.id}-svg food-macro-svg' style='height:100%;width:20%'></svg>`;

        $(`#food-${food_macros_obj.id}-bars`).append(svg_html);

    };


	//macro breakdown functions 
	return {
		CAL_GOAL: 0,//initialize value
		CAL_BAR_HEIGHT: 0,//initialize value
		SEARCH_RESULT_ADD_BUTTON_LISTENER_EXISTS: 0,
        FOOD_COUNT: 0, add_food : function() {
			mm_funk_obj = this;
			$('.search-result>button').on('click',function() {
                mm_funk_obj.FOOD_COUNT += 1;
				const food_macros_obj = create_food_macros_obj(this,mm_funk_obj);
                create_food_macro_containers(food_macros_obj);
                MACRO_NAMES.forEach(function(macro) {
                    const svg_id = `food-${food_macros_obj.id}-${macro}-svg`;

                    create_food_macro_svg(svg_id, macro, food_macros_obj);
                    assign_food_macros_obj_bar_attrs(svg_id, macro, food_macros_obj);
                    
                    let svg = d3.select(`#${svg_id}`);
                    //id format ingrdient-id-macro-svg
                    draw_food_bar(macro, svg, food_macros_obj);
                    if (macro == 'cals') {
                        add_scales_to_food_macros_obj(food_macros_obj)
                        draw_slider_bar(macro, svg, food_macros_obj);
                    }
                    create_food_goal_macros_bars(macro, food_macros_obj);
                    //create_food_labels(food_macros_obj);
                });
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
                $('#goal-macros-bar-container').html('');//clear bar area
				let macro_bars_obj = create_macro_bars_obj();
                MACRO_NAMES.forEach(function(macro) {
                    create_macro_bar_container(macro);
                    create_macro_bar(macro, macro_bars_obj);
                    //create_macro_error_bars();
                    create_macro_bar_labels(macro, macro_bars_obj);
                });
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
