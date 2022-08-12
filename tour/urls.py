from django.urls import path
from . views import tour, single_tour,CreateCheckoutSessionView, stripe_webhook,Review_model,booked_secessful, delete_booked_tour
                    
# /delete_booked_tour/{{tour.slug}}
app_name = 'tour'
urlpatterns = [
    
    path('', tour, name='home'),
    path('webhooks/stripe/', stripe_webhook, name='stripe-webhook'),
     
     
    path('success/', booked_secessful , name='success'),
    path('delete_booked_tour/<slug:delete_slug>', delete_booked_tour , name='delete_booking'),
    
    path('review/<slug:review_slug>', Review_model, name='review'),
     
    path('create-checkout-session/<slug:tour_slug>', CreateCheckoutSessionView, name='create-checkout-session'),
    path('<slug:tour_slug>',single_tour),
]