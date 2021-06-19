from django.shortcuts import redirect, render
from django.views import generic
from . import views
from .forms import *
from .models import *
import os
from django.conf import settings
from django.http import HttpResponse, Http404

# Create your views here.

def Home(request):

    units = (
            ('lbs.', "lbs."),
            ('oz.', "oz."),
            ('qt.', "qt"),
            ('fl oz.', "fl oz."),
            ('ct.', "count"),
            ('ea', "each"),
            ('sq ft.', "square feet")
        )
        
    multi_dict = {
        'lbs.': (1, "LB"),
        'oz.': (16, "LB"),
        'qt.': (1, "QT"),
        'fl oz.': (32, "QT"),
        'ct.': (100, "100 CT"),
        'ea.': (1, 'EA'),
        'sq ft.': (50, "50 SQ FT")
    }

    form = UnitPriceCalc(request.POST or None)

    context = {
        'form': form
    }
    
    if form.is_valid():
        price = form.cleaned_data['sale_price']
        size = form.cleaned_data['size']
        unit = form.cleaned_data['size_unit']
        multiplier, unit_type = multi_dict[unit]
        unit_price = round(price / size * multiplier, 2)
        context['unit_price'] = str(unit_price) + " PER " + unit_type + "."
        context['math'] = "(" + str(price) + " / " + str(size) + ") x " + str(multiplier) + " = " + str(unit_price)
        context['unit_type'] = unit
        context['unit_type2'] = unit_type
        context['units'] = multiplier



    return render(request, 'signs/home.html', context=context)

from .data import Sign
from relatorio.templates.opendocument import Template
def SignGen(request, signsize):

    context={
        'signsize': signsize
    }

    form = SignInfoFormDollar(request.POST or None)

    units = (
            ('lbs.', "lbs."),
            ('oz.', "oz."),
            ('qt.', "qt"),
            ('fl oz.', "fl oz."),
            ('ct.', "count"),
            ('ea', "each"),
            ('sq ft.', "square feet")
        )
        
    multi_dict = {
        'lbs.': (1, "LB"),
        'oz.': (16, "LB"),
        'qt.': (1, "QT"),
        'fl oz.': (32, "QT"),
        'ct.': (100, "100 CT"),
        'ea.': (1, 'EA'),
        'sq ft.': (50, "50 SQ FT")
    }

    if form.is_valid():
        price = form.cleaned_data['sale_price']
        rr = form.cleaned_data['regular_retail']
        saved = rr - price
        size = form.cleaned_data['size']
        unit = form.cleaned_data['size_unit']
        multiplier, unit_type = multi_dict[unit]
        unit_price = round(price / size * multiplier, 2)
        p1,p2 = divmod(price, 1)
        s1,s2 = divmod(saved, 1)
        p2 = int(round(p2,2) * 100)
        if p2 % 10 == p2:
            p2 = '0' + str(p2)

        temptype = 'D'

        #Checks for whole number or 2 for
        if price - int(price) == 0 or p2 == 50:
            if price == 1:
                temptype = 'T'
            else:
                temptype = 'Q'
                p1 = 2
                p2 = int(price*2)
        # Checks for common quantities
        if p2==33 or p2==66:
            temptype = 'Q'
            p1 = 3
            p2 = int(round(price*3))

        #checks for no sale
        if saved == 0:
            temptype = 'N'
        if form.data['start_date']:
            dating = "ON SALE " + form.cleaned_data['start_date'] + " THRU " + form.cleaned_data['end_date']
        else:
            dating = ""




        sign = Sign(
            title = form.cleaned_data['name'],
            description = str(size) + " " + unit + " - " + form.cleaned_data['description'],
            p1 = int(p1),
            p2 = p2,
            dating = dating,
            s1 = s1,
            s2 = f"{int(round(s2,2) * 100):02}",
            up = unit_price,
            su = "PER " + unit_type + ".",
            wb = form.cleaned_data['when_you_buy'],
            lim = form.cleaned_data['limit'],
            rr = rr
        )

        templatedict = {
            'BD': 'B_dollar_template.odt',
            'CD': 'C_dollar_template.odt',
            'BQ': 'B_quantity_template.odt',
            'CQ': 'C_quantity_template.odt',
            'BT': 'B_ten_for_ten_template.odt',
            'CT': 'C_ten_for_ten_template.odt',
            'BN': 'B_no_sale_template.odt',
            'CN': 'C_no_sale_template.odt',
        }
        basic = Template(source='', filepath=os.path.join(settings.BASE_DIR, 'signs/sign_templates/' + templatedict[signsize + temptype]))
        basic_generated = basic.generate(o=sign).render()
        fo = open("output_sign.odt", "wb")
        fo.write(basic_generated.getvalue())
        fo.close()

        with open("output_sign.odt", 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename("output_sign.odt")
            return response

    context['form']= form
    return render(request, 'signs/signgen.html', context=context)


