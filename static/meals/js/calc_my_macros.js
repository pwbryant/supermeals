
MACRO_FACTORS = {
	"fat": 9,
	"protein":4,
	"carbs":4
};
//tested
var key_press_hides_error = function () {
	$("input[type='text']").on("keypress",function() {
		$(".has-error").hide();
	});
};

//not tested
var set_navs_to_active = function() {
	$(".header__nav-tab").on("click",function() {
        $(".header__nav-tab").removeClass('active');
        $(this).addClass('active');
    });
}

//tested
var hide_home_header_on_tab_select = function() {
	$(".header__nav-tab").on("click",function() {
		$("#id_home_headline").hide();
	});
};

//not tested
var get_my_macros_page_content = function() {
	$("#my-macros-tab").on("click",function() {
		$.get("/meals/get-my-macros/",function(data) {
			$("#my-macros-container").removeClass("hide");
			$("#my-macros-container").html(data);
		});
	});
};

//not tested
var get_meal_maker_page_content = function() {
	$("#meal-maker-tab").on("click",function() {
        console.log('get meal maker');
		$.get("/meals/meal-maker/",function(data) {
			$("#meal-maker-container").removeClass("hide");
			$("#meal-maker-container").html(data);
		});
	});
};

//not tested
var save_my_macros_button_posts_form = function() {
	$("#save-my-macros-button").on("click",function() {
		var form_validated = form_validation("my-macros-form-container");
		if (form_validated) {
			var post_data = {};
			$("#my-macros-forms-container").find(":input[type='text'],:input[type='hidden'],:input[type='radio']:checked").each(function() {
			    post_data[this.name] = $(this).val();
			});
            //post_data["csrfmiddlewaretoken"] = $("input[name='csrfmiddlewaretoken']").val();
			$.post("/meals/save-my-macros",post_data,function(data) {
				if (data == "1") {
					$("#my-macros-successful-save").html("Macros Successfully Saved! Now Go Make a Meal!");
				} else {
					$("#my-macros-form-container").html(data);
				}
				
			});
		}
	});
}


//tested
var switch_between_imperial_metric = function() {
	$("input[name='unit-type']").on("click",function() {	
		var unit_type = $(this).val(),
        weight_input = "<label class='input__label'>Weight:</label>",
        height_input = "<label class='input__label'>Height:</label>",
        change_input = "<label class='input__label'>Rate of Change:</label>";
		if (unit_type == "metric") {
            weight_input += "<input type='text' name='weight-m' class='input__input--sm' placeholder='kg' data-type='number' />";
            height_input += "<input type='text' name='height-m' class='input__input--sm' placeholder='cm' data-type='number' />";
            change_input += "<input type='text' name='change-rate-m' class='input__input--sm' placeholder='kg/wk' data-type='number' />";

		} else {
            weight_input += "<input type='text' name='weight-i' class='input__input--sm' placeholder='lb' data-type='number' />";
            height_input += "<input type='text' name='height-i-ft' class='input__input--sm' placeholder='ft' data-type='number' />";
            height_input += "<input type='text' name='height-i-in' class='input__input--sm' placeholder='in' data-type='number' />";
            change_input += "<input type='text' name='change-rate-i' class='input__input--sm' placeholder='lb/wk' data-type='number' />";
		}
        $("#weight-input").html(weight_input);	
        $("#height-input").html(height_input);		
        $("#change-rate-input").html(change_input);
	});

}
//tested
var convert_between_metric_english = function(unit_value,conversion) {

	
	if (conversion == "in-to-cm") {
		return unit_value/0.39370;	
	}
	if (conversion == "lb-to-kg") {
		return unit_value * 0.45359237;	
	}
	if (conversion == "kg-to-lb") {
		return unit_value / 0.45359237;	
	}
}
//tested
var calc_tdee = function() {
	
	$("#calc-tdee").on("click",function() {	
		var form_validated = form_validation("tdee-form-container");
		if (form_validated) {
			var status_ = 1,
			tdee_data = {};
			$("#tdee-form-container").find(":input[type='text'],:input[type='radio']:checked").each(function() {
				
				if ($(this).val() == "") {
					status_ = 0;	
				} else {
					if (isNaN($(this).val())) {
						tdee_data[this.name] = $(this).val();
					} else {
						tdee_data[this.name] = parseFloat($(this).val());
					}	
				}		
			});
			if (status_ == 1) {
				var weight_change_direction = {
					"maintain": 0,
					"lose": -1,
					"gain": 1,
				}[tdee_data["direction"]];

				if (tdee_data["unit-type"] == "imperial") {
					tdee_data["weight"] = convert_between_metric_english(tdee_data["weight-i"],"lb-to-kg");
					tdee_data["height"] = convert_between_metric_english(tdee_data["height-i-ft"] * 12 + tdee_data["height-i-in"],"in-to-cm");
					tdee_data["change-rate"] = tdee_data["change-rate-i"] * weight_change_direction * 500;
				} else {
					tdee_data["weight"] = tdee_data["weight-m"];
					tdee_data["height"] = tdee_data["height-m"];
					tdee_data["change-rate"] = convert_between_metric_english(tdee_data["change-rate-m"],"kg-to-lb") * weight_change_direction * 500;
				}
				const formula_data = {
					"female":-161,
					"male":5,
					"weight":10 * tdee_data["weight"],
					"height":6.25 * tdee_data["height"],
					"age":5 * tdee_data["age"]
				};
				const activity_data = {
					"none":1.2,
					"light":1.375,
					"medium":1.55,
					"high":1.725,
					"very high":1.9
				};
				var tdee_return_value = (formula_data["weight"] + formula_data["height"] - formula_data["age"]  + formula_data[tdee_data["gender"]]) * activity_data[tdee_data["activity"]];
			    var change_tdee_return_value = ((formula_data["weight"] + formula_data["height"] - formula_data["age"]  + formula_data[tdee_data["gender"]]) * activity_data[tdee_data["activity"]]) + tdee_data["change-rate"];


			} else {
				tdee_return_value = "Missing Value. Check Form.";
			}

            tdee_return_value_str = "Maintenance: " + Math.round(tdee_return_value).toString() + " Cals";
            change_tdee_return_value_str = "Change: " + Math.round(change_tdee_return_value).toString() + " Cals";
			$("#tdee-result").html(tdee_return_value_str);
			$("#change-tdee-result").html(change_tdee_return_value_str);
            
			$("#hidden-tdee").val(Math.round(change_tdee_return_value));
			
			$("#choose-macros-form-container").removeClass("hide");
            document.getElementById("choose-macros-continue-button").scrollIntoView();
		}
	});
}

