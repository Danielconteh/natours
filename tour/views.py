from xmlrpc.client import boolean
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

import json
from django.conf import settings
from django.dispatch import receiver
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from requests import request
# from django.views import View
from .models import Tour, Images, Review, Tour_Guide, Booked_Tour
import datetime
import random
#########################################################
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.contrib import messages
from django.db.models import Avg, Q
from django.core.mail import send_mail


# Create your views here.


# ALL TOURS

def tour(request):
    bannerImage = []
    data = Tour.objects.all()
    for index, _ in enumerate(data):
        data[index].startDates = datetime.datetime.fromisoformat(data[index].startDates[0].split('T')[0]).strftime(
            "%d %B %Y")
        bannerImage.append(data[index].coverImage)

    banner = bannerImage[random.randrange(0, len(data))]

    return render(request, 'tour.html', {'data': data, 'banner': banner, 'bannerImage': bannerImage})


# SIGNLE TOUR


def single_tour(request, tour_slug):
    # try: data = Tour.objects.get(slug=tour_slug)
    # except ObjectDoesNotExist: return redirect('home')
    data = get_object_or_404(Tour, slug=tour_slug)

    next_date = datetime.datetime.fromisoformat(data.startDates[0].split('T')[0]).strftime("%B %Y")

    coords = data.location[0]["coordinates"]

    img = Images.objects.filter(post__pk=data.id)

    imgs, locationDes, locationCoords, locationDay, review = [], [], [], [], []

    for images in img: imgs.append(images.images)

    locations, par_info = data.location, [data.description]

    par_description = [y for x in par_info for y in x.split('.\\n')]

    for item in locations:
        locationDes.append(item['description'])
        locationDay.append(item['day'])
        locationCoords.append(item['coordinates'])

    startLocation = data.startLocation.coordinates

    # ADD REVIEWS TO TAST!
    review_tour = Review.objects.filter(tour=tour_slug)

    if review_tour.exists():
        for index, _ in enumerate(review_tour):
            review_user = User.objects.filter(email=review_tour[index].user)
            review.append({"review_text": review_tour[index].review,
                           'rating': float(review_tour[index].rating),
                           'image': review_tour[index].user_img,
                           'name': review_user[0].first_name and review_user[0].first_name + ' ' + review_user[
                               0].last_name or review_user[0],
                           })

    # updating data ratingAvg for any single tour  [no rating yet!]
    # updating data ratingAvg for any single tour  [no rating yet!]
    if type(review_tour.aggregate(Avg('rating'))['rating__avg']) is type(None):
        data.ratingAvg = 0
        data.save()

    else:
        data.ratingAvg = float(review_tour.aggregate(Avg('rating'))['rating__avg'])
        data.save();

    # FILTER A TOUR GUIDE
    tour_guide = Tour_Guide.objects.all()[:3]

    return render(request, 'single_tour.html',
                  {'data': data, 'next_date': next_date, 'imgs': imgs, 'coords': coords, 'locationDes': locationDes,
                   'locationCoords': locationCoords, 'locationDay': json.dumps(locationDay),
                   'startLocation': startLocation, 'par_description': par_description, 'review': review,
                   'tour_guide': tour_guide})


# REVIEW LOGIC
def Review_model(request, review_slug):
    if not request.user.is_authenticated: return redirect('/accounts/login/')

    if not request.POST['review']:
        messages.warning(request, 'please write something!')
        return redirect('/{}'.format(request.build_absolute_uri().split('/')[-1]))

    if not request.POST['rating']:
        messages.warning(request, 'please rate this tour!')
        return redirect('/{}'.format(request.build_absolute_uri().split('/')[-1]))

    rating = request.POST['rating'] or 0

    user_social_account = request.user.socialaccount_set.all()[0].extra_data

    user_image = user_social_account.get('avatar_url', user_social_account.get('picture',
                                                                               'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQSVNDTCFdYkZVDp49l0Sux5b0qaQboq6swiLhZI04&s'))

    data = Review(tour=review_slug, user=request.user.email, review=request.POST['review'],
                  rating=float(rating), user_img=user_image,
                  time_posted=datetime.datetime.now())
    try:
        data.save()
    except IntegrityError:
        messages.warning(request, 'you have already write review for  this tour!!')
        return redirect('/{}'.format(request.build_absolute_uri().split('/')[-1]))

    return redirect('/{}'.format(request.build_absolute_uri().split('/')[-1]))


# 901687663123-e0s0dtfarnr0d9e3u9bc6fbvkr8tii7h.apps.googleusercontent.com
# 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


# CHECKOUT SESSION

stripe.api_key = settings.STRIPE_SECRET_KEY


def CreateCheckoutSessionView(request, tour_slug):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

    data = Tour.objects.filter(slug=tour_slug)[0]

    user_exit = Booked_Tour.objects.filter(Q(user_email=request.user.email) & Q(tour_slug=tour_slug))

    if user_exit.exists():
        messages.info(request, 'You have booked this tour!, please book another one!')
        return redirect('/{}'.format(tour_slug))

    YOUR_DOMAIN = 'https://django-natours.herokuapp.com'
    # 'http://127.0.0.1:8000'

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': data.price * 10,
                    'product_data': {
                        'name': data.name,
                        'images': [data.coverImage.url],
                    },
                },
                'quantity': 1,
            },
        ],
        metadata={
            "tour_slug": data.slug,
            "price": data.price,
            "email": request.user.email,

        },
        mode='payment',
        success_url=YOUR_DOMAIN + '/success/',
        cancel_url=YOUR_DOMAIN,
    )
    return redirect(checkout_session.url, code=303)


# STRIPE stripe_webhook
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET_KEY


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=404)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=404)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session['metadata']['email']
        customer_book_tour = session['metadata']['tour_slug']
        if customer_email and customer_book_tour:
            data = Booked_Tour(user_email=customer_email, tour_slug=customer_book_tour)
            try:
                data.save()
            except:
                return HttpResponse(404)

        # send_mail(
        #         subject="Here is your product",
        #         message=f"Thanks for your purchase. Here is the product you ordered. The URL is",
        #         recipient_list=[customer_email],
        #         from_email="matt@test.com"
        #         )

        return JsonResponse({'customer_email': customer_email, 'customer_book_tour': customer_book_tour})


def booked_secessful(request):
    print("sucessfull  ===  !!!!!!!!!!")
    if not request.user.is_authenticated: return redirect('/accounts/login/')

    tour = []
    data = Booked_Tour.objects.filter(user_email=request.user.email)

    if data.exists():
        for item in data:
            if item:
                tour = Tour.objects.filter(slug=item.tour_slug)
    if tour:
        tour[0].startDates = datetime.datetime.fromisoformat(tour[0].startDates[0].split('T')[0]).strftime("%B %Y")

    return render(request, 'booked_sucess.html', {'data': tour})


def delete_booked_tour(request, delete_slug):
    if not request.user.is_authenticated: return redirect('home')
    data = Booked_Tour.objects.filter(tour_slug=delete_slug)

    if not data.exists(): return redirect('/')
    data.delete()
    return redirect('/success/')

    # ERROR HANDLING


def handler_404(request, *args, **argv):
    return render(request, 'not_found.html')


def handler500(request, *args, **argv):
    return render(request, 'Server_Error.html')
