from django.shortcuts import render, redirect
from .forms import CreateUserForm,LoginForm
from django.contrib.sites.shortcuts import get_current_site
from .token import user_tokenizer_generate
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def register(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)

        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            subject = 'Account Verification'
            message = render_to_string('account/registration/email-verification.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': user_tokenizer_generate.make_token(user),
            })

            user.email_user(subject=subject, message=message)

            return redirect('email-verification-sent')
        
    context = {'form': form}

    return render(request, 'account/registration/register.html', context=context)

# Email View
def email_varification(request, uidb64, token):
    unique_id = force_str(urlsafe_base64_decode(uidb64))
    user = get_object_or_404(User, pk=unique_id)

    if user and user_tokenizer_generate.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('email-verification-success')
    else:
        return redirect('email-verification-failed')


def email_varification_sent(request):
    return render(request, 'account/registration/email-verification-sent.html')


def email_varification_success(request):
    return render(request, 'account/registration/email-verification-success.html')


def email_varification_failed(request):
    return render(request, 'account/registration/email-verification-failed.html')
 
#  Login Views
def my_login(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth.login(request, user)
                return redirect("home")
        
    context = {'form': form}
    return render(request, 'account/login/my-login.html', context=context)

from django.contrib.auth import logout as auth_logout
# logout view
@login_required
def logout(request):
    user = request.user
    user.save()
    auth_logout(request)
    return redirect('my-login') 