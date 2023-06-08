from email import message
from urllib.request import Request
from django.shortcuts import render, redirect
import employee_web
import staff_admin
from .helpers import *
from django.utils.html import strip_tags
from .models import *
from staff_admin.models import *
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login as login_check
from django.contrib.auth.models import User, auth
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
import pgeocode
from geopy.geocoders import Nominatim
from django.contrib.auth.hashers import MD5PasswordHasher, make_password
from django.core.mail import send_mail
from staff_admin.helpers import generateOTP
from applicant_web.models import *
from django.core.files.storage import FileSystemStorage
from datetime import datetime
from dateutil import parser
from allauth.socialaccount.models import SocialAccount
import geopandas
from django.conf import Settings, settings
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .push_notifications import *
from .helpers import *
from_mail = settings.EMAIL_HOST_USER



User = get_user_model()
from staff_app import helpers
# Create your views here.
from staff_app.helpers import *

def home(request): 
    try:
        us = SocialAccount.objects.get(user_id=request.user.id)
        u = User.objects.get(id=us.user_id)
        u.roll = "employer"
        u.fname = u.first_name
        u.lname = u.last_name
        u.save()
        if u.company_profile_status == False:
            messages.error(request, "Please Fill Your Company Profile ")
            return redirect("/profile/company-profile/" + u.slug)
        else:
            pass
    except:

        pass

    try:
        section1 = pages.objects.get(id=1)
    except:
        section1 = None
    try:
        section2 = pages.objects.get(id=2)
    except:
        section2 = None
    try:
        section3 = pages.objects.get(id=3)
    except:
        section3 = None
    try:
        section4 = pages.objects.get(id=4)
    except:
        section4 = None
    try:
        section5 = pages.objects.get(id=5)
    except:
        section5 = None
    try:
        section6 = pages.objects.get(id=6)
    except:
        section6 = None
    try:
        section7 = pages.objects.get(id=7)
    except:
        section7 = None
    try:
        section8 = pages.objects.get(id=8)
    except:
        section8 = None

    # section4 = pages.objects.get(id=4)
    # section5 = pages.objects.get(id=5)
    # section6 = pages.objects.get(id=6)
    # section7 = pages.objects.get(id=7)

    # p = pages.objects.get(id=1)
    # p2 = pages.objects.get(id=2)

    # section4 = pages.objects.get(id=6)
    # section5 = pages.objects.get(id=7)
    qr_code = Qr_Code.objects.all()
    # modelRe = 0
    # if(request.session.get('app')=="applicant"):
    #     modelRe = 1
    #     request.session['app']='applicant2'
    total_Notification = Notification.objects.filter(user_id=request.user.id).count()
    print(total_Notification, "ffffffffffffffffffffffffffff")
    return render(
        request,
        "dashboard/index.html",
        {
            "qr_code": qr_code,
            "section1": section1,
            "section2": section2,
            "section3": section3,
            "section4": section4,
            "section5": section5,
            "section6": section6,
            "section7": section7,
            "section8": section8,
            "total_Notification": total_Notification
            # "modelRe": modelRe,
        },
    )



def showFirebaseJS(request):
    data='importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-app.js");' \
         'importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-messaging.js"); ' \
         'var firebaseConfig = {' \
        'apiKey: "AIzaSyD2dPJNRlJJ3TFMtmS6fYuMA7CzJqp9axU",'\
        'authDomain: "care-82c4a.firebaseapp.com",'\
        'databaseURL: "",'\
        'projectId: "care-82c4a",'\
        'storageBucket: "care-82c4a.appspot.com",'\
        'messagingSenderId: "787949823984",'\
        'appId: "1:787949823984:web:a01d2654ec4eeb789d1f35",'\
        'measurementId: "G-1W7LGYK7SF"'\
         ' };' \
         'firebase.initializeApp(firebaseConfig);' \
         'const messaging=firebase.messaging();' \
         'messaging.setBackgroundMessageHandler(function (payload) {' \
         '    console.log(payload);' \
         '    const notification=JSON.parse(payload);' \
         '    const notificationOption={' \
         '        body:notification.body,' \
         '        icon:notification.icon' \
         '    };' \
         '    return self.registration.showNotification(payload.notification.title,notificationOption);' \
         '});'
    return HttpResponse(data,content_type="text/javascript")


def Contact(request):
    try:
        us = SocialAccount.objects.get(user_id=request.user.id)
        u = User.objects.get(id=us.user_id)
        u.roll = "employer"
        u.fname = u.first_name
        u.lname = u.last_name
        u.save()
             
        if u.company_profile_status == False:
            messages.error(request, "Please Fill Your Company Profile ")
            return redirect("/profile/company-profile/" + u.slug)
        else:
            pass

    except:
        pass
    if request.method == "POST":
        first_name = request.POST.get("fname")
        last_name = request.POST.get("lname")
        email = request.POST.get("email")
        subject = request.POST.get("sub")
        message = request.POST.get("message")

        contact = ContactUs.objects.create(
            First_name=first_name,
            sub=subject,
            Last_name=last_name,
            email=email,
            message=message,
        )
        contact.save()
        try:
            admins = User.objects.filter(is_staff = True)
            for admin in admins:
                fcm_token = admin.web_fcm_token
                send_push_notification(fcm_token, "Carenet Inquiry", message)
        except:
            pass  
        WebNotification.objects.create(sender_name = f"{first_name} {last_name}", title= "Inquiry" , message=message)

        return JsonResponse(
            {"status": "success", "message": "Details Submitted Successfully !!!!"},
            status=200,
        )
    else:
        return JsonResponse(
            {"status": "error", "message": "No Details Saved !!!!"}, status=200
        )


def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("pass")
        u = User.objects.filter(roll="employer")
        try:
            v = User.objects.get(email=email)

        except:
            v = None
        request.session["email"] = email
        user = auth.authenticate(email=email, password=password)
        if user is None:
            messages.error(request, "invalid username or password ")
            return redirect("/login/")
        # if user:
        #     messages.error(request, "invalid username or password ")
        #     return redirect("/login/")

        if user.roll == "applicant":
            messages.error(request, "Please login from mobile application !!!")
            return redirect("/login/")

        if user.roll == "employer":
            try:
                # em = email_templates.objects.get(id=3)
                # otp = generateOTP()
                # v.OTP = otp
                # v.save()
                # send_to = [email]
                # subject = em.sub

                # content = em.content

                # t = strip_tags(content)
                # c = t.replace("{name}", v.first_name + "" + v.last_name)
                # msg = c.replace("{OTP}", otp)
                # sendMail(subject, msg, send_to)
                # to = ["447912123799"]
                # text = "Your otp Is :" + otp
                # sendsms(to, text)
                if user.email_verified == False:
                    # auth.logout(request)
                    messages.error(request, "Please verify your link on Mail")

                    return redirect("/login/")
                if user.user_status == "0":
                    # auth.logout(request)

                    messages.error(
                        request, "Your account is under verification by Admin"
                    )

                    return redirect("/login/")

                if user.user_status == "2":
                    messages.error(request, "Permission denied")

                    return redirect("/login/")
                if user.company_profile_status == True:
                    auth.login(request, user)
                    return redirect("/")

                elif user.company_profile_status == False:
                    messages.error(request, "Please Fill Company information !!!")
                    return redirect("/profile/company-profile/" + v.slug)
                messages.success(request, "OTP Sent Successfully !!!")
                return redirect("/login/" + v.slug)
            except:
                em = None
                messages.error(request, "Something Went Wrong")
                return redirect("/login/otp/" + v.slug)

        if user.roll == "employer " is None:
            messages.error(request, "invalid username or password ")
            return redirect("/login/")

    return render(request, "employer/auth/login.html")


