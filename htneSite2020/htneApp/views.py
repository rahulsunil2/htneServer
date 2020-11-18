from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.datastructures import MultiValueDictKeyError
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from .tokens import account_activation_token
from .models import UserProfile, Team


@login_required
def home(request):
    return render(request, 'dashboard.html', {'user': request.user})


def user_profile_edit(request):
    if request.method == "POST":
        userProfile = UserProfile.objects.get(user=request.user)
        userProfile.school = request.POST['school']
        userProfile.grad_year = request.POST['grad_year']
        userProfile.gender = request.POST['gender']
        userProfile.designation = request.POST['designation']
        userProfile.desc = request.POST['desc']
        userProfile.save()
        return redirect('/')

    print(UserProfile.objects.filter(user=request.user))
    if len(UserProfile.objects.filter(user=request.user)) == 0:
        userProfile = UserProfile(user=request.user, school="", grad_year="2022-01-01", gender="", designation="", desc="")
        userProfile.save()
    userProfile = UserProfile.objects.get(user=request.user)
    context = userProfile.__dict__
    context['grad_year'] = context['grad_year'].strftime('%Y-%m-%d')

    return render(request, 'profile.html', context)


def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your HTNE account.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        userProfile = UserProfile(user=user)
        userProfile.save()
        login(request, user)
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')


def team_register(request):
    if request.method == "POST":
        try:
            team = Team.objects.get(team_name=request.GET['existing_team_name'])
        except MultiValueDictKeyError:
            team = Team(
                team_name=request.POST['new_team_name']
            )
            team.save()
        team.members.add(request.user.id)
        team.save()
        return render(request, 'team_confirm.html', context={'team_name': team.team_name})

    return render(request, 'team_register.html')
