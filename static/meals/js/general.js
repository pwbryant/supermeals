MACRO_FACTORS = {
	"fat": 9,
	"protein":4,
	"carbs":4
};

var key_press_hides_error = function () {
	$("input[type='text']").on("keypress",function() {
		$(".has-error").hide();
	});
};

var set_navs_to_active = function() {
	$(".header__nav-tab").on("click",function() {
        $(".header__nav-tab").removeClass('active');
        $(this).addClass('active');
    });
}

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

var hide_home_header_on_tab_select = function() {
	$(".header__nav-tab").on("click",function() {
		$("#id_home_headline").hide();
	});
};


var get_tab_page_content = function() {
	$(".content-tab").not('.disabled').on("click",function() {
        const tab_type = $(this).attr('id').slice(0,-4);
        const url = `meals/${tab_type}/`;
        const tab_container = `#${tab_type}-container`;
		$.get(url, function(data) {
			$(tab_container).removeClass("hide");
			$(tab_container).html(data);
		});
	});
};

const disabled_return_alert = function() {

    $('.disabled').on('click', function() {
        alert('You must have an account to use this. GO SIGN UP :)!');
    });
}