def login_otp(request, slug):
    try:
        user = User.objects.get(slug=slug)
        if request.method == "POST":
            otp1 = request.POST.get("otp1")
            otp2 = request.POST.get("otp2")
            otp3 = request.POST.get("otp3")
            otp4 = request.POST.get("otp4")
            Otp = str(otp1) + str(otp2) + str(otp3) + str(otp4)

            if Otp == user.OTP:
                if user.user_status == True:
                    # auth.logout(request)
                    messages.error(request, "Permission denied")

                    return redirect("/login/")
                if user.company_profile_status == True:

                    auth.login(request, user)
                    return redirect("/")

                elif user.company_profile_status == False:

                    return redirect("/profile/company-profile/" + slug)
                else:
                    messages.success(request, user.first_name, "Login Successfully")
                    auth.login(request, user)
                    return redirect("/")
            else:
                messages.error(request, "Otp does not match")
                return redirect("/login/otp/" + slug)
        return render(request, "employer/auth/login-otp.html", {"user": user})
    except:
        messages.error(request, "Otp does not match")
        return redirect("/login/otp/" + slug)


def resend_otp(request, slug):
    try:
        m = User.objects.get(OTP_string=slug)
        em = email_templates.objects.get(id=3)
        print(em, "dddddddddddddddddddddddddddddddddd")
        o = generateOTP()
        m.OTP = o
        m.save()
        send_to = [m.email]
        subject = em.sub
        content = em.content
        otp = o
        name = m.first_name + " " + m.last_name
        t = strip_tags(content)
        c = t.replace("{name}", name)
        msg = c.replace("{OTP}", otp)
        # to = ["447912123799"]
        # text = "Your otp Is :" + otp
        sendMail(subject, msg, send_to)
        # sendsms(to, text)

        messages.success(request, "Otp sent successfully")

        return redirect("/verifyotp/" + slug)
    except:
        messages.error(request, "Something went wrong")
        return redirect("/verifyotp/" + slug)


def logout(request):
    auth.logout(request)
    return redirect("/login/")


def about_us(request):
    try:
        us = SocialAccount.objects.get(user_id=request.user.id)
        u = User.objects.get(id=us.user_id)
        u.roll = "employer"
        u.fname = u.first_name
        u.lname = u.last_name
        u.save()
        if u.company_profile_status == False:
            messages.error(request, "Please Fill Your Company Profile ")
            return redirect("/profile/company-profile/" + u.slug)
        else:
            pass

    except:
        pass
    team = meet_our_team.objects.all()
    about_section_1 = AboutUs.objects.get(id=1)
    about_section_2 = AboutUs.objects.get(id=2)
    # about_section_3 = AboutUs.objects.get(id=3)

    total_Notification = Notification.objects.filter(user_id=request.user.id).count()
    return render(
        request,
        "employer/emp_pages/about-us.html",
        {
            "about_section_1": about_section_1,
            "about_section_2": about_section_2,
            "team": team,
            "total_Notification": total_Notification,
        },
    )


def emp_country_ajax(request):
    country = request.POST.get("select_country")
    state = States.objects.filter(country_id=country).values()
    if state is None:
        return JsonResponse(
            {"status": "error", "message": " no changed !!!!"}, status=200
        )
    else:

        return JsonResponse(
            {"status": "success", "message": "changed !!!!", "result": list(state)},
            status=200,
        )


def emp_state_city_ajax(request):
    state = request.POST.get("state_value")
    city = Cities.objects.filter(state_id=state).values()
    if city is None:
        return JsonResponse(
            {"status": "error", "message": " no changed !!!!"}, status=200
        )
    else:

        return JsonResponse(
            {"status": "success", "message": "changed !!!!", "result": list(city)},
            status=200,
        )


def emp_postal_code_ajax(request):
    postal_code = request.POST.get("postal_code")
    geolocator = Nominatim(user_agent="geoapiExercises")
    zipcode = postal_code
    location = geolocator.geocode(zipcode)
    nomi = pgeocode.Nominatim("fr")
    return JsonResponse(
        {"status": "error", "message": " no changed !!!!", "location": list(location)},
        status=200,
    )


# def qr_code(request):
#
#     print(qr_code,"gggggggggggggggggggggggggggggggggggggggg")
#     return render(request, 'index.html',{'qr_code':qr_code})


def forgotpassword(request):
    try:
        if request.method == "POST":
            email = request.POST.get("email")
            request.session["email"] = email
            try:
                m = User.objects.get(email=email)
                em = email_templates.objects.get(id=3)
                if m.roll == "applicant":
                    messages.error(
                        request, "Staff Does Not Have Permission for forgot password"
                    )
                    print("noooooooo found")
                    return redirect("/forgotpassword/")
                if m.roll == "employer":
                    o = generateOTP()
                    us = hash(o)
                    m.OTP_string = us
                    m.OTP = o
                    m.save()

                    send_to = [email]

                    subject = em.sub
                    content = em.content

                    otp = o
                    name = m.first_name + " " + m.last_name
                    t = strip_tags(content)
                    c = t.replace("{name}", name)
                    msg = c.replace("{OTP}", otp)
                    # to = ["447912123799"]
                    # text = "Your otp Is :" + otp
                    sendMail(subject, msg, send_to)
                    # sendsms(to, text)

                    return redirect("/verifyotp/" + str(us))
                else:
                    messages.error(request, "Email Does Not Exits")
                    print("noooooooo found")
                    return redirect("/forgotpassword/")
            except:
                messages.error(request, "Email is not exist")
                return redirect("/forgotpassword/")

    except:
        messages.error(request, "Email is not exist")
        return redirect("/forgotpassword/")

    return render(request, "employer/auth/forgot-password.html")


def verify_otp(request, slug):
    m = User.objects.get(OTP_string=slug)
    if request.method == "POST":
        otp1 = request.POST.get("otp1")
        otp2 = request.POST.get("otp2")
        otp3 = request.POST.get("otp3")
        otp4 = request.POST.get("otp4")
        Otp = str(otp1) + str(otp2) + str(otp3) + str(otp4)

        if m.OTP == Otp:

            return redirect("/passwordresetform/" + slug)
        else:
            print("not match")
            messages.error(request, "Otp does not match")
            return redirect("/verifyotp/" + slug)

    return render(request, "employer/auth/forgot-otp.html", {"m": m})


def passwordresetform(request, slug):

    if request.method == "POST":
        new_password = request.POST.get("new-password")
        confirm_password = request.POST.get("confirm-new-password")
        if new_password is None:
            messages.error(request, "Please Fill Password ")
            return redirect("passwordresetform")
        elif new_password == confirm_password:
            m = User.objects.filter(OTP_string=slug).update(
                password=make_password(new_password)
            )

            messages.success(request, "Password Changed Successfully")
            return redirect("/login/")
        else:

            return redirect("passwordresetform")
    return render(request, "employer/auth/reset-password-form.html")


