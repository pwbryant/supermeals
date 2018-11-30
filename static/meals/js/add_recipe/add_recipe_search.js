
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
                    search_results_html = SEARCH.format_food_search_results(
                        'add-recipe',
                        search_results
                    );
                    $(`#${tab_name}-search-results-container`).html(search_results_html);
                } else {
                    search_results_html = '<span>No Foods Found</span>';
                    $(`#${tab_name}-search-results-container`).html(
                        search_results_html
                    ); 
                }
            });
        }
    }
})();
