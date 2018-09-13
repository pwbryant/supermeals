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

//not tested
const hide_non_active_content = function() {

	$(".header__nav-tab").on("click",function() {

        const this_tab_id = $(this).attr('id');

        $('.header__nav-tab').each(function() {
            const tab_id = $(this).attr('id');
            if (typeof tab_id !== 'undefined' && tab_id !== this_tab_id) {
                const container_id = tab_id.replace('-tab', '-container');
                $(`#${container_id}`).addClass('hide');
            }
        });
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