def user_profile(request, slug):
    try:
        user_obj = User.objects.get(id = request.user.id)
        company_obj = CompanyInfo.objects.get(user_slug = user_obj.slug)
        if not user_obj.post_code:
            user_obj.post_code = company_obj.post_code
            user_obj.address = company_obj.address
            user_obj.address2 = company_obj.address2
            user_obj.country = company_obj.country
            user_obj.city = company_obj.city
            user_obj.save()
    except:
        pass  
    try:
        us = SocialAccount.objects.get(user_id=request.user.id)
        u = User.objects.get(id=us.user_id)
        u.roll = "employer"
        u.fname = u.first_name
        u.lname = u.last_name
        u.save()
        if u.company_profile_status == False:
            messages.error(request, "Please Fill Your Company Profile ")
            return redirect("/profile/company-profile/" + u.slug)
        else:
            pass

    except:
        pass
          
    if request.method == "POST":
        slug = request.POST.get("slug")
        company = request.POST.get("Cname")
        image = request.FILES.get("image")
        gender = request.POST.get("gender")
        first_name = request.POST.get("Fname")
        last_name = request.POST.get("Lname")
        mobile_number = request.POST.get("mob_num")
        post_code = request.POST.get("Postal_code")
        address = request.POST.get("address")
        address2 = request.POST.get("address2")
        country = request.POST.get("country")
        city = request.POST.get("city")
        lat = request.POST.get("latitude")
        long = request.POST.get("longitude")
    

        users = User.objects.get(slug=request.user.slug)
        if image:
            image_del = users.image
            image_del.delete()
            users.slug = slug
            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            users.image = image
            users.gender = gender
            users.company = company
            users.fname = first_name
            users.lname = last_name
            users.mobile_number = mobile_number
            users.post_code = post_code
            users.address = address
            users.address2 = address2
            users.country = country
            users.city = city
         
            users.latitude = lat
    
            users.longitude = long
            users.save()
        else:
            users.slug = slug
            users.gender = gender
            users.company = company
            users.fname = first_name
            users.lname = last_name
            users.mobile_number = mobile_number
            users.post_code = post_code
            users.address = address
            users.address2 = address2
            users.country = country
            users.city = city
            users.latitude = lat
            users.longitude = long
            users.save()

        messages.success(request, "Profile Update successfully")
        return redirect("/profile/" + slug)
    else:
        try:
            user = User.objects.get(slug=request.user.slug)
            users = CompanyInfo.objects.get(user_id=user.id)
            users.user_slug = user.slug
            users.save()

        except:
            users = None
            messages.error(request, "Admin Do not Have Company InFo")
            return redirect("/")
    total_Notification = Notification.objects.filter(user_id=request.user.id).count()

    return render(
        request,
        "userprofile/profile.html",
        {
            "user": user,
            "slug": slug,
            "postal_key": settings.POSTAL_KEY,
            "total_Notification": total_Notification,
        },
    )

    # print(users.user_slug, "ffffffffffffffffffffffffff")
    # except:
    #     messages.error(request, 'Some Went Wrong')
    #     return redirect('/profile/')


def update_company_profile(request, user_slug):
    user = User.objects.get(slug=user_slug)

    if request.method == "POST":
        per_name = request.POST.get("P_Solename")
        per_name2 = request.POST.get("P_Partnershipname")
        company_name = request.POST.get("Cname")
        contact_name = request.POST.get("Contact_name")

        phone_number = request.POST.get("mob_num")

        fax = request.POST.get("fax")
        Postal_code = request.POST.get("base_Postal_code")
        email = request.POST.get("email")
        address = request.POST.get("Address")
        address2 = request.POST.get("Address2")
        country = request.POST.get("country")
        city = request.POST.get("city")
        year_in_bussiness = request.POST.get("year_in_bussiness")
        sole_trador = request.POST.get("sole")
        partnership = request.POST.get("partnership")
        limited_company = request.POST.get("limited_company")
        limited_company_partnership = request.POST.get("limited_company_partnership")
        redio = request.POST.get("propertytype")
        tax = request.POST.get("tax")
        lat = request.POST.get("latitude")
        long = request.POST.get("longitude")

        prefrence_company_name = request.POST.get("Cname1")

        prefrence_Contact_name = request.POST.get("Contact_name1")
        prefrence_phone_number = request.POST.get("mob_num1")

        prefrence_email = request.POST.get("email1")

        prefrence_Postal_code = request.POST.get("Postal_code1")

        prefrence_Address1 = request.POST.get("Address1")

        prefrence_Address2_1 = request.POST.get("Address2_1")

        prefrence_country = request.POST.get("country1")

        prefrence_city = request.POST.get("city1")

        prefrence_lat = request.POST.get("prefrence_lat")

        prefrence_long = request.POST.get("prefrence_long")

        prefrence_company_name2 = request.POST.get("Cname2")
        prefrence_Contact_name2 = request.POST.get("Contact_name2")

        prefrence_phone_number2 = request.POST.get("mob_num2")

        prefrence_email2 = request.POST.get("email2")

        prefrence_Postal_code2 = request.POST.get("Postal_code2")

        prefrence_Address2 = request.POST.get("Address2")

        prefrence_Address2_2 = request.POST.get("Address2_2")

        prefrence_country2 = request.POST.get("country2")

        prefrence_city2 = request.POST.get("city2")

        prefrence_lat2 = request.POST.get("prefrence_lat2")

        prefrence_long2 = request.POST.get("prefrence_long2")
        print(prefrence_Address2_2, "dddddddddddddddddddddd")

        if redio == "1":
            users = CompanyInfo.objects.filter(user_id=user.id).update(
                proprietor_name=per_name,
                phone_number=phone_number,
                contact_name=contact_name,
                fax=fax,
                email=email,
                address=address,
                address2=address2,
                year_of_business=year_in_bussiness,
                # registration_num=sole_trador,
                partnership=redio,
                tax=tax,
                post_code=Postal_code,
                country=country,
                city=city,
                latitude=lat or "0",
                longitude=long or "0",
                prefrence_business_name_1=prefrence_company_name,
                prefrence1_postcode=prefrence_Postal_code,
                prefrence_contact_name_1=prefrence_Contact_name,
                prefrence_phone_number_1=prefrence_phone_number,
                prefrence_email_1=prefrence_email,
                prefrence_country_1=prefrence_country,
                prefrence_city_1=prefrence_city,
                prefrence1_latitude=prefrence_lat or "0",
                prefrence1_longitude=prefrence_long or "0",
                prefrence1_address=prefrence_Address1,
                prefrence1_address2=prefrence_Address2_1,
                prefrence_business_name_2=prefrence_company_name2,
                prefrence2_postcode=prefrence_Postal_code2,
                prefrence_contact_name_2=prefrence_Contact_name2,
                prefrence_phone_number_2=prefrence_phone_number2,
                prefrence_email_2=prefrence_email2,
                prefrence_country_2=prefrence_country2,
                prefrence_city_2=prefrence_city2,
                prefrence2_latitude=prefrence_lat2 or "0",
                prefrence2_longitude=prefrence_long2 or "0",
                prefrence2_address=prefrence_Address2,
                prefrence2_address2=prefrence_Address2_2,
            )

            user.company_profile_status = True
            user.save()
            messages.success(request, "Company details saved succssfully !!!! ")
            return redirect("/client/company-profile/" + user_slug)
        elif redio == "2":
            users = CompanyInfo.objects.filter(user_id=user.id).update(
                user_id=user.id,
                proprietor_name=per_name2,
                contact_name=contact_name,
                phone_number=phone_number,
                fax=fax,
                email=email,
                post_code=Postal_code,
                country=country,
                city=city,
                address=address,
                address2=address2,
                year_of_business=year_in_bussiness,
                # registration_num=partnership,
                partnership=redio,
                tax=tax,
                latitude=lat or "0",
                longitude=long or "0",
                prefrence_business_name_1=prefrence_company_name,
                prefrence1_postcode=prefrence_Postal_code,
                prefrence_contact_name_1=prefrence_Contact_name,
                prefrence_phone_number_1=prefrence_phone_number,
                prefrence_email_1=prefrence_email,
                prefrence_country_1=prefrence_country,
                prefrence_city_1=prefrence_city,
                prefrence1_latitude=prefrence_lat or "0",
                prefrence1_longitude=prefrence_long or "0",
                prefrence1_address=prefrence_Address1,
                prefrence1_address2=prefrence_Address2_1,
                prefrence_business_name_2=prefrence_company_name2,
                prefrence2_postcode=prefrence_Postal_code2,
                prefrence_contact_name_2=prefrence_Contact_name2,
                prefrence_phone_number_2=prefrence_phone_number2,
                prefrence_email_2=prefrence_email2,
                prefrence_country_2=prefrence_country2,
                prefrence_city_2=prefrence_city2,
                prefrence2_latitude=prefrence_lat2 or "0",
                prefrence2_longitude=prefrence_long2 or "0",
                prefrence2_address=prefrence_Address2,
                prefrence2_address2=prefrence_Address2_2,
            )

            user.company_profile_status = True
            user.save()
            messages.success(request, "Company details saved succssfully !!!! ")
            return redirect("/client/company-profile/" + user_slug)
        elif redio == "3":
            users = CompanyInfo.objects.filter(user_id=user.id).update(
                user_id=user.id,
                company_name=company_name,
                contact_name=contact_name,
                phone_number=phone_number,
                fax=fax,
                email=email,
                address=address,
                post_code=Postal_code,
                country=country,
                city=city,
                address2=address2,
                year_of_business=year_in_bussiness,
                registration_num=limited_company,
                partnership=redio,
                tax=tax,
                latitude=lat or "0",
                longitude=long or "0",
                prefrence_business_name_1=prefrence_company_name,
                prefrence1_postcode=prefrence_Postal_code,
                prefrence_contact_name_1=prefrence_Contact_name,
                prefrence_phone_number_1=prefrence_phone_number,
                prefrence_email_1=prefrence_email,
                prefrence_country_1=prefrence_country,
                prefrence_city_1=prefrence_city,
                prefrence1_latitude=prefrence_lat or "0",
                prefrence1_longitude=prefrence_long or "0",
                prefrence1_address=prefrence_Address1,
                prefrence1_address2=prefrence_Address2_1,
                prefrence_business_name_2=prefrence_company_name2,
                prefrence2_postcode=prefrence_Postal_code2,
                prefrence_contact_name_2=prefrence_Contact_name2,
                prefrence_phone_number_2=prefrence_phone_number2,
                prefrence_email_2=prefrence_email2,
                prefrence_country_2=prefrence_country2,
                prefrence_city_2=prefrence_city2,
                prefrence2_latitude=prefrence_lat2 or "0",
                prefrence2_longitude=prefrence_long2 or "0",
                prefrence2_address=prefrence_Address2,
                prefrence2_address2=prefrence_Address2_2,
            )

            user.company_profile_status = True
            user.save()
            messages.success(request, "Company details saved succssfully !!!! ")
            return redirect("/client/company-profile/" + user_slug)
        else:
            users = CompanyInfo.objects.filter(user_id=user.id).update(
                user_id=user.id,
                company_name=company_name,
                contact_name=contact_name,
                phone_number=phone_number,
                fax=fax,
                email=email,
                address=address,
                post_code=Postal_code,
                country=country,
                city=city,
                address2=address2,
                year_of_business=year_in_bussiness,
                registration_num=limited_company_partnership,
                partnership=redio,
                tax=tax,
                latitude=lat or "0",
                longitude=long or "0",
                prefrence_business_name_1=prefrence_company_name,
                prefrence1_postcode=prefrence_Postal_code,
                prefrence_contact_name_1=prefrence_Contact_name,
                prefrence_phone_number_1=prefrence_phone_number,
                prefrence_email_1=prefrence_email,
                prefrence_country_1=prefrence_country,
                prefrence_city_1=prefrence_city,
                prefrence1_latitude=prefrence_lat or "0",
                prefrence1_longitude=prefrence_long or "0",
                prefrence1_address=prefrence_Address1,
                prefrence1_address2=prefrence_Address2_1,
                prefrence_business_name_2=prefrence_company_name2,
                prefrence2_postcode=prefrence_Postal_code2,
                prefrence_contact_name_2=prefrence_Contact_name2,
                prefrence_phone_number_2=prefrence_phone_number2,
                prefrence_email_2=prefrence_email2,
                prefrence_country_2=prefrence_country2,
                prefrence_city_2=prefrence_city2,
                prefrence2_latitude=prefrence_lat2 or "0",
                prefrence2_longitude=prefrence_long2 or "0",
                prefrence2_address=prefrence_Address2,
                prefrence2_address2=prefrence_Address2_2,
            )
            user.company_profile_status = True
            user.save()
            messages.success(request, "Company details saved succssfully !!!! ")
            return redirect("/client/company-profile/" + user_slug)

    company = CompanyInfo.objects.get(user_slug=user_slug)
    total_Notification = Notification.objects.filter(user_id=request.user.id)
    return render(
        request,
        "userprofile/update_user_company_profile1.html",
        {
            "company": company,
            "postal_key": settings.POSTAL_KEY,
            "total_Notification": total_Notification,
        },
    )


