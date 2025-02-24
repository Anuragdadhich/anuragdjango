from django.contrib.auth.models import User
from ship.models import UserProfile

for user in User.objects.all():
    if not hasattr(user, 'userprofile'):
        UserProfile.objects.create(user=user)
print("All missing UserProfiles created!")