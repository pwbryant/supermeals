const MY_MEAL_SEARCH = (function() { 
    
    return {
        my_meals_food_search_listener : function() { 

			search_obj = this;
			search_obj['my-meals'] = {};
            $('#my-meals-search-button').on('click', function() {
                const search_terms = $.trim($('#my-meals-search-input').val());
                if(search_terms != '') {

                    $.get('/meals/search-foods/user/' ,{'search_terms':search_terms},function(data) {
                        const search_results = data['search-results'];
                        search_results_html = search_obj.format_food_search_results(search_results);
                        $('#my-meals-search-results-container').html(search_results_html);
                        search_obj.add_result_button_lister();
                        search_results.map(function(r, i) {
                            search_obj['my-meals'][r.id] = r
                        });

                    });
                }
            });
        },

        format_food_search_results : function(search_results) {

            let search_results_html = '';	
            search_results.forEach(function(e,i) {
                search_results_html += "<div class='my-meal-result search-result'><span>" + e.name + "</span><button id='my-meal-result-" + e.id + "' class='icon'><i class='fa fa-plus'></i></button></div>"; 
            });
            return search_results_html;
        },

        add_result_button_lister: function() {
			search_obj = this;
			$('.my-meal-result>button').on('click',function() {
                const my_meal_id = this.id.split('-')[3];
                const my_meal_info = search_obj['my-meals'][my_meal_id];
                search_obj.add_result_button_shows_modal(my_meal_info);
            });
        },

        add_result_button_shows_modal: function(my_meal_info) {

            let modal = document.getElementById('my-meal-modal');

            modal.style.display = 'block';
            
            $('#my-meals-modal-header').text(my_meal_info['name']);

            $('.close-modal').on('click', function() {
                // $(modal).find(modal_inputs).val('').text('').end();
                modal.style.display = 'none';
            });
        }
    }
})();