# def manage_shift(request):
#     return render(request , 'manage-shifts.html')


# def time_sheet(request):
#     return render(request, 'time-sheet.html')


@login_required(login_url="/login/")
def notifications(request):
    try:
        usr = request.user
        notification_obj = Notification.objects.filter(user_id=request.user.id)
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        x = 0
        l = list()
        d = dict()
        notification = list()
        c = 0
        for i in notification_obj:
            if c == 0:
                x = i.create_at.date()
                d["date"] = x
                msg = {}

                msg["message"] = i.msg.message
                msg["time"] = i.create_at.time()
                msg["post_id"] = i.msg.post_id
                msg["in_time"] = i.msg.post_startdate
                msg["out_time"] = i.msg.post_enddate
                l.append(msg)
                c += 1

            elif x == i.create_at.date():
                msg = {}
                msg["message"] = i.msg.message
                msg["time"] = i.create_at.time()
                msg["post_id"] = i.msg.post_id
                msg["in_time"] = i.msg.post_startdate
                msg["out_time"] = i.msg.post_enddate
                l.append(msg)
                c += 1
                if c == len(notification_obj):
                    d["message"] = l
                    notification.append(d)

            elif x != i.create_at.date():
                d["message"] = l
                notification.append(d)
                d = dict()
                l = list()
                x = i.create_at.date()
                d["date"] = x
                msg = {}
                msg["message"] = i.msg.message
                msg["time"] = i.create_at.time()
                msg["post_id"] = i.msg.post_id
                msg["in_time"] = i.msg.post_startdate
                msg["out_time"] = i.msg.post_enddate
                l.append(msg)
                c += 1
                notification.append(d)

    except:
        pass
    try:
        us = SocialAccount.objects.get(user_id=request.user.id)
        u = User.objects.get(id=us.user_id)
        u.roll = "employer"
        u.fname = u.first_name
        u.lname = u.last_name
        u.save()
        if u.company_profile_status == False:
            messages.error(request, "Please Fill Your Company Profile ")
            return redirect("/profile/company-profile/" + u.slug)
        else:
            pass

    except:
        pass
    total_Notification = Notification.objects.filter(user_id=request.user.id).count()

    return render(
        request,
        "notification/notifications.html",
        {
            "notification": notification,
            "today": today.date(),
            "yesterday": yesterday.date(),
            "total_Notification": total_Notification,
        },
    )


def notifications_setting(request):
    try:
        us = SocialAccount.objects.get(user_id=request.user.id)
        u = User.objects.get(id=us.user_id)
        u.roll = "employer"
        u.fname = u.first_name
        u.lname = u.last_name
        u.save()
        if u.company_profile_status == False:
            messages.error(request, "Please Fill Your Company Profile ")
            return redirect("/profile/company-profile/" + u.slug)
        else:
            pass

    except:
        pass
    total_Notification = Notification.objects.filter(user_id=request.user.id).count()
    return render(
        request,
        "notification/notification-settings.html",
        {"total_Notification": total_Notification},
    )


def no_notifications(request):
    try:
        us = SocialAccount.objects.get(user_id=request.user.id)
        u = User.objects.get(id=us.user_id)
        u.roll = "employer"
        u.fname = u.first_name
        u.lname = u.last_name
        u.save()
        print(u.company_profile_status, "fffffffffffffffffffffffffffffffffffff")
        if u.company_profile_status == False:
            messages.error(request, "Please Fill Your Company Profile ")
            return redirect("/profile/company-profile/" + u.slug)
        else:
            pass

    except:
        pass
    total_Notification = Notification.objects.filter(user_id=request.user.id).count()
    return render(
        request,
        "notification/no-notifications.html",
        {"total_Notification": total_Notification},
    )


def app_sign_up(request):

    cat = Category.objects.filter(status=1)
    country = Country.objects.all()
    year = list(range(0, 15))
    month = list(range(0, 13))
    year_lists = []
    month_lists = []

    for i in year:
        year_lists.append(i)
    for i in month:
        month_lists.append(i)

    return render(
        request,
        "applicant/sign-up-applicants.html",
        {
            "cat": cat,
            "country": country,
            "l": year_lists,
            "m": month_lists,
            "postal_key": settings.POSTAL_KEY,
        },
    )


