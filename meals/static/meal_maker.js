var get_goal_meal_cals_and_set_grams = function(this_) {
	if ($.trim(this_.value) != 'header' && $.trim(this_.value) != '') {
		var cals = parseFloat(this_.value),
		fat_percent = parseFloat($('#id_goal_meal_macros_table td:eq(1)').text()),
		carbs_percent = parseFloat($('#id_goal_meal_macros_table td:eq(4)').text()),
		protein_percent = parseFloat($('#id_goal_meal_macros_table td:eq(7)').text()),
		fat_grams = Math.round(fat_percent / 100 * cals / 9),
		carbs_grams = Math.round(carbs_percent / 100 * cals / 4),
		protein_grams = Math.round(protein_percent / 100 * cals / 4)
		;
		$('#id_goal_meal_macros_table td:eq(2)').text(fat_grams);
		$('#id_goal_meal_macros_table td:eq(5)').text(carbs_grams);
		$('#id_goal_meal_macros_table td:eq(8)').text(protein_grams);
	} else {
		$('#id_goal_meal_macros_table td:eq(2)').text('-');
		$('#id_goal_meal_macros_table td:eq(5)').text('-');
		$('#id_goal_meal_macros_table td:eq(8)').text('-');
	}
}
//tested
var goal_meal_cals_dropdown_fills_in_grams = function() {
	$('#id_goal_meal_cals_select').on('change',function() {
		get_goal_meal_cals_and_set_grams(this);
		$('#id_goal_meal_cals').val('');
	});
}
//tested
var goal_meal_cals_input_fills_in_grams = function() {
	$('#id_goal_meal_cals').on('keyup',function() {
		get_goal_meal_cals_and_set_grams(this);
		$('#id_goal_meal_cals_select>option:eq(0)').prop('selected',true);
	});
}

