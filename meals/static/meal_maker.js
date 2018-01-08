var goal_meal_cals_dropdown_fills_in_grams = function() {
	$('#id_goal_meal_cals_select').on('change',function() {
		var cals = parseFloat(this.value),
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
	});
}