def app_data_ajax(request):
    if request.method == "POST":
        last_name = request.POST.get("LName")
        first_name = request.POST.get("FName")
        mobile_number = request.POST.get("mob_num")
        email = request.POST.get("email")
        position = request.POST.get("position")
        password = request.POST.get("password")
        re_password = request.POST.get("rePassword")
        user_type = request.POST.get("user_type")
        referral_code = generate_referal_code(user_type)
        phone = mobile_number.split(" ")[1]
        code = mobile_number.split(" ")[0]
        # id = request.POST.get("id")
        # distance = request.POST.get("select_range")
        # print(latitude,"ddddddddddddddd")
        # longitude = request.POST.get('longitude')
        # landline = request.POST.get("land_line")
        # experience = request.POST.get("experience")
        # country = request.POST.get("country")
        # state = request.POST.get("state")
        # city = request.POST.get("city")
        # postal = request.POST.get("postal_code")
        # address = request.POST.get("address")

        # year = request.POST.get("year") 
        # month = request.POST.get("month")
        # address2 = request.POST.get("address2")
        # df = geopandas.tools.geocode(postal)

        # try:
        #     df["lon"] = df["geometry"].x
        #     df["lat"] = df["geometry"].y
        #     lat = df["lat"]
        #     long = df["lon"]

        # except:
        #     return JsonResponse(
        #         {"status": "error", "message": " Please select valid post code !!!!"},
        #         status=404,
        #     )

        if "@" and "." not in email:
            return JsonResponse(
                {"status": "error", "message": "Invalid Email address !!!!"},
                status=404,
            )

        if user_type == "applicant":
            em = email_templates.objects.get(id=4)
            if User.objects.filter(email=email, soft_del_status="0"):
                return JsonResponse(
                    {"status": "error", "message": "Email allready exits !!!!"},
                    status=404,
                )
            elif User.objects.filter(mobile_number=mobile_number):

                return JsonResponse(
                    {"status": "error", "message": "Mobile Number allready exits !!!!"},
                    status=404,
                )

            # if latitude == ' ' or longitude == ' ':
            #     return JsonResponse({"status": "error", "message": " Please select valid address !!!!"}, status=404)

            # otp = generateOTP()

            elif password == re_password:
                userdata = User.objects.create(
                    fname=first_name,
                    lname=last_name,
                    email=email,
                    password=make_password(password),
                    mobile_number=phone,
                    country_code = code,
                    position_id=position,
                    roll=user_type,
                    referral=referral_code,
                )
                slug = userdata.slug
                otp = (
                    request.build_absolute_uri("/")[:-1]
                    + "/applicant/otp-verify/"
                    + str(slug)
                )

                unique_id = userdata.id + 100
                send_to = [email]
                subject = em.sub
                content = em.content
                t = strip_tags(content)
                c = t.replace("{name}", first_name + "" + last_name)
                msg = c.replace("{OTP}", "<a href=" + str(otp) + "> Click Link </a>")
                sub = "New Applicant Registration"
                try:
                    send_mail(
                        sub,
                        t,
                        from_mail,
                        [email],
                        fail_silently=False,
                        html_message=msg,
                                    )
                except:
                    pass
                userdata.OTP_string = otp
                userdata.save()
                try:
                    admins = User.objects.filter(is_staff = True)
                    for admin in admins:
                        fcm_token = admin.web_fcm_token
                        send_push_notification(fcm_token, "New Applicant Registration", "New applicant registred on Carenetstaff")
                except:
                    pass 
                WebNotification.objects.create(sender_name = f"{first_name} {last_name}", title= "New Applicant Registration" , message="New applicant registred on Carenetstaff")
                # em = email_templates.objects.get(id=4)
                # subject = em.sub
                # content = em.content
                # t = strip_tags(content)
                # c=t
                # otp=2323
                # msg = c.replace("{OTP}", "<a href="+str(otp)+">click</a>")
                # send_to=['testlink@getnada.com']
                # sendMail(subject, msg, send_to)
                # return HttpResponse("1")

                # unique_id = userdata.id + 100
                # send_to = [email]
                # subject = em.sub
                # content = em.content
                # t = strip_tags(content)
                # c = t.replace("{name}", first_name + "" + last_name)
                # msg = c.replace("{OTP}", otp)
                # # to = ["447912123799"]
                # # text = "Your otp Is :" + otp
                # sendMail(subject, msg, send_to)
                # # sendsms(to, text)
                # slug = userdata.slug

                return JsonResponse(
                    {
                        "status": "success",
                        "message": "Please Verify Your Email !!!!",
                        "slug": slug,
                    },
                    status=200,
                )

            else:
                return JsonResponse(
                    {"status": "error", "message": "Password Does not match!!!!"},
                    status=404,
                )
    return JsonResponse({"status": "error", "message": " No changed !!!!"}, status=404)


def app_resend_otp(request, slug):
    try:
        m = User.objects.get(slug=slug)
        em = email_templates.objects.get(id=3)

        o = generateOTP()
        m.OTP = o
        m.save()
        send_to = [m.email]
        subject = em.sub
        content = em.content
        otp = o
        name = m.first_name + " " + m.last_name
        t = strip_tags(content)
        c = t.replace("{name}", name)
        msg = c.replace("{OTP}", otp)
        # to = ["447912123799"]
        # text = "Your otp Is :" + otp
        email = send_to
        sub = subject
        try:
            send_mail(
                sub,
                t,
                from_mail,
                [email],
                fail_silently=False,
                html_message=msg,
                            )
        except:
            pass
        # sendsms(to, text)
        messages.success(request, "Otp sent successfully")
        return redirect("/applicant/otp-verify/" + slug)
    except:
        messages.error(request, "Something went wrong")
        return redirect("/applicant/otp-verify/" + slug)


