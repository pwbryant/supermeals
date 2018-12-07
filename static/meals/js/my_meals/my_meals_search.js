const MY_MEALS_SEARCH = (function() {  
    
    return {
        my_meals_search_listener : function() { 

			THIS_OBJ = this;
			$('#my-meals-search-button').on('click',function() {
                const input_element = $(this).prev();
                const search_terms = $.trim($(input_element).val());
                if (search_terms != '') {
                    THIS_OBJ.my_meals_food_search(THIS_OBJ, search_terms);
                }
			});
        },

        my_meals_food_search: function(this_obj, search_terms) {
			this_obj['my-meals'] = {};
            const search_data = {'search_terms': search_terms};
            const meal_or_recipe = $('#my-meals-select').find(':selected').val();
            $.get(`/meals/search-my-meals/${meal_or_recipe}/`, search_data, function(data) {
                const search_results = data['search-results'];
                search_results_html = SEARCH.format_food_search_results(
                        'my-meals',
                        search_results['meals']
                );

                $('#my-meals-search-results-container').html(search_results_html);
                search_results['meals'].map(function(r, i) {
                    const meal_info = search_results['meal_info'][r.id];
                    this_obj['my-meals'][r.id] = {
                        'ingredients': meal_info,
                        'macros_profile': r.macros_profile
                    }
                });

                this_obj.add_result_button_lister();
            });
        },

        add_result_button_lister: function() {
			const this_obj = this;
			$('#my-meals-search-results-container button').on('click',function() {

                const my_meal_id = this.id.split('-')[4];
                const my_meal_info = this_obj['my-meals'][my_meal_id];

                this_obj.add_result_button_shows_modal(my_meal_info);
            });
        },

        // need to test
        handle_nested_ingredients: function(this_obj, ingredient_info, ingredients_html, indent) {

            const ing_name = ingredient_info['main_food__ingredient__name'];
            const ing_id = ingredient_info['main_food__ingredient'];
            const srv_amount = parseFloat(ingredient_info['main_food__amount']);
            const srv_desc = ingredient_info['main_food__serving__description'];
            
            ingredients_html += '<div class="my-meals-ingredient">';
            ingredients_html += `${indent}${ing_name}: ${srv_amount} ${srv_desc}</div>`;

            if (ingredient_info.hasOwnProperty('meal_info')) {
                ingredients_html += 'Ingredients:'
                indent += '....';
                ingredient_info['meal_info'][ing_id].map(function(sub_ingredient_info) {
                    ingredients_html = this_obj.handle_nested_ingredients(
                        this_obj, sub_ingredient_info, ingredients_html, indent
                    );
                });
            }

            return ingredients_html;
        },

        add_result_button_shows_modal: function(my_meal_info) {

            const this_obj = this;
            let modal = document.getElementById('my-meal-modal');
            modal.style.display = 'block';
            
            // populate modal content
            // modal header
            const meal_name = my_meal_info['ingredients'][0]['name'];
            const notes = my_meal_info['ingredients'][0]['notes__notes'];
            const macros_profile = my_meal_info['macros_profile'];
            let macros_profile_summary = (
                '<div>Percentages may not add up to 100 due to rounding<br>' +
                `Cals: ~${Math.round(macros_profile['cals'])}`
            );
            ['fat', 'carbs', 'protein'].map(function(macro) {
                macros_profile_summary += (
                    ` ${macro}: ~${Math.round(macros_profile[macro])}g` +
                    ` (%${Math.round(macros_profile[macro + '_pct'])})`
                )
            });
            macros_profile_summary += '</div>';
            
            $('#my-meals-modal-header').text(meal_name);
            $('#my-meals-modal-sub-header').html(macros_profile_summary);

            // modal body
            let ingredients_html = '';
            my_meal_info['ingredients'].map(function(info) {
                indent = '';
                ingredients_html = this_obj.handle_nested_ingredients(
                    this_obj, info, ingredients_html, indent
                )
            });
            // notes
            if (notes) {
                ingredients_html += '<div id="my-meals-modal-notes">'
                ingredients_html += '<div id="my-meals-modal-notes-header">Notes:</div>';
                ingredients_html += `<div id='my-meals-modal-notes-body'>${notes}</div></div>`;
            }

            $('.modal-body').html(ingredients_html);

            // acivate modal close when x icon clicked
            $('.close-modal').on('click', function() {
                $('.modal-body').html('');
                $('#my-meals-modal-header').html('');
                modal.style.display = 'none';
            });
        }
    }
})();
