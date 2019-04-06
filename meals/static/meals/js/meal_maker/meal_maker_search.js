// BARS AND SEARCH object need to already be loaded
let MEAL_MAKER_SEARCH = (function() { 

    return {
        SEARCH_RESULT_ADD_BUTTON_LISTENER_EXISTS : 0,

		meal_maker_search_listener: function() {
			THIS_OBJ = this;
			$('#meal-maker-search-button').on('click',function() {
                const input_element = $(this).prev();
                const search_terms = $.trim($(input_element).val());
                const search_data = SEARCH.get_food_search_info('meal-maker', search_terms);
				THIS_OBJ.meal_maker_food_search(THIS_OBJ, search_data);

			});
		},

        // tested in Functional Tests
        meal_maker_food_search : function(this_obj, search_data) { 

            $.get('/meals/search-foods/all/', search_data, function(data) {
                const search_results = data['search-results'];
                let search_results_html = '';
                if(search_results.length > 0) {
                    BARS.SEARCH_RESULTS = search_results; 
                    search_results_html = SEARCH.format_food_search_results('meal-maker', search_results);
                    $('#meal-maker-search-results-container').html(search_results_html);
                    BARS.add_food();
                    this_obj.SEARCH_RESULT_ADD_BUTTON_LISTENER_EXISTS = true;
                } else {
                    search_results_html = '<span>No Foods Found</span>';
                    $('#meal-maker-search-results-container').html(
                        search_results_html
                    ); 
                }
            });
        }
    }
})();
