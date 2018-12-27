let SAVE = (function() { 

    return {
        /**
        * get_meal_info gets meal name from modal, and food
        * amts/units from page and calcs macros per gram
        * and returns food_amts_obj
        */

        // tested in FT
        get_meal_info: function() {
            const meal_name = $('#macro-meal-name').val();
            const meal_notes = $('#macro-meal-notes').val();
            let food_amts_obj = {'name': meal_name, 'notes': meal_notes};
            let total_grams = 0;
            let total_cals = 0;
            let total_fat = 0;
            let total_carbs = 0;
            let total_protein = 0;
            d3.selectAll('.slider').data().forEach(function(obj, idx) {
                const food_amt = d3.select(
                    `#food-amt-${obj.id}`
                ).data()[0]['food_amt'];
                const unit = $(
                    `#food-amt-units-${obj.id} option:selected`
                ).text();
                
                food_amts_obj[`form-${idx}-ingredient_id`] = obj.id;
                food_amts_obj[`form-${idx}-amount`] = food_amt;
                food_amts_obj[`form-${idx}-unit`] = unit;

                // _0 scale is always associated with grams
                grams = obj.servings_scales.cal_bar_height_to_unit_scale_0(
                    obj.cal_bar_height - obj.slider_y
                );

                total_grams += grams

                total_cals += grams * obj.cals_per_gram;
                total_fat += grams * obj.fat_per_gram;
                total_carbs += grams * obj.carbs_per_gram;
                total_protein += grams * obj.protein_per_gram;
            });

            food_amts_obj['cals_per_gram'] = total_cals / total_grams;
            food_amts_obj['fat_per_gram'] = total_fat / total_grams;
            food_amts_obj['carbs_per_gram'] = total_carbs / total_grams;
            food_amts_obj['protein_per_gram'] = total_protein / total_grams;
            food_amts_obj['total_grams'] = total_grams;

            console.log('food amts obj', food_amts_obj);
            return food_amts_obj;
        },

        clear_meal_maker_tab: function() {
            console.log('clear meal maker tab funk');
            $('#goal-meal-cals').val('');
            $('#goal-meal-fat-g').val('');
            $('#goal-meal-carbs-g').val('');
            $('#goal-meal-protein-g').val('');
            $('#meal-maker-search').val('');
            $('#meal-maker-search').val('');
            $('#meal-maker-search-results-container').html('');
            $('#meal-maker-food-search-container').addClass('hide');
            $('#goal-macros-bar-content').html('');
            $('#goal-macros-bar-footer').html('');
            $('#meal-maker-food-content').html('');
        },
        /**
        * save_meal posts meal data to server to save as
        * meal
        */
        // tested in FT
        save_meal: function(meal_info_obj) {
            save_obj = this;
            const csrf_token = $(
                '#save-meal-form input[name="csrfmiddlewaretoken"]'
            ).val();
            meal_info_obj['csrfmiddlewaretoken'] = csrf_token;

            $.post('/meals/save-macro-meal', meal_info_obj, function(data) {
                console.log('data', data);
                if (data.status == 1) {
                    console.log('success');
                    $('#macro-meal-save-status').text("Successfully Saved!");

                    setTimeout(function() {
                        let modal = document.getElementById('save-macro-meal-modal');
                        modal.style.display = 'none';
                    }, 3000);

                    save_obj.clear_meal_maker_tab();
                } else {
                    console.log('failed',data.errors);
                    let errors = JSON.parse(data.errors);
                    for (let key in errors) {
                        errors[key].forEach(function(error) {
                            $('#macro-meal-save-status').text(error);
                        });
                    };
                }
            });
        },

        /**
        * save_meal_button_listener listens to the 'Save Meal'
        * button on the save macro-meal modal and triggers
        * the make_meal_info and save_meal functions
        */
        // tested in FT
        save_meal_button_listener: function() {
            save_obj = this;
            $('#save-macro-meal-button').on('click', function() {
                
                const meal_info_obj = save_obj.get_meal_info();
                save_obj.save_meal(meal_info_obj);
            });
        }
    };

})();
