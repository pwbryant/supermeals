const MY_MEALS_SEARCH = (function() {  
    
    return {
        my_meals_search_listener : function() { 

			THIS_OBJ = this;
			$('#my-meals-search-button').on('click',function() {
                const input_element = $(this).prev();
                const search_terms = $.trim($(input_element).val());
                if (search_terms != '') {
                    const meal_or_recipe = $(
                        '#my-meals-select'
                    ).find(':selected').val();
                    const destination_id = '#my-meals-search-results-container';
                    THIS_OBJ.my_meals_food_search(
                        THIS_OBJ, search_terms, meal_or_recipe, destination_id,
                        'my-meals', 'my-meals-meal'
                    );
                }
			});
        },

        easy_picks: function() {
            $('#my-meals-select').on('change', function() {
                const meal_or_recipe = $('#my-meals-select').find(':selected').val();
                const search_terms = '_all_';
                const destination_id = '#my-meals-easy-picks-meals-container'
                THIS_OBJ.my_meals_food_search(
                    THIS_OBJ, search_terms, meal_or_recipe, destination_id,
                    'easy-picks', 'easy-picks-meal'
                );
            });
        }, 
       
        my_meals_food_search: function(this_obj, search_terms, meal_or_recipe,  destination_id, meal_storage, result_class) {
			this_obj[meal_storage] = {};
            const search_data = {'search_terms': search_terms};
            $.get(`/meals/search-my-meals/${meal_or_recipe}/`, search_data, function(data) {
                const search_results = data['search-results'];

                search_results_html = SEARCH.format_food_search_results(
                    'my-meals',
                    search_results['meals'],
                    result_class
                );

                $(destination_id).html(search_results_html);
                search_results['meals'].map(function(r, i) {
                    const meal_info = search_results['meal_info'][r.id];
                    this_obj[meal_storage][r.id] = {
                        'ingredients': meal_info,
                        'macros_profile': r.macros_profile
                    }
                });

                const listen_selector = destination_id + ' button';
                this_obj.add_result_button_lister(listen_selector, meal_storage);
            });
        },

        add_result_button_lister: function(listen_selector, meal_storage) {
			const this_obj = this;
			$(listen_selector).on('click',function() {

                const my_meal_id = this.id.split('-')[5];
                const my_meal_info = this_obj[meal_storage][my_meal_id];

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
            const meal_id = my_meal_info['ingredients'][0]['id'];
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

            $('#my-meals-modal-body').html(ingredients_html);

            // acivate modal close when x icon clicked
            $('.close-modal').on('click', function() {
                $('.modal-body').html('');
                $('#my-meals-modal-header').html('');
                modal.style.display = 'none';
            });

            // activate delete button
            $('#my-meals-delete').on('click', function() {

                modal.style.display = 'none';

                let delete_modal = document.getElementById('my-meals-confirm-delete');
                delete_modal.style.display = 'block';

                let delete_form = document.getElementById('my-meals-delete-form');
                delete_form.innerHTML += `<input id='my-meals-delete-meal-id' type="hidden" name="meal_id" value=${meal_id} />`;

                $('#my-meals-ok-delete').on('click', function() {
                    const post_data = $('#my-meals-delete-form').serialize();
                    $.post('meals/my-meals-delete', post_data, function(data) {
                        let confirm_msg = document.getElementById(
                            'my-meals-delete-confirmation'
                        );
                        if (data['status'] == 1) {
                            
                            confirm_msg.innerHTML = 'Deletion Complete';
                            // display confirmation for a brief time
                            setTimeout(function() {
                                const meal_id_input = document.getElementById(
                                    'my-meals-delete-meal-id'
                                );
                                delete_form.removeChild(meal_id_input);

                                confirm_msg.innerHTML = '';
                                delete_modal.style.display = 'none';

                                // reload page so meals in side bar are updated
                                $('#my-meals-tab').click();
                            }, 2000);
                        } else {
                            confirm_msg.innerHTML = 'Deletion Failed. Contact Admin';
                            setTimeout(function() {
                                const meal_id_input = document.getElementById('my-meals-delete-meal-id');
                                delete_form.removeChild(meal_id_input);

                                confirm_msg.innerHTML = '';
                                delete_modal.style.display = 'none';
                            }, 2000);
                        }
                    });
                });

                $('#my-meals-cancel-delete').on('click', function() {
                    delete_modal.style.display = 'none';
                    modal.style.display = 'block';
                });
            });
        }
    }
})();
