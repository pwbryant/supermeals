//Try loggin in. Returns 1 upon success and redirects
function try_log(login_type) {
	console.log('hello world');
	var csrftoken = $('input[name=csrfmiddlewaretoken]').val();
	if (login_type === 'guest') {
		var username = 'guest',
		password = 'password';
	} else {
		var username = $('#id_username').val(),
		password = $('#id_password').val();
	}
	if (username != 'guest' && (username.length === 0 || password.length === 0)) {
		console.log('bad input')
	} else {
		post_data = {'username':username, 'password':password,'csrfmiddlewaretoken':csrftoken};
		
		$.post('/meals/logging_in',post_data, function(data) {
			
			if (data === '1') {
				location.href = '/'					
			} else {
				console.log('error');
			}
			
		});
	}
}

//submits form data to create_account and recieves 1 upon succesfull POST and redirects to /
function create_account() {
	var csrftoken = $('input[name=csrfmiddlewaretoken]').val(),
	username=$('#id_username').val(),
	email=$('#id_email').val(),
	password =$('#id_password').val(),
	post_data = {'username':username,'email':email,'password':password,'csrfmiddlewaretoken':csrftoken};
	$.post('/meals/create_account', post_data, function(data) {
		if (data === '1') {					
			location.href = '/';
		} else {
			$('.has-error').html(data);
		}
	});
}

