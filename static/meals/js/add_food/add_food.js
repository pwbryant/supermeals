
let ADD_FOOD = (function() { 
    
    return {

        save_food: function() {

            $('#add-food-save').on('click', function() {
                const post_data = $('#add-food-form').serialize();
                console.log('post data', post_data);
                $('/meals/save-food', post_data, function(data) {
                    console.log('return data', data);
                });
            });
        }

    }

})();
