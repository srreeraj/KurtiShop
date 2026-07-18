from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

# Create your views here.

def dashboard_login(request):

    if request.user.is_authenticated and request.user.is_staff:
        return redirect("dashboard:home")

    error = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user and user.is_staff:
            login(request, user)
            return redirect('dashboard:home')

        error = "Invalid username or password"

    return render(
        request,
        "dashboard/auth/login.html",
        {"error" : error}
    )


@login_required
@user_passes_test(lambda u : u.is_staff)
def dashboard_home(request):
    context = {}
    return render(
        request,
        "dashboard/dashboard/index.html",
        context
    )

@login_required
def dashboard_logout(request):
    logout(request)
    return redirect('dashboard:login')