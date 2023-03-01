from django.contrib import admin

from users.models import UserAccount, UserSubscription, Subscriptions

# Register your models here.
admin.site.register(UserAccount)
admin.site.register(Subscriptions)
admin.site.register(UserSubscription)

