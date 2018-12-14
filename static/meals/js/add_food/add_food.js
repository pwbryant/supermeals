
let ADD_FOOD = (function() { 
    
    return {

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