def app_vaccation_information(request, slug):

    user = User.objects.get(slug=slug)

    print(user.slug)
    if request.method == "POST":
        vaccination = request.POST.get("Vaccination")
        booster = request.POST.get("booster")
        image = request.FILES.get("image")
        # city = request.POST.get('city')
        dob = request.POST.get("date_of_birth")
        # position = request.POST.get("position")
        Mnc_pin = request.POST.get("nmc_pin")

        recitation = request.POST.get("flexCheckyes")
        if recitation:
            recitations_desc = request.POST.get("recitations_desc")

        # dbc = request.POST.get("DBC")
        # DBC_Issues_Date = request.POST.get("DBC_Issues_Date")
        # DBC_status = request.POST.get("DBC_status")
        work_checkes = request.POST.get("flexCheckyespre")
        work_preference = request.POST.get("flexCheckyespress")
        emergency = request.POST.get("emergency")
        # if datetime.strptime(DBC_Issues_Date, "%Y-%m-%d") > datetime.now():
        #     messages.error(request, "Please Select Correct DBC issue Date ")
        #     return redirect("/applicant/vaccination/" + slug)

        count = request.POST.get("count")

        # 🖘 raise error if greater than

        # if datetime.strptime(training_start_date, "%Y-%m-%d") > datetime.now():
        #     messages.error(request, "Please Select Correct Training Start Date ")
        #     return redirect("/applicant/vaccination/" + slug)

        try:
            if image is None:
                data = ApplicantDeatails.objects.create(
                    user_id=user.id,
                    vaccinated=vaccination,
                    booster_dose=booster,
                    dob=dob,
                    work_checkes=work_checkes,
                    work_preference=work_preference,
                    Mnc_pin=Mnc_pin,
                    recitation=recitation,
                    emergency_no=emergency,
                    vaccination_status=True,
                )
                if recitation:
                    data.recitation_desc = recitations_desc
                if count:
                    c = int(count)
                    for i in range(c):
                        training = request.POST.get(f"training[{i}]name")
                        print(training, "kkkkkkkkkkkkkkkkkkk")
                        training_start_date = request.POST.get(
                            f"training_start[{i}]time"
                        )
                        print(training_start_date, "kkkkkkkkkkkkkkkkkkk")
                        training_end_date = request.POST.get(f"training_end[{i}]time")
                        print(training_end_date, "kkkkkkkkkkkkkkkkkkk")
                        if (
                            training == None
                            and training_start_date == ""
                            and training_end_date == ""
                        ):
                            pass
                        else:
                            training_data = ApplicantTraining.objects.create(
                                applicant_id=data.id,
                                training_id=training,
                                start_time=training_start_date,
                                end_time=training_end_date,
                            )
                else:
                    training = request.POST.get("training[0]name")
                    training_start_date = request.POST.get("training_start[0]time")
                    training_end_date = request.POST.get("training_end[0]time")
                    training_data = ApplicantTraining.objects.create(
                        applicant_id=data.id,
                        training_id=training,
                        start_time=training_start_date,
                        end_time=training_end_date,
                    )
                auth.logout(request)
                return redirect("home_redirect")
            else:
                fs = FileSystemStorage()
                filename = fs.save(image.name, image)
                data = ApplicantDeatails.objects.create(
                    user_id=user.id,
                    vaccinated=vaccination,
                    booster_dose=booster,
                    image=image,
                    dob=dob,
                    work_checkes=work_checkes,
                    work_preference=work_preference,
                    Mnc_pin=Mnc_pin,
                    recitation=recitation,
                    emergency_no=emergency,
                    vaccination_status=True,
                )
                if recitation:
                    data.recitation_desc = recitations_desc
                if count:
                    c = int(count)
                    for i in range(c):
                        training = request.POST.get(f"training[{i}]name")
                        print(training, "llllllllllllllllllll")
                        training_start_date = request.POST.get(
                            f"training_start[{i}]time"
                        )
                        print(training_start_date, "llllllllllllllllllll")
                        training_end_date = request.POST.get(f"training_end[{i}]time")
                        print(training_end_date, "llllllllllllllllllll")
                        if (
                            training == None
                            and training_start_date == ""
                            and training_end_date == ""
                        ):
                            pass
                        else:
                            training_data = ApplicantTraining.objects.create(
                                applicant_id=data.id,
                                training_id=training,
                                start_time=training_start_date,
                                end_time=training_end_date,
                            )
                else:
                    training = request.POST.get("training[0]name")
                    training_start_date = request.POST.get("training_start[0]time")
                    training_end_date = request.POST.get("training_end[0]time")
                    training_data = ApplicantTraining.objects.create(
                        applicant_id=data.id,
                        training_id=training,
                        start_time=training_start_date,
                        end_time=training_end_date,
                    )
                auth.logout(request)
                return redirect("home_redirect")

        except:
            messages.error(request, "Something went wrong")
            return redirect("/applicant/vaccination/" + slug)

    training = Training.objects.all()
    cat = Category.objects.all()
    date = datetime.now()
    m = date.date()

    return render(
        request,
        "applicant/sign-up-after-submit-applicants.html",
        {
            "cat": cat,
            "training": training,
            "user_name": user.fname + " " + user.lname,
            "date": m,
        },
    )

    # training = Training.objects.all()
    # cat = Category.objects.all()
    # return render(
    #     request,
    #     "applicant/sign-up-after-submit-applicants.html",
    #     {
    #         "cat": cat,
    #         "training": training,
    #         "user_name": user.fname + " " + user.lname,
    #     },
    # )


def emp_sign_up(request):
    userdata = User.objects.all()
    country = Country.objects.all()

    return render(
        request,
        "client/sign-up-employers.html",
        {"userdata": userdata, "country": country, "postal_key": settings.POSTAL_KEY},
    )


def emp_data_ajax(request):
    if request.method == "POST":
        company_profile_status = request.POST.get("company_profile_status")
        first_name = request.POST.get("FName")
        last_name = request.POST.get("LName")
        company_name = request.POST.get("CName")
        email = request.POST.get("email")
        password = request.POST.get("password")
        re_password = request.POST.get("rePassword")
        mobile_number = request.POST.get("mob_num")
        code = mobile_number.split(" ")[0]
        phone = mobile_number.split(" ")[1]
        user_type = request.POST.get("user_type")
        referral_code = generate_referal_code(user_type)
        # latitude = request.POST.get('latitude')
        # longitude = request.POST.get('longitude')
        # address = request.POST.get("address")
        # address2 = request.POST.get("address2")
        # country = request.POST.get("country")
        # state = request.POST.get("state")
        # city = request.POST.get("city")
        # postal = request.POST.get("postal_code")

        # df = geopandas.tools.geocode(postal)

        # try:
        #     df["lon"] = df["geometry"].x
        #     df["lat"] = df["geometry"].y
        #     lat = df["lat"]
        #     long = df["lon"]

        # except:
        #     return JsonResponse(
        #         {"status": "error", "message": " Please select valid post code !!!!"},
        #         status=404,
        #     )


        # otp = generateOTP()

        em = email_templates.objects.get(id=4)

        if "@" and "." not in email:
            return JsonResponse(
                {"status": "error", "message": "Invalid Email address !!!!"},
                status=404,
            )

        if user_type == "employer":
            print("sdfsfsfsfs")

            if User.objects.filter(email=email):
                return JsonResponse(
                    {"status": "error", "message": "email allready exits !!!!"},
                    status=404,
                )

            elif User.objects.filter(mobile_number=phone):
                return JsonResponse(
                    {"status": "error", "message": "Mobile Number allready exits !!!!"},
                    status=404,
                )

            elif password == re_password:

                userdata = User.objects.create(
                    company_profile_status=company_profile_status,
                    # latitude=lat,
                    # longitude=long,
                    # country=country,
                    # state=state,
                    # city=city,
                    # post_code=postal,
                    fname=first_name,
                    lname=last_name,
                    company=company_name,
                    email=email,
                    password=make_password(password),
                    mobile_number=phone,
                    # OTP=otp,
                    country_code=code,
                    # address=address,
                    # address2=address2,
                    roll=user_type,
                    referral=referral_code,
                )
                try:
                    admins = User.objects.filter(is_staff = True)
                    for admin in admins:
                        fcm_token = admin.web_fcm_token
                        send_push_notification(fcm_token, "New Client Registration", "New client registred on Carenetstaff")
                except:
                    pass 
                WebNotification.objects.create(sender_name = f"{first_name} {last_name}", title= "New Client Registration" , message="New client registred on Carenetstaff")

                slug = userdata.slug
                otp = (
                    request.build_absolute_uri("/")[:-1]
                    + "/client/otp-verify/"
                    + str(slug)
                )

                unique_id = userdata.id + 100
                send_to = [email]
                subject = em.sub
                content = em.content
                t = strip_tags(content)
                c = t.replace("{name}", first_name + "" + last_name)
                msg = c.replace("{OTP}", "<a href=" + str(otp) + ">Click Link </a>")
                sub = "New Client Registration"

                send_mail(
                        sub,
                        t,
                        from_mail,
                        [email],
                        fail_silently=False,
                        html_message=msg,
                                    )
                userdata.OTP_string = otp
                userdata.email_verified = True
                userdata.save()
                # to = ["447912123799"]
                # text = "Your otp Is :" + otp
                # sendMail(subject, msg, send_to)
                # sendsms(to, text)
                # messages.success(
                #     request, " Employer User Created and password sent on mail ")

                return JsonResponse(
                    {
                        "status": "success",
                        "message": "Please Verify Your Email !!!!",
                        "slug": slug,
                    },
                    status=200,
                )

            else:
                return JsonResponse(
                    {"status": "error", "message": "Password Does not match!!!!"},
                    status=404,
                )
        print("sdsdsdssssssss")
    return JsonResponse({"status": "error", "message": " No changed !!!!"}, status=404)