//tested
var change_change_rate_display = function() {
	$("input[name='direction']").on("click",function() {
		if (this.value == "maintain") {
			$("#change-rate-input").addClass("hide");
			$("#change-rate-i").val("0");
			$("#change-rate-m").val("0");
		} else {
			$("#change-rate-input").removeClass("hide");
			$("#change-rate-i").val("");
			$("#change-rate-m").val("");
		}	
	});
}

//tested
var choose_macro_handler = function() {
	$("#choose-macros-form input").on("keyup",function() {	
		if ($("#change-tdee-result") != "") {	
			var tdee_result = parseFloat($("#change-tdee-result").html().split(" ")[1]);
		} else {
			var tdee_result = parseFloat($("#tdee-result").html().split(" ")[1]);
		}
		var input_array = this.name.split("-"),
		macro_value = parseFloat(this.value),
		macro = input_array[0],
		type = input_array[1],
		macro_factor = MACRO_FACTORS[macro];
		if (type == "pct") {
			return_value = (tdee_result * macro_value / 100.0 / macro_factor).toFixed(0);
			var return_selector = "input[name='" + macro + "-g']";
		} else {
			return_value = (macro_value * macro_factor / tdee_result * 100).toFixed(0);	
			var return_selector = "input[name='" + macro + "-pct']";
		}
		if (isNaN(macro_value)) {
			$(return_selector).val("");
		} else {
			$(return_selector).val(return_value);
		}
		macro_percent_totaler("input[name='" + macro + "-pct']")

	});
}

//tested
var macro_percent_totaler = function(percent_selector) {
	var new_macro_percent = parseFloat($(percent_selector).val());

	if (isNaN(new_macro_percent)) {
		new_macro_percent = 0;

	} 
	old_macro_percent = parseFloat($(percent_selector).attr("data-value")),
	percent_diff = new_macro_percent - old_macro_percent,
	old_percent_total = parseFloat($("#choose-macros-total").html()),
	new_percent_total = old_percent_total - percent_diff;
	$("#choose-macros-total").html(new_percent_total);
	$(percent_selector).attr("data-value",new_macro_percent);
	if (new_percent_total == 0) {
		$("#choose-macros-continue-button").prop("disabled",false);
	} else {
		$("#choose-macros-continue-button").prop("disabled",true);
	}
}

//tested
var continue_button_displays_meal_snack_num_div = function() {
	$("#choose-macros-continue-button").on("click", function() {
		var form_validated = form_validation("choose-macros-form-container");
		if (form_validated) {
			$("#meal-template-meals-number-form-container").removeClass("hide");
            document.getElementById("meal-template-set-cals-continue-button").scrollIntoView();
		}
	});

}

