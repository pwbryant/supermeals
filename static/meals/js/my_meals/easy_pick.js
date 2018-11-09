const EASY_PICK = (function() { 
    
    return {
        // gets my meals sorted by 'recent' or 'popular'
        // gets triggerd when the radio inputs change
        easy_pick: function() {
            $('input[name="easy-pick"]').on('change', function() {
                const pick_type = $('input[name="easy-pick"]:checked').val();
                $.get(`/meals/easy-picks/${pick_type}/`, function(data) {

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