def emp_otp_verify(request, slug):
    user = User.objects.get(slug=slug)
    user.OTP_string = ""
    user.save()
    messages.success(request, "Your Account Verified Successfully !!!")
    return redirect("/login/")

    # return HttpResponse(
    #     "<h1 style=text-align:center >Care Net</h1><h4 style=text-align:center> Your Acoount is Verified </h4><div style=text-align:center;><a  href='/login/' > Login </a></div>"
    # )


def emp_resend_otp(request, slug):
    m = User.objects.get(slug=slug)
    em = email_templates.objects.get(id=3)
    o = generateOTP()
    m.OTP = o
    m.save()
    send_to = [m.email]
    subject = em.sub

    content = em.content

    otp = o
    print(otp, "otpppppppppppppppppppppppppppppppp")
    name = m.fname + " " + m.lname
    print(name, "ddddddddddddddddddddddddddddddd")
    t = strip_tags(content)
    print(t, "ttttttttttttttttttttttttttt")
    c = t.replace("{name}", name)
    print(c, "hhhhhhhhhhhhhhhhhhhhhhhhhhhh")
    msg = c.replace("{OTP}", otp)
    print(msg, "ggggggggggggggggggggggggggg")
    # to = ["447912123799"]
    # text = "Your otp Is :" + otp
    sendMail(subject, msg, send_to)
    # sendsms(to, text)

    return redirect("/client/otp-verify/" + slug)

    # return redirect( '/client/otp-verify/' + slug)


def app_otp_verify(request, slug):
    user = User.objects.get(slug=slug)
    user.OTP_string = ""
    user.email_verified = True
    user.save()
    messages.success(request, "Your Account Verified Successfully !!!")
    return redirect("/applicant/vaccination/" + slug)


def otp_verify_ajax(request, slug):
    u = User.objects.get(slug=slug)
    if request.method == "POST":
        otp1 = request.POST.get("otp1")
        otp2 = request.POST.get("otp2")
        otp3 = request.POST.get("otp3")
        otp4 = request.POST.get("otp4")
        Otp = str(otp1) + str(otp2) + str(otp3) + str(otp4)

        if u.OTP == Otp:
            return JsonResponse(
                {"status": "success", "message": "Otp Verified !!!!", "slug": slug}
            )
    else:
        return JsonResponse(
            {"status": "error", "message": "Otp Dose not match !!!!", "slug": slug},
            status=404,
        )
    return JsonResponse(
        {"status": "error", "message": "Otp Dose not match!!!!"}, status=404
    )


# employer
# employer


