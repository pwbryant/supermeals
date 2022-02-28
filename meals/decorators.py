from django.shortcuts import render

# define your decorators here
def user_is_not_guest(function):
    def wrap(request, *args, **kwargs):
        if request.user.username == "guest":
            return render(request, "meals/bad_raw_url.html")
        else:
            return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__

    return wrap
