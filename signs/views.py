from django.shortcuts import redirect, render
from django.views import generic
from . import views
from .forms import *
from .models import *
import os
from django.conf import settings
from django.http import HttpResponse, Http404

#For eCpn functionality------VVVV
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from getpass import getpass
from termcolor import colored
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver

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

def ecpn(request):

    form = eCouponForm(request.POST or None)
    context = {
        'form': form
    }

    if form.is_valid():

        a = 1

        #run the thing
        options = FirefoxOptions()
        options.add_argument("--headless")
        options.add_argument("window-size=1200x600")
        driver = webdriver.Firefox(options=options)
        print (colored("Welcome to the eCoupon clipper! Please wait while the headless browser loads!", 'blue', attrs=['bold', 'blink']))
        driver.get("https://shop.pricechopper.com/shop/coupons")

        #time.sleep(4)

        delay=10

        try:
            myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'shopping-selector-parent-process-modal-close-click')))
            print("Page is ready!")
        except TimeoutException:
            print("Loading took too much time!")

        if driver.find_element_by_id("shopping-selector-parent-process-modal-close-click"):
            close = driver.find_element_by_id("shopping-selector-parent-process-modal-close-click")
            close.click()

        username_input = form.cleaned_data['username']
        password_input = form.cleaned_data['password']

        try:
            myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'nav-register')))
            print("Home page ready...")
        except TimeoutException:
            print("Loading took too much time!")

        time.sleep(4)

        # login_button = driver.find_element_by_id("nav-register")

        button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'nav-register')))
        button.click()

        #time.sleep(5)

        try:
            myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'login-email')))
            print("Login ready...")
        except TimeoutException:
            print("Loading took too much time!")

        username = driver.find_element_by_id("login-email")
        password = driver.find_element_by_id("login-password")

        username.send_keys(username_input)
        password.send_keys(password_input)

        submit_login_button = driver.find_element_by_id("login-submit")
        submit_login_button.click()

        print("Logged in!")

        print("Loading your eCoupons (10 seconds)...")
        time.sleep(10)

        ecoupon_list = driver.find_elements_by_class_name("button")
        print("eCoupon's Found:")
        out = "<ul>"
        clipt = "<ul>"
        
        clipped = 0
        already = 0
        pages = 1
        for x in ecoupon_list:
            try:
                xs = x.get_attribute("aria-label")
                if isinstance(xs, str) and "Save" in xs:
                    print(xs + " ... ")
                    out = out + "<li>" + xs + " ... "

                    x.click()
                    print("... clipped!")
                    out = out + " clipped!</li>"
                    clipt = clipt + "<li>" + xs + "</li>"
                    clipped+=1
            except:
                print ("... already clipped!")
                out = out + " already clipped!</li>"
                already+=1

        togo = True
        while (togo):
            pages +=1
            count = 0
            try:
                next = driver.find_element_by_css_selector('.pagination-next > button:nth-child(1)')
                next.click()
            except:
                togo=False
                driver.get('https://shop.pricechopper.com/account/loyalty')
                print("...generating totals (sleep 10 seconds)")
                time.sleep(10)
                print (colored("[--------------------------------* eCoupon Totals *--------------------------------]", 'red', attrs=['bold']))
                out = out + "TOTALS:\n"
                #cardnum = driver.find_element_by_css_selector('.css-1fkut6w').text
                #name = driver.find_element_by_css_selector('.css-13l2qj-UserMenu--UserMenu > span:nth-child(2) > span:nth-child(1)').text
                #points  = driver.find_element_by_css_selector('.points-no-increment').text
                #print("\n" + str(name) + ", We successfully clipped " + colored(str(clipped), attrs=['bold']) + " eCoupons to your AdvantEdge card. \nYou already had " + colored(str(already), attrs=['bold']) + " eCoupons clipped! Thats a total of " + colored(str(clipped + already), 'blue', attrs=['bold']) + " eCoupons on your card!")
                out = out + "Clipped " + str(clipped) + " eCoupons to your card.\n" 
                print ("Clipped " + str(clipped) + " eCoupons to your card.")
                if clipped==0:
                    print("You already had all the eCoupons clipped, you should be all set until next Sunday!")
                    clipt = "You already have all the current eCoupons clipped, (or the program crashed, or the Golub Corporation stopped using free well-known css libraries!) you should be all set until next Sunday!"
                #print("\nThe AdvantEdge card we have on file for you is " + colored(str(cardnum), 'red', attrs=['bold']) + ".")
                #out = out + "The AdvantEdge card on file is " + str(cardnum) + ".\n"
                #print("Also, " + colored(str(points), 'cyan', attrs=['bold']) + "!\n")
                #out = out + str(points)

                driver.close()
                return render(request, 'signs/clipped.html', context=context)

            print('Checking for page ' + str(pages) + '...')
            time.sleep(4)

            ecoupon_list = driver.find_elements_by_class_name("button")
            for x in ecoupon_list:
                try:
                    xs = x.get_attribute("aria-label")
                    if isinstance(xs, str) and "Save" in xs:
                        count+=1
                        print(xs + " ... ")

                        x.click()
                        print(xs + "..." + " clipped!")
                        clipped+=1
                except:
                    print ("... already clipped!")
                    already+=1
            togo = count != 0
            driver.get('https://shop.pricechopper.com/account/loyalty')
            print("...generating totals...")
            time.sleep(5)
            print (colored("[--------------------------------* eCoupon Totals *--------------------------------]", 'red', attrs=['bold']))
            out = out + "</ul>"
            out2 =  ""
            cardnum = driver.find_element_by_css_selector('.css-1fkut6w').text
            name = driver.find_element_by_css_selector('.css-13l2qj-UserMenu--UserMenu > span:nth-child(2) > span:nth-child(1)').text
            points  = driver.find_element_by_css_selector('.points-no-increment').text
            print("\n" + str(name) + ", We successfully clipped " + colored(str(clipped), attrs=['bold']) + " eCoupons to your AdvantEdge card. \nYou already had " + colored(str(already), attrs=['bold']) + " eCoupons clipped! Thats a total of " + colored(str(clipped + already), 'blue', attrs=['bold']) + " eCoupons on your card!")
            out2 = out2 + "<p> Clipped <strong>" + str(clipped) + "</strong> eCoupons to your card. </p>" 
            if clipped==0:
                print("You already had all the eCoupons clipped, you should be all set until next Sunday!")
                clipt = "<p> You already have all the current eCoupons clipped, (or the program crashed, or the Golub Corporation stopped using free well-known css libraries!) you should be all set until next Sunday!</p>"
            print("\nThe AdvantEdge card we have on file for you is " + colored(str(cardnum), 'red', attrs=['bold']) + ".")
            out2 = out2 + "<p> The AdvantEdge card on file is " + str(cardnum) + ".</p>"
            print("Also, " + colored(str(points), 'cyan', attrs=['bold']) + "!\n")
            out2 = out2 + "<a>" + str(points) + "</a>"

            driver.close()
            togo=False
            context['output'] = out
            context['totals'] = out2
            context['output_clipped'] = clipt
            return render(request, 'signs/clipped.html', context=context)

    
    return render(request, 'signs/ecpn.html', context=context)