var MGOAL = (function() { 
    
    const MACRO_FACTORS = {
            'cals':1,
            'fat':9,
            'carbs':4,
            'protein':4
    };
    const MACRO_NAMES = ['cals', 'fat', 'carbs', 'protein'];

    const OPPOSITES = {'percent' :'g', 'g':'percent'};
	//macro breakdown functions 
	return {
		CAL_GOAL: 0,//initialize value
		CAL_BAR_HEIGHT: 0,//initialize value
		SEARCH_RESULT_ADD_BUTTON_LISTENER_EXISTS: 0,
        FOOD_COUNT: 0, 
    

        //tested
        enable_disable_create_macro_bars_button : function({goal_cals,percent_total}) {
            if (goal_cals > 0 && percent_total == 0) {
                return false;
            } else {
                return true;
            }
        },

        //tested
        get_goal_meal_grams : function(macros_obj) { 
            const cals = macros_obj['cals'];
            MACRO_NAMES.slice(1,).forEach(function(macro) {
                const percent = macros_obj[macro];
                const macro_factor = MACRO_FACTORS[macro];
                let grams = Math.round(percent / 100 * cals / macro_factor);
                
                if (isNaN(grams) == false) {
                    macros_obj[`${macro}-g`] = grams;
                } else {
                    macros_obj[`${macro}-g`] = '';
                }
            });
            return macros_obj;
        },

        //tested
        set_mgoal_goal_cals : function(obj,cals) {

            console.log('cals',cals);
            if (isNaN(cals) == false) {
                obj.CAL_GOAL = parseFloat(cals);
            } else { 
                obj.CAL_GOAL = 0;
            }	
        },

        //event - test in Function Tests
		goal_meal_choose_macro_handler : function() {
			mgoal_obj = this;
			$('.choose-macros').on('keyup',function(e) {	
                if (e.which != 9) {

                    // initialize vars unsed in below funcs
                    const input_array = this.id.split('-');
                    const macro = input_array[2];
                    const type = input_array[3];
                    const handler_obj = {
                        'cals': mgoal_obj.CAL_GOAL,
                        'macro_value': parseFloat(this.value),
                        'macro': macro,
                        'type': type,
                        'opposite_type': OPPOSITES[type],
                        'macro_factor':MACRO_FACTORS[macro]
                    };

                    // convert between g and pct
                    if (isNaN(handler_obj['cals']) == false) {
                        let return_id = `#goal-meal-${macro}-${handler_obj['opposite_type']}`;
                        if (isNaN(handler_obj['macro_value'])) {
                            $(return_id).val('');
                        } else {
                            converted_val = mgoal_obj.convert_macro_pct_grams(handler_obj);
                            $(return_id).val(converted_val);
                        }
                    }

                    // adjust total
                    const percent_id = `#goal-meal-${macro}-percent`;
                    totaler_obj = mgoal_obj.goal_meal_macro_percent_totaler({
                        'percent_id': percent_id
                    });
                    $('#goal-meal-macro-percent-total').html(totaler_obj['new_percent_total']);
                    $(percent_id).attr('data-value',totaler_obj['new_macro_percent']);
                    // change create macro button status
                    const is_disabled = mgoal_obj.enable_disable_create_macro_bars_button({
                        'goal_cals':mgoal_obj.CAL_GOAL,
                        'percent_total':totaler_obj['new_percent_total']
                    });
                    $('#create-macro-bars-button').attr('disabled',is_disabled);
                }
			});
		},

		create_macro_button_trigger : function() {
			mgoal_obj = this;
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
			mgoal_obj = this;
			$('.goal-cal-inputs').on('keyup change',function() {
                let macros_obj = {};
                $('.choose-macros-pct').each(function(i,e) {
                    const macro = e.id.split('-')[2];
                    macros_obj[macro] = parseFloat(e.value);
                });
                macros_obj['cals'] = parseFloat($.trim(this.value));
                
                mgoal_obj.set_mgoal_goal_cals(mgoal_obj,macros_obj['cals']);

                macros_obj = mgoal_obj.get_goal_meal_grams(macros_obj);
                
                MACRO_NAMES.forEach(function(macro) {
                    const id = `#goal-meal-${macro}-g`;
                    const grams = macros_obj[`${macro}-g`];
                    $(id).val(grams);
                });
                    
                const total_pct = parseFloat($('#goal-meal-macro-percent-total').html()); 
                const is_disabled = mgoal_obj.enable_disable_create_macro_bars_button({
                    'goal_cals': mgoal_obj.CAL_GOAL,
                    'percent_total': total_pct  
                });

                $('#create-macro-bars-button').attr('disabled',is_disabled);


                if ($(this).attr('id') == 'goal-meal-cals') {
                    $('#goal-meal-cals-select>option:eq(0)').prop('selected',true);
                } else {
                    $('#goal-meal-cals').val('');
                }
			});
		},

        //tested
        convert_macro_pct_grams : function({cals, macro, macro_value, macro_factor, type}) {
        
            if (!isNaN(cals)) {
                
                let converted_val;
                if (type == 'percent') {
                    converted_val = (cals * (macro_value / 100.0) / macro_factor).toFixed(0);
                } else {
                    converted_val = (macro_value * macro_factor / cals * 100).toFixed(0);	
                }
                
                return converted_val;

            }
            return NaN;
        },
        
        //tested
        goal_meal_macro_percent_totaler : function({percent_id}) {

            let new_macro_percent = parseFloat($(percent_id).val());
            if (isNaN(new_macro_percent)) {
                new_macro_percent = 0;
            } 

            const old_macro_percent = parseFloat($(percent_id).attr('data-value'));

            const percent_diff = new_macro_percent - old_macro_percent;
            const old_percent_total = parseFloat($('#goal-meal-macro-percent-total').html());
            const new_percent_total = old_percent_total - percent_diff;

            return {
                'new_percent_total': new_percent_total,
                'new_macro_percent': new_macro_percent
            };
        },

        //test in Function Tests
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
