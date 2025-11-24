# users/admin.py
from django.contrib import admin
from django.contrib.auth.models import Group
# optional: import Profile if you created it
try:
    from .models import Profile
except Exception:
    Profile = None

if Profile:
    @admin.register(Profile)
    class ProfileAdmin(admin.ModelAdmin):
        list_display = ("user", "phone", "role")
        search_fields = ("user__username", "user__email", "phone")

# show groups in admin (default)
admin.site.unregister(Group)
admin.site.register(Group)
