
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

        add_recipe_search_result_listener: function() {
            this_obj = this;
            $('.add-recipe-search-result__button').on('click', function() {

                const food_index = parseFloat(this.value);
                const food_obj = this_obj.SEARCH_RESULTS[food_index];
                const food_id = food_obj['id'];
                const food_name = food_obj['name'];

                const ingredient_html = `<p id='add-recipe-ingredient-${food_id}'>${food_name}</p>`;
                $('#add-recipe-ingredients-container').append(ingredient_html);
            });

        }
    }
})();
