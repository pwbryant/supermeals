const convert_body_measurements_in_post_to_metric = function(
    height1, height2, weight, change_rate, post_data) {

    console.log('heights', height1, height2);
    console.log('weights', weight);

    const metric_height_0 = convert_between_metric_english(
        height1 * 12, 'in-to-cm'
    );
    const metric_height_1 = convert_between_metric_english(
        height2, 'in-to-cm'
    );
    let height;

    const decimal_val = 100 // allows rounding to 2 decimals
    height = Math.round(
        (metric_height_0 + metric_height_1) * decimal_val 
    ) / decimal_val;

    // remove old weight and change_rate
    post_data = post_data.replace(`&change_rate=${change_rate}`, '')
    post_data = post_data.replace(`&weight=${weight}`, '')

    weight = Math.round(convert_between_metric_english(
        weight, 'lb-to-kg'
    ) * decimal_val) / decimal_val;

    change_rate = Math.round(convert_between_metric_english(
        change_rate, 'lb-to-kg'
    ) * decimal_val) / decimal_val;
    
    // add metric height, weight, and change_rate
    post_data += `&height=${ height }`;
    post_data += `&weight=${ weight }`;
    post_data += `&change_rate=${ change_rate }`;

    return post_data;

}

// not tested
const clear_form_errors = function() {
    $('input[type="text"]').on('keyup', function() {
        $(this).siblings('.has-errors').html('');
        $(this).siblings().removeClass('has-errors');
    });
}

//not tested
var save_my_macros_button_posts_form = function() {
	$("#my-macros-form").on("submit", function(e) {

        e.preventDefault();
        clear_form_errors();
		const form_validated = form_validation("my-macros-form-container");
		if (form_validated) {

            let post_data = $('#my-macros-form').serialize();

            // total percentage to post
            const total_macro_percent = 100 - $('#choose-macros-total').text();
            post_data += `&total_macro_percent=${ total_macro_percent }`;

            // convert body measurements in post to metric
            const unit_type = $('input[name="unit_type"]:checked').val();
            if (unit_type === 'imperial') {
                // get height, weight, and change rate to switch to metric
                const height_0 = $('#my-macros-height-0').val();
                const height_1 = $('#my-macros-height-1').val();
                let weight = $('#my-macros-weight').val();
                let change_rate = $('#my-macros-change-rate').val();
                post_data = convert_body_measurements_in_post_to_metric(
                    height_0, height_1, weight, change_rate, post_data
                )
            } else {
                let height = height_0;
                post_data += `&height=${ height }`;
            }

            console.log('post', post_data);
			$.post("/meals/save-my-macros",post_data,function(data) {
                console.log('response data', data);
				if (data['status_code'] == 200) {
                    console.log('success!!!!');
					$("#my-macros-successful-save").html("Macros Successfully Saved! Now Go Make a Meal!");
				} else {
                    TMP = data['errors'];
                    for (input_name in data['errors']) {
                        let error_list = '<ul class="form-error">';
                        data['errors'][input_name].forEach(function(error) {
                            error_list += `<li>${error}</li>`;
                        });
                        error_list += '</ul>';
                        $(`#my-macros-${input_name}-errors`).addClass('has-errors');
                        $(`#my-macros-${input_name}-errors`).html(error_list);
                    }
					// $("#my-macros-form-container").html(data);
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
		var input_array = this.name.split("_"),
		macro_value = parseFloat(this.value),
		macro = input_array[0],
		type = input_array[1],
		macro_factor = MACRO_FACTORS[macro];
		if (type == 'percent') {
			return_value = (tdee_result * macro_value / 100.0 / macro_factor).toFixed(0);
			var return_selector = "input[name='" + macro + "_g']";
		} else {
			return_value = (macro_value * macro_factor / tdee_result * 100).toFixed(0);	
			var return_selector = "input[name='" + macro + "_percent']";
		}
		if (isNaN(macro_value)) {
			$(return_selector).val("");
		} else {
			$(return_selector).val(return_value);
		}
		macro_percent_totaler("input[name='" + macro + "_percent']")

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

