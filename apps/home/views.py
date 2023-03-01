# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import loader
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import user_passes_test
from users.models import Subscriptions, UserSubscription, StatusApproved


# @login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}
    if request.user.is_superuser:
        html_template = loader.get_template('home/send_email.html')
    else:
        subscriptions = Subscriptions.objects.filter(status='APPROVED')
        print(request.user.id)
        user_subscriptions = UserSubscription.objects.filter(student_id=request.user.id)
        print(user_subscriptions)
        context['subscriptions'] = subscriptions
        context['usersubid'] = user_subscriptions.values_list('Subscriptions', flat=True)
        print(context['usersubid'])
        html_template = loader.get_template('home/stu_index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def update_user_subscriptions(request, id):
    """
    Allows a logged-in user to update their subscriptions by adding or removing a subscription from their list of subscriptions

    Parameters:
        request (HttpRequest): The HTTP request object
        id (int): The id of the subscription to add or remove

    Returns:
        HttpResponse: A response containing the updated list of subscriptions for the user

    """
    try:
        # Get the user object
        user = get_user_model().objects.get(id=request.user.id)

        # Check if the user has a UserSubscription object
        has_subscription = UserSubscription.objects.filter(student=user).exists()

        if has_subscription:
            # Get the user's UserSubscription object
            new_user_subscription = UserSubscription.objects.filter(student_id=request.user.id).first()
            if not new_user_subscription:
                # handle the case when no UserSubscription object is found for the student_id
                return HttpResponse("User subscription not found")

            # Get the user's old subscriptions
            old_subscriptions = list(new_user_subscription.Subscriptions.values_list('id', flat=True))

            # Check if the subscription to add or remove is already in the user's subscriptions
            if int(id) in old_subscriptions:
                old_subscriptions.remove(int(id))
            else:
                old_subscriptions.append(int(id))

            # Set the user's updated subscriptions
            new_user_subscription.Subscriptions.set(old_subscriptions)

        else:
            # If the user does not have a UserSubscription object, create one
            subscription = Subscriptions.objects.get(id=id)
            user_subscription = UserSubscription.objects.create(student=user)
            user_subscription.subscriptions.add(subscription)

        # Get the approved subscriptions and the user's subscriptions
        subscriptions = Subscriptions.objects.filter(status='APPROVED')
        user_subscriptions = UserSubscription.objects.filter(student_id=request.user.id)

        # Create a context with the subscriptions and the user's subscriptions
        context = {
            'subscriptions': subscriptions,
            'usersubid': user_subscriptions.values_list('Subscriptions', flat=True),
        }

        # Render the student index page with the updated context
        html_template = loader.get_template('home/stu_index.html')
        return HttpResponse(html_template.render(context, request))
    except:
        subscriptions = Subscriptions.objects.filter(status='APPROVED')
        user_subscriptions = UserSubscription.objects.filter(student_id=request.user.id)
        context = {
            'subscriptions': subscriptions,
            'usersubid': user_subscriptions.values_list('Subscriptions', flat=True),
        }
        html_template = loader.get_template('home/stu_index.html')
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def send_email(request):
    context = {}
    context['subscriptions'] = Subscriptions.objects.all()

    if request.user.is_staff:
        """
        Sends email to all users associated with a specific subscription or all users if 'ALL' is selected.
    
        If request method is 'POST', gets the subject, message, from email and selected subscriptions from the request
        data. Then gets all the user subscriptions associated with the selected subscriptions and filters out only student
        users. Sends email to all the student users' email addresses.
    
        If request method is 'GET', renders the send email form along with all available subscriptions to select.
    
        :param request: HTTP request object.
        :return: HTTP response object containing either the send email form or success message after sending the email.
        """
        if request.method == 'POST':
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            from_email = request.POST.get('from_email')
            subscriptions = request.POST.get('subscriptions')

            # Get the user subscriptions object for the selected subscriptions
            if subscriptions == 'ALL':
                user_subscriptions = UserSubscription.objects.all()
            else:
                subscription = Subscriptions.objects.get(id=int(subscriptions))
                user_subscriptions = UserSubscription.objects.filter(Subscriptions=subscription)

            # Get all student objects that are associated with the subscription
            students = get_user_model().objects.filter(usersubscription__in=user_subscriptions, is_student=True)

            # Send email to all the student users' email addresses
            for recipient in students.values_list('email', flat=True):
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=from_email,
                    recipient_list=[recipient],
                    fail_silently=False,
                )

            # Render the success message page after email has been sent
            return render(request, 'home/success.html')

        # Render to send email form along with all available subscriptions to select
        html_template = loader.get_template('home/send_email.html')
        return HttpResponse(html_template.render(context, request))
    else:
        html_template = loader.get_template('home/stu_index.html')
        return HttpResponse(html_template.render(context, request))


def get_subscription(request, id):
    """
    Retrieves a subscription object with the given ID from the database and renders
    the subscription HTML template with the subscription object as context.

    Args:
        request: The HTTP request object.
        id: The ID of the subscription to retrieve.

    Returns:
        An HTTP response containing the rendered subscription HTML template.
    """
    context = {}
    subscription = Subscriptions.objects.get(id=id)
    context['subscription'] = subscription
    html_template = loader.get_template('home/subscription.html')
    return HttpResponse(html_template.render(context, request))


class SubscriptionsForm(forms.ModelForm):
    class Meta:
        model = Subscriptions
        fields = ['name', 'description', 'status']


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_staff)
def subscription_list(request):
    subscriptions = Subscriptions.objects.all()
    return render(request, 'home/subscription_list.html', {'subscriptions': subscriptions})


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_staff)
def subscription_detail(request, pk):
    subscription = get_object_or_404(Subscriptions, pk=pk)
    return render(request, 'home/subscription_detail.html', {'subscription': subscription})


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_staff)
def subscription_create(request):
    status_approved = StatusApproved.get_status_approved()

    if request.method == 'POST':
        name = request.POST["name"]
        description = request.POST["description"]
        status = request.POST["approved_status"]
        dict = {
            'name': name,
            'description': description,
            'status': status,
        }

        subscription = Subscriptions(**dict)
        subscription.save()
        form = SubscriptionsForm(request.POST)
        if form.is_valid():
            subscription = form.save(commit=False)
            print(subscription)
            subscription.save()
            return redirect('subscription_detail', pk=subscription.pk)
    else:
        form = SubscriptionsForm()
    return render(request, 'home/subscription_form.html', {'form': form, 'status_approved': status_approved})


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_staff)
def subscription_edit(request, pk):
    subscription = get_object_or_404(Subscriptions, pk=pk)
    if request.method == 'POST':
        name = request.POST["name"]
        description = request.POST["description"]
        status = request.POST["approved_status"]
        dict = {
            'name': name,
            'description': description,
            'status': status,
        }
        sub = Subscriptions.objects.filter(pk=pk).update(**dict)
        form = SubscriptionsForm(request.POST, instance=subscription)
        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.save()
            return redirect('subscription_detail', pk=subscription.pk)
    else:
        form = SubscriptionsForm(instance=subscription)
    return render(request, 'home/subscription_form_edit.html', {'form': form, "subscription": subscription})


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.is_staff)
def subscription_delete(request, pk):
    subscription = get_object_or_404(Subscriptions, pk=pk)
    subscription.delete()
    return redirect('subscription_list')
