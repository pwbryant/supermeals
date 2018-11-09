const MY_MEAL_SEARCH = (function() { 
    
    return {
        my_meals_food_search_listener : function() { 

			search_obj = this;
            $('#my-meals-search-button').on('click', function() {
                const search_terms = $.trim($('#my-meals-search-input').val());
                if(search_terms != '') {

                    $.get('/meals/search-foods/',{'search_terms':search_terms},function(data) {
                        const search_results = data['search-results'];
                        search_results_html = search_obj.format_food_search_results(search_results);
                        $('#my-meals-search-results-container').html(search_results_html);
                    });
                }
            });
        },

        format_food_search_results : function(search_results) {

            let search_results_html = '';	
            search_results.forEach(function(e,i) {
                search_results_html += "<div class='search-result'><span>" + e.name + "</span><button id='search-result-food-" + i + "' class='icon'><i class='fa fa-plus'></i></button></div>"; 
            });
            return search_results_html;
        }
    }
})();