//tested
var set_cals_continue_button_is_enabled_upon_input_keyup = function() {

	$("input[name='meal-number']").on("keyup",function() {
		var input_value = $(this).val();
		if (!(isNaN(input_value) | input_value == 0)) {
			$("#meal-template-set-cals-continue-button").prop("disabled",false);
		} else {

			$("#meal-template-set-cals-continue-button").prop("disabled",true);
		}
	});
}

//tested
var display_set_cals_form = function() {

	$("#meal-template-set-cals-continue-button").on("click",function() {
		var tdee = parseFloat($("#change-tdee-result").html().split(" ")[1]),
		meal_num = $("input[name='meal-number']").val();
		if (tdee == "") {
			tdee = $("#tdee-result").html();
		}
		var equal_cals = tdee / meal_num,
		set_cals_form = "<div class='content-box l-flex-col--start'>";
		set_cals_form += "<div class='content-box__header'>Set Your Meal Cals</div>";
        set_cals_form += "<div id='set-cals-form-container' class='l-flex--col-start'>";
		for (i=0;i<meal_num;i++) {
			set_cals_form += "<div id='meal-" + i + "-input' class='input l-flex--row-btw'>";
			set_cals_form += "<label class='input__label'>Meal " + (i + 1) + "</label>";
            set_cals_form += "<input class='input__input--sm' name='meal-" + i + "' type='text' value='" + equal_cals + "' data-value='" + equal_cals + "' data-type='number'/></div>";
		}
		set_cals_form += "<div class='l-flex--row-btw'><label class='input__label'>Cals Left</label><span id='meal-template-set-cals-total' class='text--label' name='remaining-cals'>0</span></div>";
		set_cals_form += "<button id='save-my-macros-button' class='btn'>Save Macro Info</button>";
        set_cals_form += "</div></div>"
		$("#meal-template-set-meal-cals-form-container").html(set_cals_form)
		save_my_macros_button_posts_form();//listener for save button
		meal_template_set_cals_totaler();//start lister on new inputs 
        document.getElementById("save-my-macros-button").scrollIntoView();

	});
}

//tested
var meal_template_set_cals_totaler = function() {

	$("#meal-template-set-meal-cals-form-container input").on("keyup",function() {
		current_cal_total = $("#meal-template-set-cals-total").html();
		var new_cal = parseFloat($(this).val());
		if (isNaN(new_cal)) {
			new_cal = 0;

		} 
		var old_cal = parseFloat($(this).attr("data-value")),
		cal_diff = new_cal - old_cal,
		old_cal_total = parseFloat($("#meal-template-set-cals-total").html()),
		new_cal_total = old_cal_total - cal_diff,
		tdee = $("#change-tdee-result").html();
		if (tdee === "") {
			tdee = $("#tdee-result").html();
		}
		
		$("#meal-template-set-cals-total").html(new_cal_total);
		$(this).attr("data-value",new_cal);
		if (new_cal_total == 0) {
			$("#save-my-macros-button").prop("disabled",false);
			$("#meal-template-set-cals-total").removeClass("text--color-alert");
		} else {
			$("#save-my-macros-button").prop("disabled",true);
			$("#meal-template-set-cals-total").addClass("text--color-alert");
		}
	});
}

var form_validation = function(form_id) {
	var errors = [],
	radio_names = [];
	$("#" + form_id).find(":input[type='text'],input[type='radio']:checked").each(function(index,element) {
		var value = $(element).val(),
		type = $(element).prop("type"),
		data_type = $(element).attr("data-type"),
		label = $(element).closest("div").find("label").text().replace(/[^a-zA-Z0-9_ ]/g,""),
		error = "";
		if (type == "text" && value == "") {
			error = "Missing " + label + " Value";
		} 
		if (type == "text" && data_type == "number"  && isNaN(value)) {
			error = label + " Field Forbids Non-Numeric Values";
		}
		if (type == "radio") {
			var name = $(element).prop("name");
			radio_names.push(name);
		} 
		if (error != "") {
			errors.push(error);
		}
	});

	$("#" + form_id).find("input[type='radio']").each(function(index,element) {
		var name = $(element).prop("name");
		if (!(radio_names.includes(name))) {
			var title_name = "";
			name.split("_").forEach(function(chunk) {
				title_name += chunk[0].toUpperCase() + chunk.slice(1) + " ";
			});
			error = title_name.trim() + " Option Needs To Be Selected";
			if (!(errors.includes(error))) {
				errors.push(error);
			}
		}
	});
	if (errors.length > 0) {
		var error_html = "<ul>";
		errors.forEach(function(error) {
			error_html += "<li>" + error + "</li>";
		});
		error_html += "</ul>";
		$("#client-side-form-errors").html(error_html);
		return 0;
	} else {
		$("#client-side-form-errors").html("");
		return 1;
	}	
}

