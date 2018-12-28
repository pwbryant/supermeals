let ADD_RECIPE = (function() { 

    return {
        add_recipe_form_save: function() {
            this_add_recipe_obj = this;
            $('#add-recipe-form').on('submit', function(e) {
                // clear any existing errors
                e.preventDefault();
                $('.form-errors').html('');
                const form_valid = this_add_recipe_obj.add_recipe_validation();
                console.log('clicked valid', form_valid);
                if (form_valid) {
                    const post_data = $('#add-recipe-form').serialize();
                    console.log('post data', post_data)
                    $.post('/meals/save-recipe', post_data, function(data) {
                        console.log('data', data);
                        if (data['status'] == 'success') {
                            $('#add-recipe-save-status').text('Recipe Saved');

                            // clear search results
                            $('#add-recipe-search-results-container').html('');

                            // clear form of ingredients
                            $('#add-recipe-ingredients-container').html('');

                            // clear inputs
                            $('#add-recipe-notes').val('');
                            $('input:visible').val('');
                        }
                        if (data['status'] == 'failure') {
                            for (let key in data['errors']) {
                                const error_id = `#add-recipe-${key.replace(/_/g, '-')}-errors`;
                                let errors = '';
                                data['errors'][key].forEach(function(e, i) {
                                    errors += `<p class='form-error'>${e}</p>`;
                                });
                                $(error_id).html(errors);
                            }
                        }
                    });
                }
            });
        },

        add_recipe_validation: function() {

            let is_valid = true;
            $('#add-recipe-form input:visible').each(function(i, e) {
                
                console.log('e name', e.name);
                const error_div = $(`#add-recipe-${e.name.replace(/_/g, '-')}-errors`);
                console.log(`#add-recipe-${e.name.replace(/_/g, '-')}-errors`);
                if ($.trim(e.value) == '') {
                    is_valid = false;
                    if (e.name == 'name') {
                        error_div.html('<p class="form-error">Enter recipe name</p>');
                    } else {
                        error_div.html('<p class="form-error">Enter ingredient amount</p>');
                    }
                } else {
                    error_div.html('');
                }

            });

            const ingredient_count = $('.add-recipe-ingredient').length;
            const ingredient_errors = $('#add-recipe-ingredients-container-errors');
            if (ingredient_count < 2) {
                is_valid=false;
                ingredient_errors.html('<p class="form-error">Recipes require more than one ingredient');
               
            } else {
                ingredient_errors.html('');
            }

            return is_valid;
        }
    }
})();
