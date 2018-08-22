let SAVE = (function() { 

    return {
        /**
        * get_meal_info gets meal name from modal, and food
        * amts/units from page and returns food_amts_obj
        */

        get_meal_info: function() {
            const food_amts = d3.selectAll('.food-amt').data();
            const meal_name = $('#macro-meal-name').val();
            food_amts.forEach(function(obj) {
                const food_id = obj['food-id'];
                const unit = $(`#food-amt-units-${food_id} option:selected`).text()
                obj['unit'] = unit;
            });
            const food_amts_obj = {'food_amts': food_amts, 'meal_name': meal_name};
            return food_amts_obj;
        },

        /**
        * save_meal posts meal data to server to save as
        * meal
        */
        // tested in FT
        save_meal: function({food_amts, meal_name}) {
            
            const csrf_token = $(
                '#meal-save-form input[name="csrfmiddlewaretoken"]'
            ).val();
            const post_data = {
                'food_amts': food_amts,
                'meal_name': meal_name,
                'csrfmiddlewaretoken': csrf_token
            };

            $.post('/meals/save-macro-meal', post_data, function(data) {
            // $.post('/meals/save-my-macros', post_data, function(data) {
                console.log(data);
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
