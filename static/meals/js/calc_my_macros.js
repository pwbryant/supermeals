

//not tested
var save_my_macros_button_posts_form = function() {
	$("#my-macros-form").on("submit", function(e) {

        e.preventDefault();
		var form_validated = form_validation("my-macros-form-container");
		if (form_validated) {
			// var post_data = {};

            const post_data = $('#my-macros-form').serialize();
			// $("#my-macros-forms-container").find(":input[type='text'],:input[type='hidden'],:input[type='radio']:checked").each(function() {
			    // post_data[this.name] = $(this).val();
			// });
            //post_data["csrfmiddlewaretoken"] = $("input[name='csrfmiddlewaretoken']").val();
            console.log('post data', post_data);
			$.post("/meals/save-my-macros",post_data,function(data) {
				if (data == "1") {
                    console.log('success!!!!');
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
	$("input[name='unit_type']").on("click",function() {	
        console.log('switch');
		const unit_type = $(this).val();
        const tab_name = 'my-macros';
        let weight_placeholder = 'lbs';
        let height_placeholder_0 = 'ft';
        let height_placeholder_1 = 'in';
        let change_rate_placeholder = 'lbs/wk';

		if (unit_type == "metric") {
            weight_placeholder = 'kgs';
            height_placeholder_0 = 'cm';
            change_rate_placeholder = 'kgs/wk';
            $(`#${tab_name}-height-1`).hide();	

		} else {
            $(`#${tab_name}-height-1`).show();	
            $(`#${tab_name}-height-1`).attr('placeholder', height_placeholder_1);	
		}
        $(`#${tab_name}-weight`).attr('placeholder', weight_placeholder);	
        $(`#${tab_name}-height-0`).attr('placeholder', height_placeholder_0);	
        $(`#${tab_name}-change-rate`).attr('placeholder', change_rate_placeholder);	
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

				if (tdee_data["unit_type"] == "imperial") {
					tdee_data["weight"] = convert_between_metric_english(tdee_data["weight"],"lb-to-kg");
					tdee_data["height"] = convert_between_metric_english(tdee_data["height_0"] * 12 + tdee_data["height_1"],"in-to-cm");
					tdee_data["change_rate"] = tdee_data["change_rate"] * weight_change_direction * 500;
				} else {
					// tdee_data["weight"] = tdee_data["weight-m"];
					// tdee_data["height"] = tdee_data["height-m"];
					tdee_data["change_rate"] = convert_between_metric_english(tdee_data["change_rate"],"kg-to-lb") * weight_change_direction * 500;
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
			    var change_tdee_return_value = ((formula_data["weight"] + formula_data["height"] - formula_data["age"]  + formula_data[tdee_data["gender"]]) * activity_data[tdee_data["activity"]]) + tdee_data["change_rate"];


			} else {
				tdee_return_value = "Missing Value. Check Form.";
			}
            console.log('tdee-data', tdee_data);


            tdee_return_value_str = "Maintenance: " + Math.round(tdee_return_value).toString() + " Cals";
            change_tdee_return_value_str = "Change: " + Math.round(change_tdee_return_value).toString() + " Cals";
			$("#tdee-result").html(tdee_return_value_str);
			$("#change-tdee-result").html(change_tdee_return_value_str);
            
			$("#hidden-tdee").val(Math.round(change_tdee_return_value));
			
			$("#choose-macros-form-container").removeClass("hide");
            document.getElementById("save-my-macros-button").scrollIntoView();
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
		$("#save-my-macros-button").prop("disabled",false);
	} else {
		$("#save-my-macros-button").prop("disabled",true);
	}
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

