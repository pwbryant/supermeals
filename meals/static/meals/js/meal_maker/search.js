let SEARCH = (function() { 

    return {
        SEARCH_RESULT_ADD_BUTTON_LISTENER_EXISTS : 0,
        BARS_OBJ: BARS,// bars.js nees to alread be loaded

        // tested in Functional Tests
		meal_maker_food_search_trigger: function() {
			search_obj = this;
			$('#food-search-icon-button').on('click',function() {
				search_obj.meal_maker_food_search(search_obj);
			});
		},

        // tested in Functional Tests
        meal_maker_food_search : function(search_obj) { 
            const search_terms = $.trim($('#meal-maker-food-search-input').val());
            if(search_terms != '') {
                $.get('/meals/search-foods/',{'search_terms':search_terms},function(data) {
                    const search_results = data['search-results'];
                    let search_results_html = '';
                    if(search_results.length > 0) {
                        search_obj.BARS_OBJ.SEARCH_RESULTS = search_results; 
                        search_results_html = search_obj.format_food_search_results(search_results);
                        $('#meal-maker-food-search-results-container').html(search_results_html);
                        search_obj.BARS_OBJ.add_food();
                        search_obj.SEARCH_RESULT_ADD_BUTTON_LISTENER_EXISTS = true;
                    } else {
                        search_results_html = '<span>No Foods Found</span>';
                        $('#meal-maker-food-search-results-container').html(search_results_html);
                    }
                });
            } else {
                $('#meal-maker-food-search-input').val('');
                $('#meal-maker-food-search-results-container').html('');
            }
        },

        format_food_search_results : function(search_results) {

            var search_results_html = '';	
            search_results.forEach(function(e,i) {
                search_results_html += "<div class='search-result'><span>" + e.name + "</span><button id='search-result-food-" + i + "' class='icon'><i class='fa fa-plus'></i></button></div>"; 
            });
            return search_results_html;
        }
    }
})();
