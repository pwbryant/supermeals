var BARS = (function() { 
    
	const MACRO_FACTORS = {
		'cals':1,
		'fat':9,
		'carbs':4,
		'protein':4
	};
    
    const MACRO_NAMES = ['cals', 'fat', 'carbs', 'protein'];

	return {
        MGOAL : MGOAL,// set_macro_goals.js needs to be loaded
        FOOD_COUNT: 0,
        // I must have copy pasted this because I'm not sure what the fuck
        // this is all about
        enable_save_meal_button: function() {
            const target_node = document.getElementById('cals-amt');
            const config = { attributes: true, childList: true, subtree: true };
            const callback = function(mutations) {

                if (Math.round(mutations[0].target.__data__.macro_amt) > 0) {
                    document.getElementById('show-modal-button').disabled = false;
                } else {
                    document.getElementById('show-modal-button').disabled = true;
                }
            }
            let observer = new MutationObserver(callback);
            observer.observe(target_node, config);
        },

        create_save_macro_meal_modal: function() {

			// let bars_obj = this;

            let modal = document.getElementById('save-macro-meal-modal');

            $('#show-modal-button').on('click', function() {
                modal.style.display = 'block';
            });

            let modal_inputs = 'input[id="macro-meal-name"]';
            modal_inputs += ',textarea';
            modal_inputs += ',div[id="macro-meal-save-status"]';
            $('.close-modal').on('click', function() {
                $(modal).find(modal_inputs).val('').text('').end();
                modal.style.display = 'none';
            });

        },

        add_food : function() {
			bars_obj = this;
			$('.meal-maker-search-result__button').on('click',function() {

                // hide the food banner
                $('#meal-maker-food-content-banner').addClass('hide');

                bars_obj.FOOD_COUNT += 1;

                // create food macros obj
				const food_macros_obj = bars_obj.create_food_macros_obj({
                    'search_button_id': this.id,
                    'bars_obj': bars_obj,
                    'result_index': parseFloat(this.value)
                });

                //create food container
                const food_div = bars_obj.create_food_macro_containers(food_macros_obj);
                $('#meal-maker-food-content').append(food_div);
                d3.select(`#food-amt-${food_macros_obj.id}`)
                    .data([{'food-id':food_macros_obj.id, 'food_amt':food_macros_obj.food_amt}])
                    .text(function(d) { return d.food_amt; });
                
                //set up remove food listener
                bars_obj.remove_food({
                    'food_macros_obj': food_macros_obj,
                    'bars_obj': bars_obj
                });

                MACRO_NAMES.forEach(function(macro) {
                    const svg_id = `food-${food_macros_obj.id}-${macro}-svg`;

                    // draw food svg
                    const svg_html = bars_obj.create_food_macro_svg({
                        'svg_id': svg_id,
                        'macro': macro,
                        'food_macros_obj': food_macros_obj
                    });
                    $(`#food-${food_macros_obj.id}-bars`).append(svg_html);
                    bars_obj.assign_food_macros_obj_bar_attrs(svg_id, macro, food_macros_obj);
                    
                    let svg = d3.select(`#${svg_id}`);
                    //id format ingrdient-id-macro-svg
                    bars_obj.draw_food_bar(macro, svg, food_macros_obj);

                    if (macro == 'cals') {

                        food_macros_obj.goal_cal_bar_height = $('#cals-bar-svg').height();
                        bars_obj.add_scales_to_food_macros_obj(food_macros_obj);
                        bars_obj.change_unit_scales_trigger();
                        
                        bars_obj.draw_slider_bar({
                            'bars_obj': bars_obj, 
                            'macro': macro, 
                            'svg': svg, 
                            'food_macros_obj': food_macros_obj});
                    }
                    bars_obj.create_food_goal_macros_bars(macro, food_macros_obj);
                    //create_food_labels(food_macros_obj);
                });
			});
		},

		create_macro_button_trigger : function() {
			bars_obj = this;
			$('#create-macro-bars-button').on('click',function() {


                // show search area and food bar banner
                $('#meal-maker-food-search-container').removeClass('hide');
                $('#meal-maker-food-content-banner').removeClass('hide');

                // set macro amts
                let macro_amts_obj = {};
                $('.choose-macros-pct').each(function(i,e) {
                    let macro = e.id.split('-')[2];
                    macro_amts_obj[macro] = parseFloat(e.value);
                });
                bars_obj.MACRO_AMTS = macro_amts_obj

                //clear bar area
                $('#goal-macros-bar-content').html('');
				let macro_bars_obj = bars_obj.create_macro_bars_obj({
                    'cal_bar_height': $('#goal-macros-bar-content').height() * .9,
                    'macro_amts_obj': macro_amts_obj 
                });
                MACRO_NAMES.forEach(function(macro) {
                    
                    let container_html = bars_obj.create_macro_bar_container(macro);
                    $('#goal-macros-bar-content').append(container_html);

                    bars_obj.create_macro_bar(macro, macro_bars_obj);
                    //create_macro_error_bars();
                    bars_obj.create_macro_bar_labels(macro, macro_bars_obj);
                });


                
                // add save macro meal button if user not guest
                $('#goal-macros-bar-footer').html('');//clear save button
                const is_guest = $('#is-guest').val();
                if (is_guest === 'false') {
                    const show_modal_button = (
                        '<button id="show-modal-button" \
                        class="btn" disabled>Save Meal</button>'
                    )
                    $('#goal-macros-bar-footer').append(show_modal_button);
                    // change in cals enables meal save button
                    bars_obj.enable_save_meal_button();
                    bars_obj.create_save_macro_meal_modal();
                } else {

                    const show_modal_button = (
                        '<button id="show-modal-button" \
                        class="btn disabled">Save Meal</button>'
                    )
                    $('#goal-macros-bar-footer').append(show_modal_button);
                }
			});
		},

        // tested
        create_macro_bars_obj : function({cal_bar_height,macro_amts_obj}) {
            let macros_bar_obj = {};
            macros_bar_obj.cal_bar_height = cal_bar_height;
            MACRO_NAMES.forEach(function(macro) {
                macros_bar_obj[macro] = {'name':macro};
                if (macro === 'cals') {
                    macros_bar_obj[macro]['ratio'] = 1;
                } else {
                    macros_bar_obj[macro]['ratio'] = macro_amts_obj[macro]/100.0
                }
            });
            return macros_bar_obj;
        },

        // tested
        create_macro_bar_container : function(macro) {

            macro_div = `<div id='${macro}-bar-container' class='macro-bar-container'>`;

            macro_div += `<svg id='${macro}-bar-svg' class='macro-bar-svg' style='height:90%;width:100%'></svg>`;

            macro_div += `<div id='${macro}-label-container' class='macro-label-container'></div>`

            macro_div += '</div>';
                
            return macro_div;
        },

        // tested in Functional Tests
        create_macro_bar : function(macro, macro_bars_obj) {

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
        },

        // tested in Functional Tests
        create_macro_error_bars : function(obj) {
            
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
        
        // tested in Functional Tests
        create_macro_bar_labels : function(macro, macro_bars_obj) {

            const macro_title = macro[0].toUpperCase() + macro.slice(1,);
            const label = `<span class='macro-label'>${macro_title}: </span>`;
            const amt = `<span id='${macro}-amt' class='macro-amt'></span>`;
if (macro != 'cals') {
                const unit = `<span class='macro-unit'>g</span>`;
                $(`#${macro}-label-container`).html(label + amt + unit);
            } else {
                $(`#${macro}-label-container`).html(label + amt);
            }

            d3.select(`#${macro}-amt`)
                .data([{'macro_amt': 0, 'name': macro}])
                .text(function(d) { return d.macro_amt; });
        },
        
        // tested
        create_food_macros_obj : function({search_button_id, bars_obj, result_index}) { 
            // const search_result_index = parseFloat(search_button_id.split('-')[3]);
            const food_macros_obj = bars_obj.SEARCH_RESULTS[result_index];
            food_macros_obj.food_order = bars_obj.FOOD_COUNT;
            food_macros_obj.cal_goal = bars_obj.MGOAL.CAL_GOAL;
            food_macros_obj.food_amt = 0;
            MACRO_NAMES.forEach(function(macro) {
                food_macros_obj[macro] = {};
                food_macros_obj[macro].name = macro;
                food_macros_obj[macro].food_id = food_macros_obj.id;
                const macro_per_gram = `${macro}_per_gram`;
                food_macros_obj[macro][macro_per_gram] = food_macros_obj[macro_per_gram];
                food_macros_obj[macro].food_order = bars_obj.FOOD_COUNT;
                food_macros_obj[macro].color_count = 10;
                if (macro === 'cals') {
                    food_macros_obj[macro]['goal_ratio'] = 1;
                } else {
                    food_macros_obj[macro]['goal_ratio'] = bars_obj.MACRO_AMTS[macro]/100.0
                }

            });
            return food_macros_obj;
        },
        
        // tested
        add_scales_to_food_macros_obj : function(food_macros_obj) {

            food_macros_obj['cal_to_goal_cal_height_scale']= d3
                .scaleLinear()
                .domain([0,food_macros_obj.cal_bar_height])
                .range([0,food_macros_obj.goal_cal_bar_height]);

            const food_g_in_goal_cals = food_macros_obj.cal_goal / food_macros_obj.cals_per_gram; 
            food_macros_obj['servings_scales'] = {}
            food_macros_obj['servings_scales']['cal_bar_height_to_unit_scale_0'] = d3
                .scaleLinear()
                .domain([0,food_macros_obj.cal_bar_height])
                .range([0,food_g_in_goal_cals]);

            food_macros_obj['servings'].forEach(function(servings_obj, i) {
                const servings_g = parseFloat(servings_obj['servings__grams']);
                const quantity = parseFloat(servings_obj['servings__quantity']);
                const servings_in_food_g = food_g_in_goal_cals / (servings_g / quantity);
                food_macros_obj['servings_scales'][`cal_bar_height_to_unit_scale_${i+1}`] = d3
                    .scaleLinear()
                    .domain([0,food_macros_obj.cal_bar_height])
                    .range([0,servings_in_food_g]);
                 

            });

            food_macros_obj['cal_bar_height_to_unit_scale']= food_macros_obj['servings_scales']['cal_bar_height_to_unit_scale_0'];

            food_macros_obj['food_cal_bar_height_to_goal_cal_scale']= d3
                .scaleLinear()
                .domain([0,food_macros_obj.cal_bar_height])
                .range([0,food_macros_obj.cal_goal]);

        },
        
        // tested in FT
        change_unit_scales_trigger: function() {
            $('.food-amt-units').on('change', function() {
                const food_id = this.id.split('-')[3];
                const food_amt_id = `#food-amt-${food_id}`;
                const food_slider_id = `#food-${food_id}-slider`;
                const unit_value = this.value;
                const slider = d3.select(`${food_slider_id}`);
                const food_macros_obj = slider.data()[0];
                const slider_height = food_macros_obj.cal_bar_height - slider.attr('y');
                const new_scale = food_macros_obj['servings_scales'][`cal_bar_height_to_unit_scale_${unit_value}`];
                food_macros_obj['cal_bar_height_to_unit_scale'] = new_scale;
                
                d3.select(food_amt_id)
                    .text(function(d) {
                        d.food_amt = new_scale(slider_height);
                        // round to 2 decimal places
                        return Math.round(d.food_amt * 100) / 100;
                    });
                
            });
        },
            
        
        // tested
        create_food_macro_containers : function(food_macros_obj) {
            const food_id = food_macros_obj.id;
            let food_div = `<div id='food-${food_id}-container' class='food-container'>`;
            let food_name = food_macros_obj.name;
            if (food_name.length > 20) {
                food_name = food_name.slice(0,20) + '...';
            }
            food_div += `<div class='food-container-header l-flex--row-btw'>
                <span>${food_name}</span><i id='exit-${food_id}' class='fa fa-times-circle food-exit'></i>
            </div>`;
            food_div += `<div id='food-${food_id}-bars' class='food-container-bars'></div>`;
            food_div += `<div id='food-container-footer-${food_id}' class='food-container-footer bm-margin--md-top'>`;


            food_div += `<span id='food-amt-${food_id}' class='food-amt'></span>`;
            food_div += `<select id='food-amt-units-${food_id}' class='food-amt-units'>`;
            food_div += `<option value='0'>g</option>`;
            food_macros_obj['servings'].forEach(function(obj, i) {
                food_div += `<option value='${i+1}'>${obj.servings__description}</option>`;
            });
            food_div += '</select>';
                
            food_div += "</div>";
            food_div += '</div>'; 
                
            return food_div;
        },

        // event tested in Functional Tests
        remove_food : function({food_macros_obj, bars_obj}) {
            const icon_id = `#exit-${food_macros_obj.id}`;
            $(icon_id).on('click', function() {
                const food_id = food_macros_obj.id;
                const container_id = `#food-${food_id}-container`;
                const y_delta = -1 * (food_macros_obj.slider_y - food_macros_obj.cal_bar_height);// has to be negated to move in the right direction
                //remove food container
                $(container_id).remove();
                
                bars_obj.remove_food_macro_bars(food_macros_obj);
                bars_obj.adjust_remaining_macro_bars(food_macros_obj);
                bars_obj.update_macro_amt_labels(y_delta,food_macros_obj);
            });
        },

        // tested in Functional Tests
        remove_food_macro_bars : function(food_macros_obj) {
            
            const food_id = food_macros_obj.id;
            const food_class = `.food-${food_id}-goal-macro-bar`;
            const macro_heights = $(food_class).toArray().reduce(function(map, e) {
                const element = $(e);
                const height = parseFloat(element.attr('height'));
                const macro = element.attr('id').split('-')[0];
                map[macro] = height;
                return map;
            }, {});

            $(food_class).remove();
            food_macros_obj.macro_heights = macro_heights;
        },

        // tested in Functional Tests
        adjust_remaining_macro_bars : function(food_macros_obj) {
            
            const macro_heights = food_macros_obj.macro_heights;
            const food_order = food_macros_obj.food_order;

            d3.selectAll('.goal-macro-bar').transition().attr('y', function(d) {
                if (d.food_order < food_order) {
                    d.food_goal_y += macro_heights[d.name];
                }
                return d.food_goal_y;
            });

        },

        // tested in Functional Tests
        assign_food_macros_obj_bar_attrs : function(svg_id ,macro, food_macros_obj) {

            const svg_element = $(`#${svg_id}`);

            food_macros_obj.svg_height = svg_element.height();
            food_macros_obj.svg_width = svg_element.width();
            food_macros_obj.cal_bar_height = food_macros_obj.svg_height * .9;
            food_macros_obj.bar_width = food_macros_obj.svg_width * .5;
            food_macros_obj.bar_margin_left = (food_macros_obj.svg_width - food_macros_obj.bar_width) / 2;
            food_macros_obj.slider_height = food_macros_obj.svg_height - food_macros_obj.cal_bar_height;  
            food_macros_obj.slider_width = food_macros_obj.svg_width * .8;  
            food_macros_obj.slider_margin_left = (food_macros_obj.svg_width - food_macros_obj.slider_width) / 2;
            food_macros_obj.slider_y = food_macros_obj.cal_bar_height;

        },

        // tested in Functional Tests
        draw_food_bar : function(macro, svg, food_macros_obj) {

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
        },

        // tested in Functional Tests
        draw_slider_bar : function({bars_obj, macro, svg, food_macros_obj}) {
            food_macros_obj.slider_y = food_macros_obj.cal_bar_height;
            
            svg.selectAll('.slider')
                .data([food_macros_obj]).enter()
                .append('rect')
                .attr('height', function(d) { return d.slider_height; })
                .attr('width', function(d) { return d.slider_width; })
                .attr('x', function(d) { return d.slider_margin_left; })
                .attr('y', function(d) { return d.slider_y; })
                .attr('fill','green')
                .attr('id', function(d) { return `food-${d.id}-slider`; })
                .attr('class', 'slider')
                .call(d3.drag()
                    .on('start', bars_obj.dragstarted)
                    .on('drag', function(d) {
                        if (d.cal_bar_height != d.cal_bar_height_to_unit_scale.domain()[1]) {
                        }
                        const y_delta = bars_obj.dragged(d,this);
                        bars_obj.update_food_amt_label(y_delta, d);
                        bars_obj.move_these_macro_bars(y_delta, d);
                        bars_obj.move_other_macro_bars(y_delta, d);
                        bars_obj.update_macro_amt_labels(y_delta, d);
                    })
                    .on('end', bars_obj.dragended));
        },

        // tested in Functional Tests
        create_food_goal_macros_bars : function(macro, food_macros_obj) {
        
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
                        `food-${food_macros_obj.id}-goal-macro-bar ${macro}-goal-macro-bar goal-macro-bar`)
        },
        
        // tested in Functional Tests
        update_food_amt_label : function(y_delta, food_macros_obj) {
            // food_amt is negative y_delat due to nature of
            // d3 y values
            const food_amt_delta = -1 * food_macros_obj['cal_bar_height_to_unit_scale'](y_delta);

            d3.select(`#food-amt-${food_macros_obj.id}`)
                .text(function(d) {
                    d.food_amt += food_amt_delta;
                    return Math.round(d.food_amt * 100) / 100;
                });

        },

        // tested in Functional Tests
        move_these_macro_bars : function(y_delta, food_macros_obj) {
            
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
        },

        // tested in Functional Tests
        move_other_macro_bars : function(y_delta, food_macros_obj) {
            
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
        },

        // tested in Functional Tests
        update_macro_amt_labels : function(y_delta, food_macros_obj) {

            d3.selectAll('.macro-amt').text(function(d) {
                const macro_obj = food_macros_obj[d.name];
                const cal_change = -1 * food_macros_obj.food_cal_bar_height_to_goal_cal_scale(y_delta); // negate so direction is correct
                const macro_change = cal_change * macro_obj.macro_to_cal_ratio / MACRO_FACTORS[d.name];
                d.macro_amt += macro_change;
                return Math.round(d.macro_amt);
            });
        },

        // tested in Functional Tests
        dragstarted : function() {
            d3.select(this).raise().classed('slider-active', true);
        },

        // tested in Functional Tests
        dragged : function(d,this_) {
            const old_y = d3.select(this_).attr('y');
     
            d3.select(this_).attr('y', function() {
                const y = d3.event.y;
                if (y < 0) {
                    d.slider_y = 0;
                } else if (y > d.cal_bar_height) {
                    d.slider_y = d.cal_bar_height;
                } else {
                    d.slider_y = y;
                }
                return d.slider_y;
            });
            
            const new_y = d3.select(this_).attr('y');
            const y_delta = new_y - old_y;
            return y_delta;
        },

        // tested in Functional Tests
        dragended : function() {
            d3.select(this).raise().classed('slider-active', false);
        },

        // tested
        create_food_macro_svg : function({svg_id, macro, food_macros_obj}) {

            let svg_html = "<div class='food-macro-svg-container'>";
            svg_html += `<svg id='${svg_id}' class='food-${food_macros_obj.id}-svg food-macro-svg' style='height:100%;width:100%'></svg></div`;

            return svg_html;
        }
	};
})();
