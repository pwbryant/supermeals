const EASY_PICK = (function() { 
    
    return {
        easy_pick: function() {

            $('input[name="easy-pick"]').on('change', function() {
                $.get('/meals/easy-picks/recent/', function(data) {

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
