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
            const filters = $('input[name="filter"]:checked').map(function(i, filter) {
                return filter.value
            }).toArray();
            if(search_terms != '') {
                const get_data = {"search_terms": search_terms, "filters": filters}
                $.get('/meals/search-foods/all/', get_data, function(data) {
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

        format_food_search_results: function(search_results) {

            var search_results_html = '';	
            search_results.forEach(function(e,i) {
                search_results_html += "<div class='search-result l-flex--row-start'><button id='search-result-food-" + i + "' class='icon search-result__button bm-margin--sm-right'><i class='fa fa-plus'></i></button><div class='search-result__name'>" + e.name + "</div></div>"; 
            });
            return search_results_html;
        },

        // tested in FT
        filter_checkbox_behavior: function() {
            $('.filter, .non-filter').on('click', function() {
                if (this.checked == true && this.id != 'meal-maker-filter-none') {
                    $('#meal-maker-filter-none').prop('checked', false);
                } 
                if (this.checked == true && this.id == 'meal-maker-filter-none') {
                    $('.filter').prop('checked', false);
                }
                if ($('input[type="checkbox"]:checked').length == 0) {
                    $('#meal-maker-filter-none').prop('checked', true);
                }   
            });
        }
    }
})();
