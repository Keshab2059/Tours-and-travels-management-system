from django.shortcuts import redirect

def admin_only(func):
    def wrapper_func(request,*args,**kwargs):
        if request.user.is_staff:
            return func(request,*args,**kwargs)
        else:
            return redirect('home-page')
    return wrapper_func

def user_only(func):
    def wrapper_func(request,*args,**kwargs):
        if request.user.is_staff:
            return redirect('dashboard')
        else:
            return func(request,*args,**kwargs)
    return wrapper_func