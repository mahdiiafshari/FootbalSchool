from django import forms
from .models import Attendance
from django.forms import modelformset_factory



class SingleAttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['status', 'note', 'rating']


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['player', 'status', 'score', 'trainer_note']
        widgets = {
            'player': forms.HiddenInput(),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'trainer_note': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
        }


AttendanceFormSet = modelformset_factory(
    Attendance,
    form=AttendanceForm,
    extra=0,  # No extra empty forms
)

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['player', 'status', 'note', 'rating']
        widgets = {
            'player': forms.HiddenInput(),
        }

