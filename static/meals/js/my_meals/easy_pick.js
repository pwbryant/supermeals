const EASY_PICK = (function() { 
    
    return {
        // gets my meals sorted by 'recent' or 'popular'
        // gets triggerd when the radio inputs change
        easy_pick: function() {
            $('#my-meals-select').on('change', function() {
                const meal_or_recipe = $('#my-meals-select').find(':selected').val();
                $.get(`/meals/easy-picks/${meal_or_recipe}/`, function(data) {

                    console.log('data', data);
                    let my_meals = '';
                    data['my_meals'].map(function(meal, i) {
                        my_meals += `<div class='my-meals-easy-picks-meal'>${meal.name}</div>`;
                    });

                    $('#my-meals-easy-picks-meals-container').html(my_meals);

                })
            });
       }
    }
})();
