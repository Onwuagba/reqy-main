from django import forms
from .models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class RegForm(forms.Form):
    # name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter your firstname and lastname'}))
    # email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Enter your email'}))
    # number = forms.CharField(label='Phone Number', max_length=18, widget=forms.NumberInput(attrs={'class':'form-control','placeholder':'Enter your phone number','type':'tel'}))
    # password = forms.CharField(max_length=23, widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Enter your password'}))

    name = forms.CharField()
    email = forms.EmailField()
    number = forms.CharField(required=False)
    password = forms.CharField(max_length=23, widget=forms.PasswordInput(attrs={'placeholder':'Enter your password',}))

    class Meta:
        model = User

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = '#'
        self.helper.form_class = 'authForm'
        self.helper.form_tag = 'novalidate'
        self.helper.attrs = {
            'novalidate':'novalidate'
        }
        self.fields['password'].help_text = "Password must be at least 8 characters long"
        self.helper.add_input(Submit('submit', 'Create Account', css_class='btn btn-az-primary btn-block'))
