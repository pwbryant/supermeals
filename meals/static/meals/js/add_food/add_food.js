
let ADD_FOOD = (function() { 
    
    return {

        enable_serving: function() {
            $('#add-food-enable-serving').on('change', function() {
                field_set = $('#add-food-serving');
                console.log('f', field_set);
                if ($(this).prop('checked')) {
                    field_set.prop('disabled', false)
                } else {
                    field_set.prop('disabled', true)
                }
            });
        },
        save_food: function() {
            $('#add-food-form').on('submit', function(e) {
                e.preventDefault();
                const post_data = $('#add-food-form').serialize();
                console.log('post data', post_data);
                $.post('/meals/add-food/', post_data, function(data) {
                    console.log('return data', data);
                    if ( data['status_code'] == 201 ) {
                        $('#add-food-save-status').html('Food Saved!');

                        setTimeout(
                            function() { $("#add-food-save-status").empty(); }
                            , 3000
                        );
                        
                    } else {
                        $('#add-food-save-status').html('Errors!');
                    }
                });
            });
        }

    }

})();
