let ADD_RECIPE = (function() { 


    return {

        add_recipe_form_save: function() {

            this_add_recipe_obj = this;
            $('#add-recipe-save-button').on('click', function() {
                const form_valid = this_add_recipe_obj.add_recipe_validation();
                if (form_valid) {
                    const post_data = $('#add-recipe-form').serialize();
                    $.post('/meals/save-recipe', post_data, function(data) {
                        if (data['status'] == 'success') {
                            $('#add-recipe-save-status').text('Recipe Saved');
                        }
                    });
                }
            });
        },

        add_recipe_validation: function() {

            let is_valid = true;
            $('#add-recipe-form input:visible').each(function(i, e) {
                
                const error_div = $(`#${e.id}-errors`);
                if ($.trim(e.value) == '') {
                    is_valid = false;
                    if (e.name == 'name') {
                        error_div.html('<p style="color:red;">Enter recipe name</p>');
                    } else {
                        error_div.html('<p style="color:red;">Enter ingredient amount</p>');
                    }
                } else {
                    error_div.html('');
                }

            });

            const ingredient_count = $('.add-recipe-ingredient').length;
            const ingredient_errors = $('#add-recipe-ingredients-container-errors');
            if (ingredient_count < 2) {
                is_valid=false;
                ingredient_errors.html('<p style="color:red;">Recipes require more than one ingredient');
               
            } else {
                ingredient_errors.html('');
            }

            return is_valid;
        }
    }
})();
