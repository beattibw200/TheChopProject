from django import forms
from .models import *
from django.forms import ModelForm

class eCouponForm(forms.Form):
    def __init__(self, *args, **kwargs):

        super(eCouponForm, self).__init__(*args, **kwargs)
        self.fields['username'] = forms.CharField()
        self.fields['password'] = forms.CharField(widget=forms.PasswordInput())


    
class SignTypeForm(forms.Form):

    def __init__(self, *args, **kwargs):

        saletypes = (
            ('q', 'Quantity'),
            ('d', 'Dollar'),
            ('c', 'Cent'),
            ('t', 'Ten for Ten'),
            ('b1', 'Buy 1 Get 1'),
            ('b2', 'Buy 1 Get 2')
        )

        super(SignTypeForm, self).__init__(*args, **kwargs)

        self.fields['size'] = forms.ChoiceField(choices=(('b', "B"), ('c', "C"), ('d', "D")))
        self.fields['on_sale'] = forms.BooleanField(required=False)
        self.fields['price_type'] = forms.ChoiceField(choices=saletypes)

class SignInfoFormDollar(forms.Form):

    def __init__(self, *args, **kwargs):

        units = (
            ('lbs.', "lbs."),
            ('oz.', "oz."),
            ('qt.', "qt"),
            ('fl oz.', "fl oz."),
            ('ct.', "count"),
            ('ea.', "each"),
            ('sq ft.', "square feet")
        )

        super(SignInfoFormDollar, self).__init__(*args, **kwargs)

        self.fields['name'] =forms.CharField()
        self.fields['description']=forms.CharField(required=False)
        self.fields['size'] = forms.DecimalField()
        self.fields['size_unit'] = forms.ChoiceField(choices=units)
        self.fields['regular_retail'] = forms.DecimalField()
        self.fields['sale_price'] = forms.DecimalField()
        self.fields['start_date'] = forms.CharField(required=False)
        self.fields['end_date'] = forms.CharField(required=False)
        self.fields['when_you_buy'] = forms.CharField(required=False)
        self.fields['limit'] = forms.CharField(required=False)

class UnitPriceCalc(forms.Form):

    def __init__(self, *args, **kwargs):

        units = (
            ('lbs.', "lbs."),
            ('oz.', "oz."),
            ('qt.', "qt"),
            ('fl oz.', "fl oz."),
            ('ct.', "count"),
            ('ea', "each"),
            ('sq ft.', "square feet")
        )

        super(UnitPriceCalc, self).__init__(*args, **kwargs)

        self.fields['size'] = forms.DecimalField()
        self.fields['size_unit'] = forms.ChoiceField(choices=units)
        self.fields['sale_price'] = forms.DecimalField()




