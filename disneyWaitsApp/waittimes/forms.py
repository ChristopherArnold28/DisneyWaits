from django import forms

from .models import UserNotifications
from .models import UserPhonenumber
from registration.forms import RegistrationForm

class NotificationForm(forms.ModelForm):

    datestart = forms.DateField(label = "Start Date")
    dateend = forms.DateField(label = "End Date")
    class Meta:
        model = UserNotifications
        fields = ('datestart','dateend',)

class PhonenumberForm(forms.ModelForm):

    class Meta:
        model = UserPhonenumber
        fields = ('phonenumber',)
        labels = {
            'phonenumber':"Valid US Phone Number"
        }