def emp_company_information(request, slug):
    user = User.objects.get(slug=slug)
    if request.method == "POST":
        per_name = request.POST.get("P_Solename")
        per_name2 = request.POST.get("P_Partnershipname")

        company_name = request.POST.get("Cname")
        contact_name = request.POST.get("Contact_name")
        phone_number = request.POST.get("mob_num")
        fax = request.POST.get("fax")
        Postal_code = request.POST.get("Postal_code")

        email = request.POST.get("email")
        address = request.POST.get("Address")
        address2 = request.POST.get("Address")
        country = request.POST.get("country")
        city = request.POST.get("city")
        year_in_bussiness = request.POST.get("year_in_bussiness")
        sole_trador = request.POST.get("sole")
        partnership = request.POST.get("partnership")
        limited_company = request.POST.get("limited_company")
        limited_company_partnership = request.POST.get("limited_company_partnership")
        redio = request.POST.get("propertytype")
        tax = request.POST.get("tax")
        lat = request.POST.get("latitude")
        long = request.POST.get("longitude")

        prefrence_company_name = request.POST.get("Cname1")

        prefrence_Contact_name = request.POST.get("Contact_name1")
        prefrence_phone_number = request.POST.get("mob_num1")

        prefrence_email = request.POST.get("email1")

        prefrence_Postal_code = request.POST.get("Postal_code1")

        prefrence_Address1 = request.POST.get("Address1")

        prefrence_Address2_1 = request.POST.get("Address2_1")

        prefrence_country = request.POST.get("country1")

        prefrence_city = request.POST.get("city1")

        prefrence_lat = request.POST.get("prefrence_lat")

        prefrence_long = request.POST.get("prefrence_long")

        prefrence_company_name2 = request.POST.get("Cname2")
        prefrence_Contact_name2 = request.POST.get("Contact_name2")

        prefrence_phone_number2 = request.POST.get("mob_num2")

        prefrence_email2 = request.POST.get("email2")

        prefrence_Postal_code2 = request.POST.get("Postal_code2")

        prefrence_Address2 = request.POST.get("Address2")

        prefrence_Address2_2 = request.POST.get("Address2_2")

        prefrence_country2 = request.POST.get("country2")

        prefrence_city2 = request.POST.get("city2")

        prefrence_lat2 = request.POST.get("prefrence_lat2")

        prefrence_long2 = request.POST.get("prefrence_long2")
        if redio == "1":
            users = CompanyInfo.objects.create(
                user_id=user.id,
                proprietor_name=per_name,
                phone_number=phone_number,
                contact_name=contact_name,
                fax=fax,
                email=email,
                address=address,
                address2=address2,
                year_of_business=year_in_bussiness,
                # registration_num=sole_trador,
                partnership=redio,
                tax=tax,
                post_code=Postal_code,
                country=country,
                city=city,
                latitude=lat or "0",
                longitude=long or "0",
                prefrence_business_name_1=prefrence_company_name,
                prefrence1_postcode=prefrence_Postal_code,
                prefrence_contact_name_1=prefrence_Contact_name,
                prefrence_phone_number_1=prefrence_phone_number,
                prefrence_email_1=prefrence_email,
                prefrence_country_1=prefrence_country,
                prefrence_city_1=prefrence_city,
                prefrence1_latitude=prefrence_lat or "0",
                prefrence1_longitude=prefrence_long or "0",
                prefrence1_address=prefrence_Address1,
                prefrence1_address2=prefrence_Address2_1,
                prefrence_business_name_2=prefrence_company_name2,
                prefrence2_postcode=prefrence_Postal_code2,
                prefrence_contact_name_2=prefrence_Contact_name2,
                prefrence_phone_number_2=prefrence_phone_number2,
                prefrence_email_2=prefrence_email2,
                prefrence_country_2=prefrence_country2,
                prefrence_city_2=prefrence_city2,
                prefrence2_latitude=prefrence_lat2 or "0",
                prefrence2_longitude=prefrence_long2 or "0",
                prefrence2_address=prefrence_Address2,
                prefrence2_address2=prefrence_Address2_2 or "null",
            )

            user.company_profile_status = True
            user.save()
            if user.roll == "employer":
                if not user.latitude:
                    try:
                        c_address = CompanyInfo.objects.get(user_id = user.id)
                        user.address = c_address.address
                        user.address2 = c_address.address2
                        user.city = c_address.city
                        user.post_code = c_address.post_code
                        user.country = c_address.country
                        user.latitude = c_address.latitude
                        user.longitude = c_address.longitude
                        user.save()
                    except:
                        pass  
            messages.success(request, "Company details saved succssfully !!!! ")
            auth.login(request, user)
            return redirect("/")
        elif redio == "2":
            users = CompanyInfo.objects.create(
                user_id=user.id,
                proprietor_name=per_name2,
                contact_name=contact_name,
                phone_number=phone_number,
                fax=fax,
                email=email,
                post_code=Postal_code,
                country=country,
                city=city,
                address=address,
                address2=address2,
                year_of_business=year_in_bussiness,
                # registration_num=partnership,
                partnership=redio,
                tax=tax,
                latitude=lat or "0",
                longitude=long or "0",
                prefrence_business_name_1=prefrence_company_name,
                prefrence1_postcode=prefrence_Postal_code,
                prefrence_contact_name_1=prefrence_Contact_name,
                prefrence_phone_number_1=prefrence_phone_number,
                prefrence_email_1=prefrence_email,
                prefrence_country_1=prefrence_country,
                prefrence_city_1=prefrence_city,
                prefrence1_latitude=prefrence_lat or "0",
                prefrence1_longitude=prefrence_long or "0",
                prefrence1_address=prefrence_Address1,
                prefrence1_address2=prefrence_Address2_1,
                prefrence_business_name_2=prefrence_company_name2,
                prefrence2_postcode=prefrence_Postal_code2,
                prefrence_contact_name_2=prefrence_Contact_name2,
                prefrence_phone_number_2=prefrence_phone_number2,
                prefrence_email_2=prefrence_email2,
                prefrence_country_2=prefrence_country2,
                prefrence_city_2=prefrence_city2,
                prefrence2_latitude=prefrence_lat2 or "0",
                prefrence2_longitude=prefrence_long2 or "0",
                prefrence2_address=prefrence_Address2,
                prefrence2_address2=prefrence_Address2_2 or "null",
            )

            user.company_profile_status = True
            user.save()
            if user.roll == "employer":
                if not user.latitude:
                    try:
                        c_address = CompanyInfo.objects.get(user_id = user.id)
                        user.address = c_address.address
                        user.address2 = c_address.address2
                        user.city = c_address.city
                        user.post_code = c_address.post_code
                        user.country = c_address.country
                        user.latitude = c_address.latitude
                        user.longitude = c_address.longitude
                        user.save()
                    except:
                        pass  
            messages.success(request, "Company details saved succssfully !!!! ")
            auth.login(request, user)
            return redirect("/")
        elif redio == "3":
            users = CompanyInfo.objects.create(
                user_id=user.id,
                company_name=company_name,
                contact_name=contact_name,
                phone_number=phone_number,
                fax=fax,
                email=email,
                address=address,
                post_code=Postal_code,
                country=country,
                city=city,
                address2=address2,
                year_of_business=year_in_bussiness,
                registration_num=limited_company,
                partnership=redio,
                tax=tax,
                latitude=lat or "0",
                longitude=long or "0",
                prefrence_business_name_1=prefrence_company_name,
                prefrence1_postcode=prefrence_Postal_code,
                prefrence_contact_name_1=prefrence_Contact_name,
                prefrence_phone_number_1=prefrence_phone_number,
                prefrence_email_1=prefrence_email,
                prefrence_country_1=prefrence_country,
                prefrence_city_1=prefrence_city,
                prefrence1_latitude=prefrence_lat or "0",
                prefrence1_longitude=prefrence_long or "0",
                prefrence1_address=prefrence_Address1,
                prefrence1_address2=prefrence_Address2_1,
                prefrence_business_name_2=prefrence_company_name2,
                prefrence2_postcode=prefrence_Postal_code2,
                prefrence_contact_name_2=prefrence_Contact_name2,
                prefrence_phone_number_2=prefrence_phone_number2,
                prefrence_email_2=prefrence_email2,
                prefrence_country_2=prefrence_country2,
                prefrence_city_2=prefrence_city2,
                prefrence2_latitude=prefrence_lat2 or "0",
                prefrence2_longitude=prefrence_long2 or "0",
                prefrence2_address=prefrence_Address2,
                prefrence2_address2=prefrence_Address2_2 or "null",
            )

            user.company_profile_status = True
            user.save()
            if user.roll == "employer":
                if not user.latitude:
                    try:
                        c_address = CompanyInfo.objects.get(user_id = user.id)
                        user.address = c_address.address
                        user.address2 = c_address.address2
                        user.city = c_address.city
                        user.post_code = c_address.post_code
                        user.country = c_address.country
                        user.latitude = c_address.latitude
                        user.longitude = c_address.longitude
                        user.save()
                    except:
                        pass  
            messages.success(request, "Company details saved succssfully !!!! ")
            auth.login(request, user)
            return redirect("/")
        else:
            users = CompanyInfo.objects.create(
                user_id=user.id,
                company_name=company_name,
                contact_name=contact_name,
                phone_number=phone_number,
                fax=fax,
                email=email,
                address=address,
                post_code=Postal_code,
                country=country,
                city=city,
                address2=address2,
                year_of_business=year_in_bussiness,
                registration_num=limited_company_partnership,
                partnership=redio,
                tax=tax,
                latitude=lat or "0",
                longitude=long or "0",
                prefrence_business_name_1=prefrence_company_name,
                prefrence1_postcode=prefrence_Postal_code,
                prefrence_contact_name_1=prefrence_Contact_name,
                prefrence_phone_number_1=prefrence_phone_number,
                prefrence_email_1=prefrence_email,
                prefrence_country_1=prefrence_country,
                prefrence_city_1=prefrence_city,
                prefrence1_latitude=prefrence_lat or "0",
                prefrence1_longitude=prefrence_long or "0",
                prefrence1_address=prefrence_Address1,
                prefrence1_address2=prefrence_Address2_1,
                prefrence_business_name_2=prefrence_company_name2,
                prefrence2_postcode=prefrence_Postal_code2,
                prefrence_contact_name_2=prefrence_Contact_name2,
                prefrence_phone_number_2=prefrence_phone_number2,
                prefrence_email_2=prefrence_email2,
                prefrence_country_2=prefrence_country2,
                prefrence_city_2=prefrence_city2,
                prefrence2_latitude=prefrence_lat2 or "0",
                prefrence2_longitude=prefrence_long2 or "0",
                prefrence2_address=prefrence_Address2,
                prefrence2_address2=prefrence_Address2_2 or "null",
            )
            users.save()

            user.company_profile_status = True
            user.save()
            if user.roll == "employer":
                if not user.latitude:
                    try:
                        c_address = CompanyInfo.objects.get(user_id = user.id)
                        user.address = c_address.address
                        user.address2 = c_address.address2
                        user.city = c_address.city
                        user.post_code = c_address.post_code
                        user.country = c_address.country
                        user.latitude = c_address.latitude
                        user.longitude = c_address.longitude
                        user.save()
                    except:
                        pass  
            messages.success(request, "Company details saved succssfully !!!! ")
            auth.login(request, user)
            return redirect("/")
        # except:
        #     messages.error(request, "Something Went Wrong")
        #     return redirect("/profile/company-profile/" + slug)

    country = Country.objects.all()
    return render(
        request,
        "client/enter-your-company-information.html",
        {"country": country, "postal_key": settings.POSTAL_KEY},
    )


def Change_password(request):
    try:
        us = SocialAccount.objects.get(user_id=request.user.id)
        u = User.objects.get(id=us.user_id)
        u.roll = "employer"
        u.fname = u.first_name
        u.lname = u.last_name
        u.save()
        if u.company_profile_status == False:
            messages.error(request, "Please Fill Your Company Profile ")
            return redirect("/profile/company-profile/" + u.slug)
        else:
            pass

    except:
        pass
    if request.method == "POST":
        password = request.POST.get("pass")
        new_passowrd = request.POST.get("newpass")
        rnew_passowrd = request.POST.get("cnewpass")
        user = User.objects.get(id=request.user.id)
        print()
        un = user.id
        print(user, "ddddddddddddddd")
        check = user.check_password(password)
        if check == True:
            if new_passowrd == rnew_passowrd:
                user.set_password(new_passowrd)
                user.save()
                user = User.objects.get(id=un)
                login_check(request, user)
                messages.success(request, " Password changed Successfully !!!! ")
                return redirect("/client/change-password")
            else:
                messages.error(request, " Password Does not Match !!!! ")
                return redirect("/client/change-password")
        else:
            messages.error(request, " Old password Does not Match !!!! ")
            return redirect("/client/change-password")
    total_Notification = Notification.objects.filter(user_id=request.user.id).count()
    return render(
        request, "change-password.html", {"total_Notification": total_Notification}
    )


def privacy_policy(request):
    privacy = Privacy.objects.all()
    return render(request, "privacy-policy.html", {"privacy": privacy})


def cookies_read(request):
    return render(request, "cookies.html")


def test4(request):
    return render(request, "client/enter-your-company-information.html")
