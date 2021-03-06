let SEARCH = (function() { 

    return {

        // tested in Functional Tests
        get_food_search_info : function(tab_name, search_terms) { 

            let search_data = {};
            if(search_terms != '') {
                let filters = [];
                if ($(`#${tab_name}-filter-none`).prop('checked')) {
                    filters = $(`.${tab_name}-filter:not(checked)`).map(function(i, filter) {
                        return filter.value
                    }).toArray();
                    
                } else {
                    filters = $(
                        `.${tab_name}-filter:checked`
                    ).map(function(i, filter) {
                        return filter.value
                    }).toArray();
                }

                search_data['search_terms'] = search_terms;
                search_data['filters'] = filters;

            } else {
                $(`#${tab_name}-search`).val('');
                $(`#${tab_name}-search-results-container`).html('');
            }

            return search_data;
        },

        format_food_search_results: function(tab_name, search_results, result_class) {

            var search_results_html = '';	
            search_results.forEach(function(e,i) {
                search_results_html += `<div class='search-result ${tab_name}-search-result ${result_class} l-flex--row-start'>`;
                search_results_html += `<button id='${tab_name}-${result_class}-${e.id}' class='icon search-result__button ${tab_name}-search-result__button ${tab_name}-${result_class}__button bm-margin--sm-right' value='${i}'><i class='fa fa-plus'></i></button><div class='search-result__name ${tab_name}-search-result__name'>${e.name}</div></div>`; 

            });
            return search_results_html;
        },

        // // tested in FT
        filter_checkbox_behavior: function(tab_name) {
            $(`.${tab_name}-filter, .${tab_name}-non-filter`).on('click', function() {
                if (this.checked == true && this.id != `${tab_name}-filter-none`) {
                    $(`#${tab_name}-filter-none`).prop('checked', false);
                } 
                if (this.checked == true && this.id == `${tab_name}-filter-none`) {
                    $(`.${tab_name}-filter`).prop('checked', false);
                }
                if ($(`.${tab_name}-filter:checked`).length == 0) {
                    $(`#${tab_name}-filter-none`).prop('checked', true);
                }   
            });
        }
    }
})();
