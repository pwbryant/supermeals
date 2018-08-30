let SAVE = (function() { 

    return {
        /**
        * get_meal_info gets meal name from modal, and food
        * amts/units from page and returns food_amts_obj
        */

        // tested in FT
        get_meal_info: function() {
            const meal_name = $('#macro-meal-name').val();
            let food_amts_obj = {'meal_name': meal_name};
            d3.selectAll('.slider').data().forEach(function(obj, idx) {
                const food_amt = d3.select(
                    `#food-amt-${obj.id}`
                ).data()[0]['food_amt'];
                const unit = $(
                    `#food-amt-units-${obj.id} option:selected`
                ).text();
                food_amts_obj[`ingredients_id_${idx}`] = obj.id;
                food_amts_obj[`ingredients_amt_${idx}`] = food_amt;
                food_amts_obj[`ingredients_unit_${idx}`] = unit;
            });
            console.log('food_amts_obj', food_amts_obj)
            return food_amts_obj;
        },

        /**
        * save_meal posts meal data to server to save as
        * meal
        */
        // tested in FT
        save_meal: function(meal_info_obj) {
            
            const csrf_token = $(
                '#save-meal-form input[name="csrfmiddlewaretoken"]'
            ).val();
            meal_info_obj['csrfmiddlewaretoken'] = csrf_token;

            $.post('/meals/save-macro-meal', meal_info_obj, function(data) {
                console.log('data', data);
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
