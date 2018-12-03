
// SEARCH object need to already be loaded
let ADD_RECIPE_SEARCH = (function() { 

    return {

		add_recipe_search_listener: function() {
			THIS_OBJ = this;
			$('#add-recipe-search-button').on('click',function() {
                const input_element = $(this).prev();
                const search_terms = $.trim($(input_element).val());
                const tab_name = 'add-recipe';
                const search_data = SEARCH.get_food_search_info(tab_name, search_terms);
				THIS_OBJ.add_recipe_food_search(THIS_OBJ, tab_name, search_data);
			});
		},

        // tested in Functional Tests
        add_recipe_food_search : function(this_obj, tab_name, search_data) { 

            $.get('/meals/search-foods/all/', search_data, function(data) {
                const search_results = data['search-results'];
                let search_results_html = '';
                if(search_results.length > 0) {
                    // give results to this_obj for later use
                    this_obj.SEARCH_RESULTS = search_results;
                    search_results_html = SEARCH.format_food_search_results(
                        'add-recipe',
                        search_results
                    );
                    $(`#${tab_name}-search-results-container`).html(search_results_html);

                    // set result button listenr
                    this_obj.add_recipe_search_result_listener();
                } else {
                    search_results_html = '<span>No Foods Found</span>';
                    $(`#${tab_name}-search-results-container`).html(
                        search_results_html
                    ); 
                }
            });
        },

        create_ingredient_html: function(food_id, food_name, servings) {

                let ingredient_html = `<div id='add-recipe-ingredient-${food_id}-container' class="input l-flex--row-start add-recipe-ingredient">`;
                // food name
                ingredient_html += `<label id='add-recipe-ingredient-name-${food_id}' class='bm-margin--sm-right'>${food_name}</label>`;
                // Amount
                ingredient_html += `<div class='l-flex--col-start'><label for='add-recipe-ingredient-amt-${food_id}'>Amount</label><input id='add-recipe-ingredient-amt-${food_id}'type='text' name='ingredient' /></div>`;
                // Unit
                ingredient_html += `<div class='l-flex--col-start'><label for='add-recipe-ingredient-units-${food_id}'>Units</label><select id='add-recipe-ingredient-units-${food_id}' name='units-${food_id}'>`;

                // first unit is grams
                ingredient_html += '<option value="0">g</option>';
                servings.map(function(e, i) {
                    ingredient_html += `<option value='${i + 1}'>${e.servings__description}</option>`;
                });

                ingredient_html += `</select></div><i id='add-recipe-ingredient-exit-${food_id}' class='fa fa-times-circle add-recipe-ingredient-exit'></i>`;

                ingredient_html += `<div id='add-recipe-ingredient-amt-${food_id}-errors' class='form-errors'></div>`;

                return ingredient_html;
        },

        add_recipe_search_result_listener: function() {
            this_obj = this;
            $('.add-recipe-search-result__button').on('click', function() {

                const food_index = parseFloat(this.value);
                const food_obj = this_obj.SEARCH_RESULTS[food_index];
                const food_id = food_obj['id'];
                const food_name = food_obj['name'];

                const ingredient_html = this_obj.create_ingredient_html(
                    food_id, food_name, food_obj['servings']
                );

                $('#add-recipe-ingredients-container').append(ingredient_html);
                this_obj.add_ingredient_delete_listener();
            });

        },

        add_ingredient_delete_listener: function() {

            $('.add-recipe-ingredient-exit').on('click', function() {
                const ingredient_id = this.id.split('-')[4];
                const ingredient_container_id = `add-recipe-ingredient-${ingredient_id}-container`;
                $('#' + ingredient_container_id).remove();
            });
        }
    }
})();
