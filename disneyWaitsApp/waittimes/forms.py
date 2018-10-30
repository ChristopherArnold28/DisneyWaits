from django import forms

from .models import UserNotifications

class NotificationForm(forms.ModelForm):

    datestart = forms.DateField(label = "Start Date")
    dateend = forms.DateField(label = "End Date")
    class Meta:
        model = UserNotifications
        fields = ('phonenumber','datestart','dateend',)
        labels = {
            'phonenumber':"Valid US Phone Number"
        }
