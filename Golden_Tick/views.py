from urllib.request import Request
from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse, request, response
from event_admin.models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login as login_check
from django.contrib.auth.models import auth
from django.conf import settings
import random
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.hashers import MD5PasswordHasher, make_password,check_password
from .email import *
from django.views.decorators.csrf import csrf_exempt
from datetime import date
from django.db.models import Avg
from .helper import *
import geocoder
from math import sin, cos, radians, acos
from_mail=settings.EMAIL_HOST_USER
import json
import requests

def send_notification(registration_ids , message_title , message_desc):
    fcm_api = settings.FCM
    url = "https://fcm.googleapis.com/fcm/send"
    headers = {
    "Content-Type":"application/json",
    "Authorization": 'key='+fcm_api}
    payload = {
        "registration_ids" :registration_ids,
        "priority" : "high",
        "notification" : {
            "body" : message_desc,
            "title" : message_title,
            "image" : "https://eventticketbooking.devtechnosys.tech/static/participant/images/logo-black.svg",
            "icon": "https://eventticketbooking.devtechnosys.tech/static/participant/images/logo-black.svg",
            
        }
    }
    result = requests.post(url,  data=json.dumps(payload), headers=headers )
    print(result.json())
    

def location(request):
    g = geocoder.ip('me')
    city = g.city
    state = g.state
    location = f'{city} {state}'
    return JsonResponse({'location': location})

@csrf_exempt
def save_fcm_tocken(request):
    try:
        user_id = request.user.id
        notification_data = NotificationSetting.objects.get(user_id = user_id)
        notification_data.fcm_tocken = request.POST.get("currentToken")
        notification_data.save()
        return JsonResponse({'success': 'success'})
    except:
        pass    

def homeView(request): 
    try:
        g = geocoder.ipinfo('me')
        city = g.city
        state = g.state   
        banner_obj=BannerManagement.objects.filter(is_active=False)
        category_obj=EventCategory.objects.exclude(is_active=False)
        social=SocialSetting.objects.all()
        current_date=datetime.now()
        category_data = EventCreate.objects.all()
        event_category = []
        for data in category_data:
            event_category.append(int(data.category_id))
        upcoming_event=EventCreate.objects.filter(start_time__gte = current_date, is_active='1',event_cancel='0',ticket_create_status=False, privacy = True).order_by('start_time')
        upcoming_event_count=EventCreate.objects.filter(start_time__gte = current_date,privacy = False, is_active='1').count()
        feature_event  = Featured.objects.all()
        # ticket=EventTicketCreate.objects.filter(ticket_event_id__in=upcoming_event)
        ticket=EventTicketCreate.objects.all()[:5]
        ticket_data=EventTicketCreate.objects.all()
        trending_event=EventCreate.objects.filter( is_active='1',privacy = True, event_cancel='0',ticket_create_status=True,id__in = list(ticket_data.values_list("ticket_event_id", flat=True)))
        ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=trending_event)
        # trending_event=EventCreate.objects.filter(id__in = list(ticket.values_list("ticket_event_id", flat=True)))
        all_event = EventTicketCreate.objects.filter(ticket_event__is_active='1')
        favouritees=Favourite.objects.filter(favourite=True, user_id=request.user.id).values_list('event_id',flat=True)
        try:
            whychoose=WhyChooseUs.objects.get(id=1)
        except:
            whychoose=None
        data={'event_category': event_category, 'city': city, 'state': state,'banner':banner_obj,'category':category_obj,'sociallink':social,'feature_event': feature_event,  
                'whychoose':whychoose,'upcoming_event':upcoming_event,"upcoming_event_count":upcoming_event_count,
                        'ticket': ticket,'trending_event':trending_event,'ticket_price':ticket_price,'all_event':all_event
                        ,'favouritees':favouritees}                              
        return render(request,'frontend/include/body.html',data)
    except:
        messages.error(request, 'Something Went Wrong')
        return redirect(request.META.get('HTTP_REFERER'))  


def search_event(request):
    try:
        g = geocoder.ip('me')
        city = g.city
        state = g.state
        banner_obj=BannerManagement.objects.filter(is_active=False)
        category_obj=EventCategory.objects.exclude(is_active=False)
        social=SocialSetting.objects.all()
        current_date=datetime.now()
        upcoming_event=EventCreate.objects.filter(start_time__gte = current_date,event_cancel='0', is_active='1',ticket_create_status=False).order_by('start_time')
        upcoming_event_count=EventCreate.objects.filter(start_time__gte = current_date, is_active='1').count()
        feature_event  = Featured.objects.all()
        # ticket=EventTicketCreate.objects.filter(ticket_event_id__in=upcoming_event)
        ticket=EventTicketCreate.objects.all()[:5]
        ticket_data=EventTicketCreate.objects.all()
        trending_event=EventCreate.objects.filter(id__in = list(ticket_data.values_list("ticket_event_id", flat=True)), is_active='1', ticket_create_status=True,event_cancel='0')
        ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=trending_event)
        # trending_event=EventCreate.objects.filter(id__in = list(ticket.values_list("ticket_event_id", flat=True)))
        all_event = EventTicketCreate.objects.filter(ticket_event__is_active='1')
        favouritees=Favourite.objects.filter(favourite=True,user_id=request.user.id).values_list('event_id',flat=True)
        try:
            whychoose=WhyChooseUs.objects.get(id=1)
        except:
            whychoose=None
        select_distance = 16.00
        obj_list = []
        for i in trending_event:
            if request.method == "POST":
                latitude1=request.POST.get('latitude')
                longitude1=request.POST.get('longitude')
                lat_a = float(latitude1)
                long_a = float(longitude1)
                lat_b = i.latitude
                long_b = i.longitude
                lat_a = radians(lat_a)
                lat_b = radians(lat_b)
                delta_long = radians(long_a - long_b)
                cos_x = (sin(lat_a) * sin(lat_b) +
                    cos(lat_a) * cos(lat_b) * cos(delta_long))
                distance_data = acos(cos_x) * 3958.8 * 1.60934
                distance = "%.2f" % distance_data
                if select_distance > float(distance):
                    obj_list.append(i)  
            else:
                latitude1= g.lat
                longitude1= g.lng
                longitude2=i.longitude
                latitude2=i.latitude
                distance = haversine(float(longitude1), float(latitude1), float(longitude2), float(latitude2))
                if float(select_distance) > float(distance):
                    obj_list.append(i)              
        data={'city': city, 'state': state, 'banner':banner_obj,'category':category_obj,'sociallink':social,'feature_event': feature_event,  
                'whychoose':whychoose,'upcoming_event':upcoming_event,"upcoming_event_count":upcoming_event_count,
                        'ticket': ticket,'trending_event':obj_list,'ticket_price':ticket_price,'all_event':all_event
                        ,'favouritees':favouritees}
        return render(request,'frontend/include/search_body.html',data)
    except:
        messages.error(request, 'Something Went Wrong')
        return redirect('home')


@login_required(login_url='/login/')
def ticket_view(request, slug):
    try:
        user_id = request.user.id
        event_data = EventCreate.objects.get(slug = slug)
        start_date = event_data.start_time
        today_date = timezone.now()
        if start_date > today_date:
            start = event_data.start_time
        else:
            start = today_date
        end_date = event_data.end_time
        day_count = (end_date - start).days + 1
        dates = [d for d in (start + timedelta(n) for n in range(day_count)) if d <= end_date]  
        event_id = event_data.id
        ticket_data = EventTicketCreate.objects.get(ticket_event_id = event_id)
        time_slots = Tickets.objects.filter(event_ticket_id = ticket_data.id)
        ticket_data = EventTicketCreate.objects.get(ticket_event_id = event_id)
        seats_category = TicketSeats.objects.filter(ticket_id = ticket_data.id).order_by('-seat_price')
        seats_category_count = seats_category.count()
        if request.method == "POST":
            if UserTickets.objects.all().exists():
                obj = UserTickets.objects.last()
                order_id = int(obj.order_id) + 1
            else:
                order_id = '1001'
            seats = request.POST.get("user_selected_seat")
            seat_category_id = request.POST.get("seat_category_id")
            seat_quantity = request.POST.get("seat_quantity")
            date = request.POST.get("date_of_event")
            time = request.POST.get("time_of_event")
            date_time = f'{date} {time}'
            data = TicketSeats.objects.get(id=seat_category_id)
            price = data.seat_price
            total_price = float(price) * float(seat_quantity)
            request.session['ticket_data'] = {
                'user_id': user_id,
                'event_id' :event_data.id,
                'ticket_id' :ticket_data.id,
                'seat_quantity' :seat_quantity,
                'date_and_time' :date_time,
                'total_price' :total_price,
                'seat_category_id' :seat_category_id,
                'seats' :seats,
                'order_id' :order_id,
                'discounted_price': 0.00,
                'offer_id': None
            }
            request.session.modified = True 
            return redirect("checkout_ticket")
        return render(request, "frontend/event_booking/ticket_book.html", { 'dates': dates,
                                                                            'seats_category_count': seats_category_count,
                                                                            'event_data': event_data, 
                                                                            'ticket_data': ticket_data,
                                                                            'time_slots': time_slots,
                                                                            'seats_category': seats_category })
    except:
        messages.error(request, "Something Went Wrong")
        return redirect('home')                                                                    


@login_required(login_url='/login/')
def checkout_ticket(request):
    try:
        ticket_data = request.session['ticket_data']
        seat_category = TicketSeats.objects.get(id = ticket_data['seat_category_id'])
        event_data = EventCreate.objects.get(id = ticket_data['event_id'])
        return render(request,"frontend/event_booking/checkout.html", {'ticket_data': ticket_data, 'event_data': event_data, 'seat_category': seat_category} )
    except:
        messages.error(request,'Something Went Wrong')
        return redirect('home')


@csrf_exempt
def apply_offer(request):
    ticket_data = request.session['ticket_data']
    offer_code = request.POST.get("offer_code")
    total_price = ticket_data['total_price']
    offer_data = Offer.objects.get(name = offer_code)
    discount_percentage = offer_data.percentage
    discounted_price = float(total_price) * (float(discount_percentage)/100)
    discount = float(total_price) - float(discounted_price)
    ticket_data['discounted_price'] = discount
    ticket_data['offer_id'] = offer_data.id
    request.session['ticket_data'] = ticket_data
    request.session.modified = True 
    return JsonResponse({"discount_percentage": discount_percentage, "discount": discount })


@csrf_exempt
def remove_offer(request):
    ticket_data = request.session['ticket_data']
    ticket_data['discounted_price'] = 0.00
    ticket_data['offer_id'] = None
    request.session['ticket_data'] = ticket_data
    request.session.modified = True 
    return JsonResponse({"offer_code": 0.00})    


def pay_ticket(request):
    try:
        ticket_session_data = request.session['ticket_data']
        seat_category = TicketSeats.objects.get(id = ticket_session_data['seat_category_id'])
        event_data = EventCreate.objects.get(id = ticket_session_data['event_id'])
        user = User.objects.get(id = ticket_session_data['user_id'])
        ticket_data = UserTickets.objects.create( user_id = ticket_session_data['user_id'], event_id = ticket_session_data['event_id'], 
                ticket_id = ticket_session_data['ticket_id'], 
                seat_quantity = ticket_session_data['seat_quantity'],
                date_and_time = ticket_session_data['date_and_time'],
                seat_category_id = ticket_session_data['seat_category_id'],
                seats = ticket_session_data['seats'], order_id = ticket_session_data['order_id'],
                total_prices = ticket_session_data['total_price'],
                discounted_price = ticket_session_data['discounted_price'],
                offer_id = ticket_session_data['offer_id'])
        ticket_buy_qr(user, ticket_data)
        message = f'Hi {event_data.organizer.first_name} {event_data.organizer.last_name}, ticket for the event {event_data.evnet_name} sold'
        OrganizerNotification.objects.create(subject="Ticket Sold", message = message, notification_type = 'TICKETS_SOLD', organizer_id = event_data.organizer_id)
        message = f"{user.first_name} {user.last_name}, bought ticket for the event {event_data.evnet_name}"
        AdminNotification.objects.create(subject="Ticket Sold", message = message, notification_type = 'TICKETS')
        del request.session['ticket_data']
        request.session.modified = True
        return render(request, "frontend/event_booking/pay.html", {'ticket_data': ticket_session_data, 'seat_category': seat_category, 'event_data': event_data})        
    except:
        messages.error(request,'Something Went Wrong')
        return redirect('home')


def view_ticket_by_qr(request, slug):
    try:
        ticket_data = UserTickets.objects.get(slug = slug)
        ticket_data.is_used = True
        ticket_data.save()
        return render(request, "frontend/event_booking/ticket_view_qr.html", {'ticket_data': ticket_data})
    except:
        messages.error(request, "Something Went Wrong")
        return redirect('home')


@csrf_exempt
def reserved_seat_data(request):
    event_id = request.POST.get("event_id")
    date = request.POST.get("date")
    time = request.POST.get("time")
    date_and_time = f'{date} {time}'
    seat_data = UserTickets.objects.filter(event_id = event_id, date_and_time = date_and_time)

    sold_seat = []
    for seat_id in seat_data:
        id = seat_id.seats
        xyz = tuple(id.split(","))
        for seat in xyz:
            sold_seat.append(seat)
    return JsonResponse({"seat_data": sold_seat})



def notification_settings(request):
    try:
        notification_settings = NotificationSetting.objects.get(user_id = request.user.id)
        return render(request, "frontend/notification/settings.html", {'notification_settings': notification_settings})
    except:
        messages.error(request, 'Something Went Wrong')
        return redirect('home')

@csrf_exempt    
def change_notification_setting(request):
    settings = NotificationSetting.objects.get(user_id = request.user.id)
    invite = request.POST.get('invite')
    follow = request.POST.get('follow')
    if invite == '1':
        settings.invite = True
    else:
        settings.invite = False

    if follow == '1':    
        settings.follow = True
    else:
        settings.follow = False
    settings.save()
    return JsonResponse({'success': 'success'})


def user_tickets(request):
    try:
        user_id = request.user.id
        ticket_data = UserTickets.objects.filter(user_id = user_id)
        return render(request, "frontend/event_booking/user-ticket.html", {'ticket_data': ticket_data})
    except:
        messages.error(request, "Something Went Wrong")
        return redirect('home')    


def loginView(request):
        # u = User.objects.get(id=72)
        # u.delete()
    try:
        if request.method=="POST":
            data = request.POST
            email=request.POST.get('email')
            password=request.POST.get('password')
            
            if email == '' or email.isspace():
                messages.error(request,'Please Enter the email')
                return render(request,'frontend/login.html', {'data':data})
            if '@' not in email:
                messages.error(request,'Please Enter the valid email')
                return render(request,'frontend/login.html', {'data':data})
            if '.' not in email:
                messages.error(request,'Please Enter the valid email')
                return render(request,'frontend/login.html', {'data':data})
            if password == '' or password.isspace():
                messages.error(request,'Please Enter the password ')
                return render(request,'frontend/login.html', {'data':data})
            if User.objects.filter(email=email, is_active=True, roll='2').exists():
                user = User.objects.get(email=email)
                if not user.is_superuser=='1':
                    if user.OTP == "":
                        if user.is_profile_setup:
                            if user.check_password(password):
                                auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                                messages.success(request,'You are successfully Login!!')
                                return redirect('home')
                            else:
                                messages.error(request,'Incorrect Password.')
                                return render(request,'frontend/login.html', {'data':data})
                        else:
                            messages.error(request,'Please Complete profile Setup.')
                            return redirect('/profileSetUp/'+str(user.slug))  
                    else:
                        otp=random.randint(1000,9999)
                        user.OTP=otp
                        user.save()
                        
                        subject='Verification OTP'
                        message=f"Your Verification OTP is:{otp}"
                        sendmail(subject,message,email)
                        messages.error(request,'OTP send in your email id  ')
                        return redirect('/signup/otp/verification/' + str(user.slug))
                else:
                    messages.error(request,'you are super user!!')
                    return render(request,'frontend/login.html', {'data':data})
                
            else:
                messages.error(request,'Email not Found or not a valid user.')
                return render(request,'frontend/login.html', {'data':data})
        return render(request,'frontend/login.html')
    except:
        messages.error(request,'Something Went Wrong')
        return redirect('home')


def signUp(request):
    try:
        if request.method=='POST':
            data=request.POST
            email=request.POST.get('email')
            email_instance=email.lower()
            password=request.POST.get('password')
            confirm_password=request.POST.get('confirm_password')
            if email_instance == '' or email_instance.isspace():
                messages.error(request,'Please Enter the email')
                return render(request,'frontend/auth/sign-up.html',{'data':data})
            if '@' not in email_instance:
                messages.error(request,'Please Enter the valid email')
                return render(request,'frontend/auth/sign-up.html',{'data':data})
            if '.' not in email_instance:
                messages.error(request,'Please Enter the valid email')
                return render(request,'frontend/auth/sign-up.html',{'data':data})
            if password == '' or password.isspace():
                messages.error(request,'Please Enter the password ')
                return render(request,'frontend/auth/sign-up.html',{'data':data})
            if confirm_password == '' or confirm_password.isspace():
                messages.error(request,'Please Enter the confirm password ')
                return render(request,'frontend/auth/sign-up.html',{'data':data})
            if not len(password) > 7 or not len(password) < 15: 
                messages.error(request,'Password must be 8 characters ')
                return render(request,'frontend/auth/sign-up.html',{'data':data})
            if not len(confirm_password) > 7 or not len(confirm_password) < 15: 
                messages.error(request,'Confirm Password must be 8 characters ')
                return render(request,'frontend/auth/sign-up.html',{'data':data})
            if User.objects.filter(email=email_instance).exists():
                messages.info(request,'Email Id  Already Exists !')
                return render(request,'frontend/auth/sign-up.html',{'data':data})
            if password == confirm_password:
                obj=User.objects.create(email=email_instance,roll="2")
                obj.set_password(password)
                otp=random.randint(1000,9999)
                obj.OTP=otp
                obj.save()
                slug=obj.slug
                subject='Verification OTP'
                message=f"Your Verification OTP is:{otp}"
                sendmail(subject,message,email)
                messages.info(request,'Verifivation Otp send in your email !')
                return redirect('/signup/otp/verification/'+str(slug))
            else:
                messages.error(request,'Password Does Not Match !')
                return render(request,'frontend/auth/sign-up.html',{'data':data}) 
        return render(request,'frontend/auth/sign-up.html') 
    except:
        messages.error(request,'Something Went Wrong!')
        return render(request,'frontend/auth/sign-up.html',{'data':data})
    

def sign_up_otp(request,slug):
    try:
        if request.method=='POST':
            data=request.POST
            first_digit=request.POST.get('first_digit')
            second_digit=request.POST.get('second_digit')   
            third_digit=request.POST.get('third_digit')
            fourth_digit=request.POST.get('fourth_digit')
            if first_digit == '' or second_digit == '' or third_digit == '' or fourth_digit == '':
                messages.info(request,'please enter otp!')
                return render(request, 'frontend/auth/signup_otp.html', {'data':data ,'slug':slug})
            if first_digit and second_digit and third_digit and fourth_digit:
                otp=first_digit+second_digit+third_digit+fourth_digit
                user = User.objects.get(slug=slug)
                if user.OTP == otp:
                    user.OTP = ''
                    user.save()
                    messages.success(request,'OTP is matched now create the profile')
                    return redirect('/profileSetUp/'+str(slug))      
                else:
                    messages.error(request,"OTP not matched")
                    return render(request, 'frontend/auth/signup_otp.html', {'data':data ,'slug':slug} )
            return render(request, 'frontend/auth/signup_otp.html', {'data':data,'slug':slug} )
        return render(request, 'frontend/auth/signup_otp.html', {'slug':slug})
    except:
        messages.error(request,'Something Went Wrong')
        return redirect('home')


def resend_sign_up_otp(request,slug):
    try:
        otp=random.randint(1000,9999)
        user = User.objects.get(slug=slug)
        user.OTP = otp
        user.save()
        email=user.email
        subject=' Resend Verification OTP'
        message=f"Your Verification OTP is:{otp}"
        sendmail(subject,message,email)
        messages.success(request,'Resend OTP Send ')
        return redirect('/signup/otp/verification/'+str(slug))
    except:
        messages.error(request,"OTP not matched")
        return render(request, 'frontend/auth/signup_otp.html',{'slug':slug} )


@login_required(login_url='/')
def logoutView(request):
    try:
        auth.logout(request)
        messages.success(request,'Successfully logout !')
        return redirect('/')
    except:
        messages.error(request,'Something Went Wrong')
        return redirect('home')


def profileSetup(request,slug):
    try:
        try:
            country=Country.objects.all()
            if request.method=='POST':
                data=request.POST
                fname=request.POST.get('fname')
                lname=request.POST.get('lname')
                contact=request.POST.get('contact')
                nationality=request.POST.get('nationality')
                country=request.POST.get('country')
                date=request.POST.get('date')   
                img=request.FILES.get('image')
                user=User.objects.get(slug=slug)
                countrys=Country.objects.all()
                if img and  img.name.split('.')[-1] not in ['png','jpeg','jpg']:
                    messages.error(request,'Imgae must be in png ,jpg ,jpeg format')
                    return render(request,'frontend/auth/profile-setup.html',{'data':data,'country':countrys,'user':user})
                if fname == '' or fname.isspace():
                    messages.error(request,'First Name Required!! ')
                    return render(request,'frontend/auth/profile-setup.html',{'data':data,'country':countrys,'user':user})
                if len(fname)>20:
                    messages.error(request,'First Name must be in 20 characters!! ')
                    return render(request,'frontend/auth/profile-setup.html',{'data':data,'country':countrys,'user':user})
                if lname == '' or lname.isspace():
                    messages.error(request,'Last Name Required!! ')
                    return render(request,'frontend/auth/profile-setup.html',{'data':data,'country':countrys,'user':user})
                if len(lname)>20:
                    messages.error(request,'Last Name must be in 20 characters!! ')
                    return render(request,'frontend/auth/profile-setup.html',{'data':data,'country':countrys,'user':user})
                if contact =='' or contact.isspace():
                    messages.error(request,'Contact Nunber Required!! ')
                    return render(request,'frontend/auth/profile-setup.html',{'data':data,'country':country,'user':user})
                if not len(contact) >9 or not len(contact) < 16: 
                    messages.error(request,'contact must be in 10-15 digit ')
                    return render(request,'frontend/auth/profile-setup.html',{'data':data,'country':countrys,'user':user})
                if not nationality:
                    messages.error(request,'nationality required')
                    return render(request,'frontend/auth/profile-setup.html',{'data':data,'country':countrys,'user':user})
                if not country:
                    messages.error(request,'country required')
                    return render(request,'frontend/auth/profile-setup.html',{'data':data,'country':countrys,'user':user})
                if not date:
                    messages.error(request,'Date of birth required')
                    return render(request,'frontend/auth/profile-setup.html',{'data':data,'country':countrys,'user':user})
                usr_obj=User.objects.get(slug=slug)
                usr_obj.first_name=fname
                usr_obj.last_name=lname
                usr_obj.country_id=country
                usr_obj.nationlity_id=nationality 
                if img:
                    usr_obj.image=img
                usr_obj.contact=contact
                # usr_obj.date=date
                usr_obj.DOB=date
                usr_obj.is_profile_setup=True
                usr_obj.save()
                if not NotificationSetting.objects.filter(user_id = usr_obj.id).exists():
                    NotificationSetting.objects.create(user_id = usr_obj.id)
                auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request,'Successfully User Porfile Setup !')
                return redirect('/')  
            else:
                user=User.objects.get(slug=slug)
                return render(request,'frontend/auth/profile-setup.html',{'country':country,'slug':slug ,'user':user})
        except:
            user=User.objects.get(slug=slug)
            countrys=Country.objects.all()
            messages.info(request,'Something went wrong')
            return render(request,'frontend/auth/profile-setup.html',{'country':countrys,'slug':slug ,'user':user})
    except:
        messages.error(request,'Something Went Wrong')
        return redirect('home')


def forgetPass(request):
    try:
        if request.method=="POST":
            data=request.POST
            email=request.POST.get('email')
            if email =="" or email.isspace():
                messages.error(request,'Please Enter The Email')
                return render(request,'frontend/auth/forgot-password.html',{'data':data})
            if '@' not in email:
                messages.error(request,'Please Enter the valid email')
                return render(request,'frontend/auth/forgot-password.html',{'data':data})
            if '.' not in email:
                messages.error(request,'Please Enter the valid email')
                return render(request,'frontend/auth/forgot-password.html',{'data':data})
            if User.objects.filter(email=email,is_active=True, roll='2').exists(): 
                usr= User.objects.get(email=email)
                otp=random.randint(1000,9999)
                usr.OTP=otp
                usr.save()
                subject='Forgot Password '
                message=f"Your Forgot Password OTP is:{otp}"
                sendmail(subject,message,email)
                messages.success(request,'OTP Send in Your email')
                return redirect('/OTPVerification/'+str(usr.slug))
            else:
                messages.info(request,'User Email Id Does Not Register')
                return render(request,'frontend/auth/forgot-password.html',{'data':data})
        else:
            return render(request,'frontend/auth/forgot-password.html')
    except:
        messages.error(request,'Something Went Wrong')
        return redirect('home')


def OTPVerification(request,slug):
    try:
        if request.method=='POST':
            data=request.POST
            first_digit=request.POST.get('first_digit')
            second_digit=request.POST.get('second_digit')
            third_digit=request.POST.get('third_digit')
            fourth_digit=request.POST.get('fourth_digit')
            if first_digit == '' or second_digit == '' or third_digit == '' or fourth_digit == '':
                messages.info(request,'please enter otp!')
                return render(request, 'frontend/auth/forgot_password_otp.html', {'data':data,'slug':slug})
            if first_digit and second_digit and third_digit and fourth_digit:
                otp=first_digit+second_digit+third_digit+fourth_digit
                user = User.objects.get(slug=slug)
                if user.OTP ==  otp:
                    user.OTP = ''
                    user.save()
                    return redirect('/changeForgetPass/' + str(slug)) 
                else:
                    messages.error(request,"OTP not matched")
                    return render(request, 'frontend/auth/signup_otp.html', {'data':data,'slug':slug} )
            else:
                return render(request, 'frontend/auth/forgot_password_otp.html', {'data':data,'slug':slug} )
        return render(request, 'frontend/auth/forgot_password_otp.html', {'slug':slug})
    except:
        messages.error(request,'Something Went Wrong')
        return redirect('home')
    

def changeForgetPass(request,slug):
    try:
        if request.method=='POST':
            data=request.POST
            new_password=request.POST.get('new_password')
            confirm_password=request.POST.get('confirm_password')
            if new_password == '' or new_password.isspace():
                messages.error(request,'Please Enter The New password ')
                return render(request,'frontend/auth/change_forgot_password.html',{'data':data})
            if confirm_password == '' or confirm_password.isspace():
                messages.error(request,'Please Enter The confirm password ')
                return render(request,'frontend/auth/change_forgot_password.html',{'data':data})
            if not len(new_password) > 7 or not len(new_password) < 15: 
                messages.error(request,'Password must be 8 characters ')
                return render(request,'frontend/auth/change_forgot_password.html',{'data':data})
            if not len(confirm_password) > 7 or not len(confirm_password) < 15: 
                messages.error(request,'Confirm Password must be 8 characters ')
                return render(request,'frontend/auth/change_forgot_password.html',{'data':data})
            if new_password == confirm_password:
                    usr_obj=User.objects.get(slug=slug)
                    usr_obj.set_password(confirm_password)
                    usr_obj.save()
                    messages.info(request,'Password Change Successfully !')
                    return redirect('/login/')
            else:
                messages.info(request,'Password Does Not Match !')
                return render(request,'frontend/auth/change_forgot_password.html',{'data':data})
        else:
            return render(request,'frontend/auth/change_forgot_password.html',{'slug':slug})
    except:
        messages.error(request,'Something Went Wrong')
        return redirect('home')


def resendOTP(request,slug):
    try:
        otp=random.randint(1000,9999)
        user = User.objects.get(slug=slug)
        user.OTP = otp
        user.save()
        email=user.email
        subject=' Resend Forgot Password OTP'
        message=f"Your Resend Forgot Password OTP is:{otp}"
        sendmail(subject,message,email)
        messages.success(request,'Resend OTP Send ')
        return redirect('/OTPVerification/' + str(slug))
    except:
        messages.error(request,'Something Went Wrong')
        return redirect('home')


def aboutUs(request):
    try:
        try:
            about=AboutUs.objects.get(id=1)
        except:
            about=None
        try:
            social=SocialSetting.objects.all()
        except:
            social=None
        return render(request,'frontend/cms/about-us.html',{'aboutus':about,'sociallink':social})
    except:
        messages.success(request,'Something Went Wrong')
        return redirect('home')


def contactUs(request):
    try: 
        contact_data=ContactUsPage.objects.get(id=1)
        if request.method == "POST":
            data=request.POST
            name=data.get('name')
            email=data.get('email')
            message=data.get('message')
            contact=ContactUs.objects.create(name=name,email=email,query=message)
            contact.save()
            subject="Contact Us"
            message=f"Hello {name} We have received your enquiry."
            sendmail(subject,message,email)
            messages.success(request,'Your Message send Succesfully!!')
            return render(request,'frontend/cms/contact-us.html',{'contact_data':contact_data })
        return render(request,'frontend/cms/contact-us.html',{'contact_data':contact_data})
    except:
        messages.error(request,'Something Went Wrong')
        return render(request,'frontend/cms/contact-us.html',{'contact_data':contact_data ,'data':data})


def privacyPolicy(request):
    try:
        privacy=PrivacyPolicy.objects.get(id=1)
    except:
        privacy=None
    try:
        social=SocialSetting.objects.all()
    except:
        social=None
    return render(request,'frontend/cms/privacy-policy.html',{'privacy':privacy,'sociallink':social})


def termConditions(request):
    try:
        term=TermConditon.objects.get(id=1)
        social=SocialSetting.objects.all()
        return render(request,'frontend/cms/terms-conditions.html',{'termcondtion':term,'sociallink':social})
    except:
        messages.error(request,'Something Went Wrong')
        return redirect('home')


def frequentlyAskQuetion(request):
    try:
        social=SocialSetting.objects.all()
        faq_obj=FAQ.objects.all()
        return render(request,'frontend/cms/faq.html',{'sociallink':social,'faqs':faq_obj})
    except:
        messages.error(request,'Something Went Wrong')
        return redirect('home')


def upcoming_event_detail(request):
    try:
        current_date=datetime.now()
        upcoming_event=EventCreate.objects.filter(start_time__gte = current_date, is_active='1',event_cancel='0',ticket_create_status=False).order_by('start_time')
        upcoming_event_count=EventCreate.objects.filter(start_time__gte = current_date, is_active='1').count() 
        category = EventCategory.objects.filter(is_active=True)
        ticket=EventTicketCreate.objects.filter(ticket_event_id__in=upcoming_event)
        favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
        data = {
                "upcoming_event":upcoming_event, 
                "category":category,
                "ticket":ticket, 
                "favouritees":favouritees}
        return render(request,'frontend/upcoming_event/event-listing.html',data)
    except:
        messages.error(request,'Something Went Wrong')
        return redirect('home')


def filter_upcoming_event_detail(request):
    try:
        if request.method == "POST":
            location = request.POST.get('location')
            category=request.POST.get('category')
            event_type=request.POST.get('event_type')
            start_time=request.POST.get('start_time')
            try:
                dt = datetime.fromisoformat(start_time)
            except:
                dt=None
            current_date=datetime.now()
        # try:
            if location and category and event_type and dt:
                fliter_data=EventCreate.objects.filter(Q(address__icontains=location) & Q(category_id=category) & Q(privacy=event_type) 
                        & Q(start_time__iexact=dt),start_time__gte = current_date, is_active='1',event_cancel='0',ticket_create_status=False).order_by('start_time')
                
                category = EventCategory.objects.filter(is_active=True)
                ticket=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                
                return render(request,'frontend/upcoming_event/filter-event-listing.html', {'category':category,
                'fliter_data':fliter_data,'ticket':ticket,"favouritees":favouritees})
            
            elif location and category:
                fliter_data=EventCreate.objects.filter(Q(address__icontains=location) & Q(category_id=category),
                        start_time__gte = current_date, is_active='1',event_cancel='0',ticket_create_status=False).order_by('start_time')
                category = EventCategory.objects.filter(is_active=True)
                ticket=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                
                return render(request,'frontend/upcoming_event/filter-event-listing.html', {'category':category,
                'fliter_data':fliter_data,'ticket':ticket,"favouritees":favouritees})

            elif location and event_type:
                fliter_data=EventCreate.objects.filter(Q(address__icontains=location) & Q(privacy=event_type),
                        start_time__gte = current_date, is_active='1',event_cancel='0',ticket_create_status=False).order_by('start_time')
                category = EventCategory.objects.filter(is_active=True)
                ticket=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
            
                return render(request,'frontend/upcoming_event/filter-event-listing.html', {'category':category,
                'fliter_data':fliter_data,'ticket':ticket,"favouritees":favouritees})

            elif location and dt:
                fliter_data=EventCreate.objects.filter(Q(address__icontains=location) & Q(start_time__iexact=dt),
                        start_time__gte = current_date, is_active='1',event_cancel='0',ticket_create_status=False).order_by('start_time')
                category = EventCategory.objects.filter(is_active=True)
                ticket=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                
                return render(request,'frontend/upcoming_event/filter-event-listing.html', {'category':category,
                'fliter_data':fliter_data,'ticket':ticket,"favouritees":favouritees})

            elif category and event_type:
                fliter_data=EventCreate.objects.filter(Q(category_id=category) & Q(privacy=event_type),
                        start_time__gte = current_date, is_active='1',event_cancel='0',ticket_create_status=False).order_by('start_time')
            
                category = EventCategory.objects.filter(is_active=True)
                ticket=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
            
                return render(request,'frontend/upcoming_event/filter-event-listing.html', {'category':category,
                'fliter_data':fliter_data,'ticket':ticket,"favouritees":favouritees})

            elif category and dt:
                fliter_data=EventCreate.objects.filter(Q(category_id=category) & Q(start_time__iexact=dt),
                        start_time__gte = current_date, is_active='1',event_cancel='0',ticket_create_status=False).order_by('start_time')
                category = EventCategory.objects.filter(is_active=True)
                ticket=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
            
                return render(request,'frontend/upcoming_event/filter-event-listing.html', {'category':category,
                'fliter_data':fliter_data,'ticket':ticket,"favouritees":favouritees})

            elif event_type and dt:
                fliter_data=EventCreate.objects.filter(Q(privacy=event_type) & Q(start_time__iexact=dt),
                        start_time__gte = current_date, is_active='1',event_cancel='0',ticket_create_status=False).order_by('start_time')
                category = EventCategory.objects.filter(is_active=True)
                ticket=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
            
                return render(request,'frontend/upcoming_event/filter-event-listing.html', {'category':category,
                'fliter_data':fliter_data,'ticket':ticket,"favouritees":favouritees})

            else:
                if category:
                    fliter_data=EventCreate.objects.filter(category_id=category,
                        start_time__gte = current_date, is_active='1',event_cancel='0',ticket_create_status=False).order_by('start_time')
                    category = EventCategory.objects.filter(is_active=True)
                    ticket=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                    favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                    
                    return render(request,'frontend/upcoming_event/filter-event-listing.html', {'category':category,
                    'fliter_data':fliter_data,'ticket':ticket,"favouritees":favouritees})
                
                elif location:
                    fliter_data=EventCreate.objects.filter(address__icontains=location,
                        start_time__gte = current_date, is_active='1',event_cancel='0',ticket_create_status=False).order_by('start_time')
                    category = EventCategory.objects.filter(is_active=True)
                    ticket=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                    favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
            
                    return render(request,'frontend/upcoming_event/filter-event-listing.html', {'category':category,
                    'fliter_data':fliter_data,'ticket':ticket,"favouritees":favouritees})

                elif event_type:
                    fliter_data=EventCreate.objects.filter(privacy=event_type,
                        start_time__gte = current_date, is_active='1',event_cancel='0',ticket_create_status=False).order_by('start_time')
                    category = EventCategory.objects.filter(is_active=True)
                    ticket=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                    favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                    return render(request,'frontend/upcoming_event/filter-event-listing.html', {'category':category,
                    'fliter_data':fliter_data,'ticket':ticket,"favouritees":favouritees})

                elif dt:           
                    fliter_data=EventCreate.objects.filter(start_time__iexact=dt,
                        start_time__gte = current_date, is_active='1',event_cancel='0',ticket_create_status=False).order_by('start_time')
                   
                    category = EventCategory.objects.filter(is_active=True)
                    ticket=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                    favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                    return render(request,'frontend/upcoming_event/filter-event-listing.html', {'category':category,
                    'fliter_data':fliter_data,'ticket':ticket,"favouritees":favouritees})
        current_date=datetime.now()
        upcoming_event=EventCreate.objects.filter(start_time__gte = current_date, event_cancel='0',is_active='1',ticket_create_status=False).order_by('start_time')
        ticket=EventTicketCreate.objects.filter(ticket_event_id__in=upcoming_event)
        category = EventCategory.objects.filter(is_active=True)
        favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
        data = {
                "upcoming_event":upcoming_event, 
                "category":category,       
                "ticket":ticket,
                "favouritees":favouritees}
        return render(request,'frontend/upcoming_event/event-listing.html', data)
    except:
        messages.error(request,'Something Went Wrong')
        return redirect('home')
           

def search_upcoming_event(request):
    try:
        if request.method == "POST":
            search = request.POST.get('search')
            current_date=datetime.now()
            try:
                if search:
                    fliter_data=EventCreate.objects.filter(evnet_name__icontains=search ,start_time__gte = current_date, is_active='1',event_cancel='0',ticket_create_status=False)
                    ticket=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                    category=EventCategory.objects.filter(is_active=True)
                    favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                    return render(request,'frontend/upcoming_event/filter-event-listing.html', {'fliter_data':fliter_data,
                    'ticket':ticket,'category':category,"favouritees":favouritees})
                else:
                    category=EventCategory.objects.filter(is_active=True)
                    return render(request,'frontend/upcoming_event/filter-event-listing.html',{'category':category})
            except:
                category=EventCategory.objects.filter(is_active=True)
                return render(request,'frontend/upcoming_event/filter-event-listing.html',{'category':category})
        else:
            category=EventCategory.objects.filter(is_active=True)
            return render(request,'frontend/upcoming_event/filter-event-listing.html',{'category':category})
    except:
        messages.error(request,'Something Went Wrong')
        return redirect('home')


# def individual_upcoming_event_detail(request,slug):
   
  
#     event_detail=EventCreate.objects.get(slug=slug)
#     ticket=EventTicketCreate.objects.filter(ticket_event_id=event_detail.id)
#     food_cost=FoodInEvent.objects.filter(event_id=event_detail)
   
  
#     return render(request,'frontend/upcoming_event/event-details.html',{'event_detail':event_detail,
#                 'ticket':ticket,'food_cost':food_cost})


def category_event_listing(request):
    try:
        # Event_data=EventCreate.objects.filter(is_active='1')
    # id__in = list(ticket.values_list("ticket_event_id", flat=True),ticket_create_status=True),
        # ticket=EventTicketCreate.objects.filter(ticket_event_id__in=Event_data)
        ticket=EventTicketCreate.objects.all()
        Event_data=EventCreate.objects.filter(is_active="1",event_cancel='0')
        ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=Event_data)
        category_event=EventCategory.objects.filter(is_active =True)
        favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
        data={
        
            "Event_data":Event_data,
            "ticket":ticket,
            'all_category':category_event,'favouritees':favouritees,'ticket_price':ticket_price
        }
        return render(request,'frontend/category_wise_event/category_all_listing.html',data)
    except:
        messages.error(request,'Something Went Wrong')
        return redirect('home')


def category_wise_listing(request,category):
    try:
        event_category=EventCategory.objects.filter(category=category, is_active=True)
        # event=EventCreate.objects.filter(category_id__in=event_category,is_active='1')
        ticket=EventTicketCreate.objects.all()
        event=EventCreate.objects.filter(is_active='1',category_id__in=event_category,event_cancel='0')
        ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=event)
        # ticket=EventTicketCreate.objects.filter(ticket_event_id__in=event)
        all_category=EventCategory.objects.filter(is_active =True)
        favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
        slug= category

        return render(request,'frontend/category_wise_event/category_wise_listing.html',
        {'event':event,'event_category':event_category,
        'ticket':ticket,'all_category':all_category,"slug":slug,'favouritees':favouritees,'ticket_price':ticket_price})
    except:
        messages.error(request,'Something Went Wrong')
        return redirect('home')
    
    


def filter_category_listing_event_detail(request):
    try:
        if request.method == "POST":
            location = request.POST.get('location')
            category=request.POST.get('category')
            event_type=request.POST.get('event_type')
            start_time=request.POST.get('start_time')
            try:
                dt = datetime.fromisoformat(start_time)
            except:
                dt = None
            try:
                if location and category and event_type and dt:
                    fliter_data=EventCreate.objects.filter(Q(address__icontains=location) & Q(category_id=category) & Q(privacy=event_type) & Q(start_time=dt), event_cancel='0',is_active='1').order_by('start_time')             
                    category_name = EventCategory.objects.filter(category=category)  
                    category=EventCategory.objects.filter(is_active=True)
                    ticket=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                    favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                    slug= category
                    ticket=EventTicketCreate.objects.all()
                    event=EventCreate.objects.filter(id__in = list(ticket.values_list("ticket_event_id", flat=True)), 
                    is_active='1', ticket_create_status=True,category_id=category)
                    ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)

                    return render(request,'frontend/category_wise_event/category_filter_listing.html', {'all_category': category,
                    'fliter_data':fliter_data,'ticket':ticket, "slug":slug,'favouritees':favouritees,'ticket_price':ticket_price})
                
                
                
                elif location:
                    fliter_data=EventCreate.objects.filter(category_id=category,event_cancel='0',is_active='1' ,address__icontains=location).order_by('start_time')
                    category_name = EventCategory.objects.filter(category=category)
                    category=EventCategory.objects.filter(is_active=True)
                    # ticket=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                    favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                    slug= category
                    ticket=EventTicketCreate.objects.all()
                    # event=EventCreate.objects.filter(id__in = list(ticket.values_list("ticket_event_id", flat=True)), 
                    # is_active='1', ticket_create_status=True,category_id=category)
                    ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                
                    return render(request,'frontend/category_wise_event/category_filter_listing.html', {'all_category': category,
                    'fliter_data':fliter_data,'ticket':ticket,"slug":slug,'favouritees':favouritees,'ticket_price':ticket_price})

                
                elif  event_type:
                    fliter_data=EventCreate.objects.filter(category_id=category,is_active='1',event_cancel='0',privacy=event_type)
                    category_name = EventCategory.objects.filter(category=category)
                    category=EventCategory.objects.filter(is_active=True)
                    # ticket=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                    favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                    slug= category
                    ticket=EventTicketCreate.objects.all()
                    # event=EventCreate.objects.filter(id__in = list(ticket.values_list("ticket_event_id", flat=True)), 
                    # is_active='1', ticket_create_status=True,category_id=category)
                    ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                
                    return render(request,'frontend/category_wise_event/category_filter_listing.html', {'all_category': category,
                    'fliter_data':fliter_data ,'ticket':ticket,"slug":slug,'favouritees':favouritees,'ticket_price':ticket_price})

                elif dt :
                    fliter_data=EventCreate.objects.filter(is_active='1',event_cancel='0',start_time__iexact=dt, )
                    category_name = EventCategory.objects.filter(category=category)
                    category=EventCategory.objects.filter(is_active=True)
                    # ticket=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                    favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                    slug= category
                    ticket=EventTicketCreate.objects.all()
                    # event=EventCreate.objects.filter(id__in = list(ticket.values_list("ticket_event_id", flat=True)), 
                    # is_active='1', ticket_create_status=True,category_id=category)
                    ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)

                    return render(request,'frontend/category_wise_event/category_filter_listing.html', {'all_category':category,'fliter_data':fliter_data,
                    'ticket':ticket,"slug":slug,'favouritees':favouritees,'ticket_price':ticket_price})
                
                elif category:                
                    fliter_data=EventCreate.objects.filter(is_active='1',event_cancel='0',category_id=category)
                    
                    
                    category=EventCategory.objects.filter(is_active=True)
                    # ticket=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                    favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                    slug= category
                    ticket=EventTicketCreate.objects.all()
                    # event=EventCreate.objects.filter(id__in = list(ticket.values_list("ticket_event_id", flat=True)), 
                    # is_active='1', ticket_create_status=True,category_id=category)
                    ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                    
            
                    return render(request,'frontend/category_wise_event/category_filter_listing.html', {'all_category': category,
                    'fliter_data':fliter_data ,'ticket':ticket,"slug":slug,'favouritees':favouritees,'ticket_price':ticket_price})

            except:
                pass
        
        
        current_date=datetime.now()
        category_event=EventCreate.objects.filter(event_cancel='0',is_active='1').order_by('start_time')
        # ticket=EventTicketCreate.objects.filter(ticket_event_id__in=category_event)
    
        category_name = EventCategory.objects.filter(category=category)
        category=EventCategory.objects.filter(is_active=True)
        favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
        ticket=EventTicketCreate.objects.all()
        # event=EventCreate.objects.filter(id__in = list(ticket.values_list("ticket_event_id", flat=True)), 
        # is_active='1', ticket_create_status=True,category_id=category)
        ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=category_event)
    
        slug= category
    
        data = {
                "category_event":category_event, 
                "all_category": category,
                "ticket":ticket,
                "slug":slug,
                "favouritees":favouritees,
                "ticket_price":ticket_price}
        return render(request,'frontend/category_wise_event/category_filter_listing.html', data)
    except:
        messages.error(request,'Something Went Wrong')
        return redirect('home')




# def individual_category_event_detail(request,slug):
#     event_detail=EventCreate.objects.get(slug=slug)
#     ticket=EventTicketCreate.objects.filter(ticket_event_id=event_detail.id)
#     food_cost=FoodInEvent.objects.filter(event_id=event_detail)
#     slug=slug
  
#     return render(request,'frontend/category_wise_event/event-details.html',{'event_detail':event_detail,
#                 'ticket':ticket,'food_cost':food_cost,'slug':slug})



def search_category_event(request):
    try:
        if request.method == "POST":
                search = request.POST.get('search')
                try:
                    if search:
                        fliter_data=EventCreate.objects.filter(evnet_name__icontains=search,event_cancel='0',is_active='1')
                    
                        category = EventCategory.objects.filter(is_active=True)
                        # ticket=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                        favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                        ticket=EventTicketCreate.objects.all()
                        # event=EventCreate.objects.filter(id__in = list(ticket.values_list("ticket_event_id", flat=True)), 
                        # is_active='1', ticket_create_status=True,category_id=category)
                        ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                        return render(request,'frontend/category_wise_event/category_filter_listing.html',
                        {'fliter_data':fliter_data,'ticket':ticket,'all_category':category,'favouritees':favouritees,'ticket_price':ticket_price})
                    else: 
                        category = EventCategory.objects.filter(is_active=True)                      
                        return render(request,'frontend/category_wise_event/category_filter_listing.html',{'all_category':category})

                except:
                    category = EventCategory.objects.filter(is_active=True)                      
                    return render(request,'frontend/category_wise_event/category_filter_listing.html',{'all_category':category})
        else:
            category = EventCategory.objects.filter(is_active=True)                      
            return render(request,'frontend/category_wise_event/category_filter_listing.html',{'all_category':category})
    except:
        messages.error(request,'Something Went Wrong')
        return render(request,'frontend/category_wise_event/category_wise_listing.html',{'all_category':category})






def filter_category_all_listing_event_detail(request):
    try:
        if request.method == "POST":
            location = request.POST.get('location')
            category=request.POST.get('category')
            event_type=request.POST.get('event_type')
            start_time=request.POST.get('start_time')
            try:
                dt = datetime.fromisoformat(start_time)
            except:
                dt= None
        
            try:
                if location and category and event_type and dt:
                    fliter_data=EventCreate.objects.filter(Q(address__icontains=location) & Q(category_id=category) & Q(privacy=event_type) 
                            & Q(start_time__iexact=dt),event_cancel='0',is_active='1').order_by('start_time')
                    category = EventCategory.objects.filter(is_active=True)
                    ticket=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                    
                    favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                    ticket=EventTicketCreate.objects.all()
                        # event=EventCreate.objects.filter(id__in = list(ticket.values_list("ticket_event_id", flat=True)), 
                        # is_active='1', ticket_create_status=True,category_id=category)
                    ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
        
                    return render(request,'frontend/category_wise_event/category_all_filter_listing.html', {'all_category': category,
                    'fliter_data':fliter_data,'ticket':ticket,'favouritees':favouritees,'ticket_price':ticket_price})
                elif category and event_type:
                    fliter_data=EventCreate.objects.filter(Q(category_id=category) & Q(privacy=event_type),
                           event_cancel='0', is_active='1').order_by('start_time')
                
                    category = EventCategory.objects.filter(is_active=True)
                    # ticket=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                    favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                    ticket=EventTicketCreate.objects.all()
                        # event=EventCreate.objects.filter(id__in = list(ticket.values_list("ticket_event_id", flat=True)), 
                        # is_active='1', ticket_create_status=True,category_id=category)
                    ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                
            
                    return render(request,'frontend/category_wise_event/category_all_filter_listing.html', {'all_category': category,
                    'fliter_data':fliter_data ,'ticket':ticket,'favouritees':favouritees,'ticket_price':ticket_price})
                
            
                elif category and dt:
                   
                    fliter_data=EventCreate.objects.filter(Q(category_id=category) & Q(start_time__iexact=dt),
                          event_cancel='0',  is_active='1').order_by('start_time')
                 
                    category = EventCategory.objects.filter(is_active=True)
                  
                    # ticket=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                    favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                    ticket=EventTicketCreate.objects.all()
                        # event=EventCreate.objects.filter(id__in = list(ticket.values_list("ticket_event_id", flat=True)), 
                        # is_active='1', ticket_create_status=True,category_id=category)
                    ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
    
    
                    return render(request,'frontend/category_wise_event/category_all_filter_listing.html', {'all_category':category,'fliter_data':fliter_data,
                    'ticket':ticket,'favouritees':favouritees,'ticket_price':ticket_price})


                else:
                    if category:
                        fliter_data=EventCreate.objects.filter(category_id=category,event_cancel='0',
                        is_active='1').order_by('start_time')
                        category = EventCategory.objects.filter(is_active=True)
                        # ticket=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                        favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                        ticket=EventTicketCreate.objects.all()
                        # event=EventCreate.objects.filter(id__in = list(ticket.values_list("ticket_event_id", flat=True)), 
                        # is_active='1', ticket_create_status=True,category_id=category)
                        ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                
                        return render(request,'frontend/category_wise_event/category_all_filter_listing.html', {'all_category': category,
                        'fliter_data':fliter_data ,'ticket':ticket,'favouritees':favouritees,'ticket_price':ticket_price})
            except:
                pass
    
        category_event=EventCreate.objects.filter(event_cancel='0',is_active='1').order_by('start_time')
        # ticket=EventTicketCreate.objects.filter(ticket_event_id__in=category_event)
        category_name = EventCategory.objects.filter(category=category)
        category=EventCategory.objects.filter(is_active=True)
        favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
        ticket=EventTicketCreate.objects.all()
                        # event=EventCreate.objects.filter(id__in = list(ticket.values_list("ticket_event_id", flat=True)), 
                        # is_active='1', ticket_create_status=True,category_id=category)
        ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=category_event)
                
        data = {
                "category_event":category_event, 
                "all_category": category,
                "ticket":ticket,
                "favouritees":favouritees,
                "ticket_price":ticket_price}
        return render(request,'frontend/category_wise_event/category_all_filter_listing.html', data)
    except:
        messages.error(request,'Something Went Wrong')
        return redirect('home')



def search_category_all_event(request):
    try:
        if request.method == "POST":
            search = request.POST.get('search')
            current_date=datetime.now()
            try:
                if search:
                    fliter_data=EventCreate.objects.filter(evnet_name__icontains=search,event_cancel='0',is_active='1')
                    
                    category = EventCategory.objects.filter(is_active=True)
                    ticket=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                    favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                    ticket=EventTicketCreate.objects.all()
                    # event=EventCreate.objects.filter(id__in = list(ticket.values_list("ticket_event_id", flat=True)), 
                    # is_active='1', ticket_create_status=True,category_id=category)
                    ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                    return render(request,'frontend/category_wise_event/category_all_filter_listing.html', 
                    {'fliter_data':fliter_data,'ticket':ticket,'all_category':category,'favouritees':favouritees,'ticket_price':ticket_price})
                else:
                    category = EventCategory.objects.filter(is_active=True)
                    return render(request,'frontend/category_wise_event/category_all_filter_listing.html',{"all_category":category})
            except:
                category = EventCategory.objects.filter(is_active=True)
                return render(request,'frontend/category_wise_event/category_all_filter_listing.html',{"all_category":category})
        else:
            category = EventCategory.objects.filter(is_active=True)
            return render(request,'frontend/category_wise_event/category_all_filter_listing.html',{"all_category":category})
    except:
        messages.error(request, 'Something Went Wrong')
        return redirect('home')


@login_required(login_url='/login/')
def my_account(request):
    try:
        user_id = request.user.id
        user_detail=User.objects.get(id = user_id)
        country=Country.objects.all()
        nationality=Country.objects.all()
        user_interest_data = user_detail.interests
        try:
            user_interest = []
            jsonDec = json.decoder.JSONDecoder()
            user_interest_data = jsonDec.decode(user_interest_data)
            for interest in user_interest_data:
                user_interest.append(int(interest))
        except:
            user_interest = []
        interests_data = EventCategory.objects.all()
        interest_count = interests_data.count()
        private_event = PrivateEvent.objects.all()
        if request.method == "POST":
            profile_pic=request.FILES.get('profile_pic')
            first_name=request.POST.get('first_name')
            last_name=request.POST.get('last_name')
            contact=request.POST.get('contact')
            nationality=request.POST.get('nationality')
            location=request.POST.get('location')
            latitude=request.POST.get('latitude')
            longitude=request.POST.get('longitude')
            country=request.POST.get('country')
            dob=request.POST.get('dob')
            bio = request.POST.get("user_bio")
            interests_data = request.POST.getlist('user_interests')
            interests = json.dumps(interests_data)
            profession = request.POST.get('profession')

            if profile_pic and profile_pic.name.split('.')[-1] not in ['jpg','png','jpeg']:
                messages.error(request,'Image must be in jpeg ,png and jpg format')
                return redirect('/my-account/')
            if first_name =='' or first_name.isspace() :

                messages.error(request,'First name Are Required!!')
                return redirect('/my-account/')
            
            if len(first_name)>20:
                messages.error(request,'First name must be in 20 characters!!')
                return redirect('/my-account/')

            if last_name =='' or last_name.isspace():
                messages.error(request,'Last name Are Required!!')
                return redirect('/my-account/')

            if len(last_name)>20:
                messages.error(request,'last name must be in 20 characters!!')
                return redirect('/my-account/')

            if contact =='' or contact.isspace():
                messages.error(request,'contact Required!!')
                return redirect('/my-account/')


            if dob =='' or dob.isspace():
                messages.error(request,'Date Of Birth Required!!')
                return redirect('/my-account/')

            if not len(contact) >9 or not len(contact) < 16: 
                    messages.error(request,'contact must be in 10-16 digit ')
                    return redirect('/my-account/')

            if profile_pic:
                request.user.image=profile_pic
            request.user.first_name=first_name
            request.user.last_name=last_name
            request.user.contact=contact
            request.user.nationlity_id=nationality
            request.user.location=location
            request.user.latitude = latitude
            request.user.longitude = longitude
            request.user.country_id=country
            request.user.bio = bio
            request.user.profession = profession
            request.user.interests = interests
            if dob:
                request.user.DOB=dob
            request.user.is_profile_setup=True
           
            request.user.save()
            messages.success(request,'Update Successfully ')
            return redirect('my_account')
        return render(request, 'frontend/auth/my-profile.html',{'user_interest': user_interest, 'private_event': private_event, 'interest_count': interest_count, 'interests_data': interests_data, 'user_detail':user_detail,'country':country,'nationality':nationality})
    except:
        messages.success(request,'Something Went Wrong ')
        return redirect('/my-account/')
    
    
@login_required(login_url='/login/')
def change_password_account(request):
    try:
        if request.method == "POST":
            data=request.POST
            old_password=request.POST.get('old_password')
            new_password=request.POST.get('new_password')
            confirm_password=request.POST.get('confirm_password')
            if old_password == '' or old_password.isspace():
                messages.error(request, "Please enter  old valid password!")
                return render(request,'frontend/auth/change-password.html',{'data':data})
            if new_password == '' or new_password.isspace():
                messages.error(request, "Please enter New valid password!")
                return render(request,'frontend/auth/change-password.html',{'data':data})
            if confirm_password == '' or confirm_password.isspace():
                messages.error(request, "Please enter confirm valid password!")
                return render(request,'frontend/auth/change-password.html',{'data':data})
            if not len(new_password) > 7 or not len(new_password) < 15: 
                messages.error(request,'Password must be 8 characters ')
                return render(request,'frontend/auth/change-password.html',{'data':data})
            if not len(confirm_password) > 7 or not len(confirm_password) < 15: 
                messages.error(request,'Confirm Password must be 8 characters ')
                return render(request,'frontend/auth/change-password.html',{'data':data})
            if check_password(old_password,request.user.password):
                if new_password != confirm_password:
                    messages.error(request,'Password Does Not Match')
                    return render(request,'frontend/auth/change-password.html',{'data':data})
                request.user.set_password(confirm_password)
                request.user.save()
                auth.login(request,request.user)
                messages.success(request,'Password Change Successfully Done!!')
                return redirect('/change/password/account/')
            else:
                messages.error(request,' Old Password Does Not Match')
                return render(request,'frontend/auth/change-password.html',{'data':data})

        return render(request,'frontend/auth/change-password.html')
    except:
        messages.error(request,'Something Went Wrong')
        return redirect('/change/password/account/')
    

def trending_event_listing(request):
    try:
        ticket=EventTicketCreate.objects.all()
        trending_event=EventCreate.objects.filter(id__in = list(ticket.values_list("ticket_event_id", flat=True)), is_active='1', event_cancel='0',ticket_create_status=True)
        ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=trending_event)
        category = EventCategory.objects.filter(is_active=True)
        favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
        data={
            'ticket':ticket,
            'trending_event':trending_event,
            'ticket_price':ticket_price,
            'category':category,
            'favouritees':favouritees
        }
        return render(request,'frontend/trending_event/trending_event_listing.html',data)
    except:
        messages.error(request,'Something Went Wrong')
        return redirect('home')


def trending_event_filter(request):
    try:
        ticket=EventTicketCreate.objects.all()
        trending_event=EventCreate.objects.filter(id__in = list(ticket.values_list("ticket_event_id", flat=True)),event_cancel='0', is_active='1', ticket_create_status=True)
        ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=trending_event)
        category = EventCategory.objects.filter(is_active=True)
        favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
        if request.method == "POST":
            location = request.POST.get('location')
            category=request.POST.get('category')
            event_type=request.POST.get('event_type')
            start_time=request.POST.get('start_time')
            try:
                dt = datetime.fromisoformat(start_time)    
            except:
                dt=None
            if location and category and event_type and dt:
                fliter_data=EventCreate.objects.filter(Q(address__icontains=location) & Q(category_id=category) & Q(privacy=event_type) 
                        & Q(start_time__iexact=dt), is_active='1',event_cancel='0', ticket_create_status=True).order_by('start_time')
                category = EventCategory.objects.filter(is_active=True)
                ticket=EventTicketCreate.objects.all()
                ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                data={'fliter_data':fliter_data,'category':category,'ticket_price':ticket_price,'ticket':ticket,'favouritees':favouritees}
                return render(request,'frontend/trending_event/trending_event_filter.html',data)
                 
            elif location and category:
                fliter_data=EventCreate.objects.filter(Q(address__icontains=location) & Q(category_id=category), event_cancel='0',is_active='1', ticket_create_status=True).order_by('start_time')
                category = EventCategory.objects.filter(is_active=True)
                ticket=EventTicketCreate.objects.all()
                ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                data={'fliter_data':fliter_data,'category':category,'ticket_price':ticket_price,'ticket':ticket,'favouritees':favouritees}
                return render(request,'frontend/trending_event/trending_event_filter.html',data)

            elif location and event_type:
                fliter_data=EventCreate.objects.filter(Q(address__icontains=location) & Q(privacy=event_type),
                    ticket_create_status=True,event_cancel='0', is_active='1').order_by('start_time')
                category = EventCategory.objects.filter(is_active=True)
                ticket=EventTicketCreate.objects.all()
                ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                data={'fliter_data':fliter_data,'category':category,'ticket_price':ticket_price,'ticket':ticket,'favouritees':favouritees}
                return render(request,'frontend/trending_event/trending_event_filter.html',data)

            elif location and dt:
                fliter_data=EventCreate.objects.filter(Q(address__icontains=location) & Q(start_time__iexact=dt),
                    ticket_create_status=True,event_cancel='0', is_active='1').order_by('start_time')
                category = EventCategory.objects.filter(is_active=True)
                ticket=EventTicketCreate.objects.all()
                ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                data={'fliter_data':fliter_data,'category':category,'ticket_price':ticket_price,'ticket':ticket,'favouritees':favouritees}
                return render(request,'frontend/trending_event/trending_event_filter.html',data)

            elif category and event_type:
                fliter_data=EventCreate.objects.filter(Q(category_id=category) & Q(privacy=event_type),
                    ticket_create_status=True,event_cancel='0', is_active='1').order_by('start_time')
                category = EventCategory.objects.filter(is_active=True)
                ticket=EventTicketCreate.objects.all()
                ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                data={'fliter_data':fliter_data,'category':category,'ticket_price':ticket_price,'ticket':ticket,'favouritees':favouritees}
                return render(request,'frontend/trending_event/trending_event_filter.html',data)

            elif category and dt:
                fliter_data=EventCreate.objects.filter(Q(category_id=category) & Q(start_time__iexact=dt),
                    ticket_create_status=True,event_cancel='0', is_active='1').order_by('start_time')
                category = EventCategory.objects.filter(is_active=True)
                ticket=EventTicketCreate.objects.all()
                ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                data={'fliter_data':fliter_data,'category':category,'ticket_price':ticket_price,'ticket':ticket,'favouritees':favouritees}
                return render(request,'frontend/trending_event/trending_event_filter.html',data)

            elif event_type and dt:
                fliter_data=EventCreate.objects.filter(Q(privacy=event_type) & Q(start_time__iexact=dt),
                        ticket_create_status=True, event_cancel='0',is_active='1').order_by('start_time')
                category = EventCategory.objects.filter(is_active=True)
                ticket=EventTicketCreate.objects.all()
                ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                data={'fliter_data':fliter_data,'category':category,'ticket_price':ticket_price,'ticket':ticket,'favouritees':favouritees}
                return render(request,'frontend/trending_event/trending_event_filter.html',data)

            else:
                if category:
                
                    fliter_data=EventCreate.objects.filter(category_id=category,
                    ticket_create_status=True, event_cancel='0',is_active='1').order_by('start_time')
                    category = EventCategory.objects.filter(is_active=True)
                    ticket=EventTicketCreate.objects.all()
                    ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                    favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                    data={'fliter_data':fliter_data,'category':category,'ticket_price':ticket_price,'ticket':ticket,'favouritees':favouritees}
                    return render(request,'frontend/trending_event/trending_event_filter.html',data)
                    
                elif location:
                    fliter_data=EventCreate.objects.filter(address__icontains=location,
                    ticket_create_status=True,event_cancel='0', is_active='1').order_by('start_time')
                    category = EventCategory.objects.filter(is_active=True)
                    ticket=EventTicketCreate.objects.all()
                    ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                    favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                    data={'fliter_data':fliter_data,'category':category,'ticket_price':ticket_price,'ticket':ticket,'favouritees':favouritees}
                    return render(request,'frontend/trending_event/trending_event_filter.html',data)

                elif event_type:
                    fliter_data=EventCreate.objects.filter(privacy=event_type,
                    ticket_create_status=True,event_cancel='0', is_active='1').order_by('start_time')
                    category = EventCategory.objects.filter(is_active=True)
                    ticket=EventTicketCreate.objects.all()
                    ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                    favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                    data={'fliter_data':fliter_data,'category':category,'ticket_price':ticket_price,'ticket':ticket,'favouritees':favouritees}
                    return render(request,'frontend/trending_event/trending_event_filter.html',data)

                elif dt:           
                    fliter_data=EventCreate.objects.filter(start_time__iexact=dt,
                    ticket_create_status=True, event_cancel='0',is_active='1').order_by('start_time')
                    category = EventCategory.objects.filter(is_active=True)
                    ticket=EventTicketCreate.objects.all()
                    ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                    favouritees=Favourite.objects.filter(favourite=True).values_list('event_id',flat=True)
                    data={'fliter_data':fliter_data,'category':category,'ticket_price':ticket_price,'ticket':ticket,'favouritees':favouritees}
                    return render(request,'frontend/trending_event/trending_event_filter.html',data)
        data={'fliter_data':trending_event,'category':category,'ticket_price':ticket_price,'ticket':ticket,'favouritees':favouritees}
        return render(request,'frontend/trending_event/trending_event_filter.html',data)
    except:
        messages.error(request, "Something Went Wrong")
        return redirect('home')    


def event_individual_detail(request,slug):
    try:
        event_detail=EventCreate.objects.get(slug=slug)
        try:
            g = geocoder.ip('me') 
            lat_long = g.latlng
            lat_a = lat_long[0]
            long_a = lat_long[1]
            lat_b = event_detail.latitude
            long_b = event_detail.longitude
            lat_a = radians(lat_a)
            lat_b = radians(lat_b)
            delta_long = radians(long_a - long_b)
            cos_x = (
                sin(lat_a) * sin(lat_b) +
                cos(lat_a) * cos(lat_b) * cos(delta_long)
                )
            distance_data = acos(cos_x) * 3958.8 * 1.60934
            distance = "%.2f" % distance_data
        except:
            distance = ""
        if event_detail.offer_id:
            today_time = timezone.now()
            if today_time >= event_detail.offer.start_date and today_time <= event_detail.offer.end_date:
                event_offer = True   
            else:
                event_offer = False  
        else:         
            event_offer = False    
        ticket=EventTicketCreate.objects.filter(ticket_event_id=event_detail.id)
        ticket_id = []
        for id in ticket:
            ticket_id.append(id.ticket_event_id)
        attendees_data = UserTickets.objects.filter(event_id = event_detail.id).values('user_id').distinct() 
        attendees_count = attendees_data.count()
        food_cost=FoodInEvent.objects.filter(event_id=event_detail).exclude(food_id=None)
        like_count=EventLike.objects.filter(event_id=event_detail).count()
        try:
            seat_price = TicketSeats.objects.filter(event_id = event_detail.id).order_by('-seat_price').values('seat_price').last()
            ticket_start_from = seat_price['seat_price']
        except:
            ticket_start_from = None   
        avg=EventRating.objects.filter(event_id=event_detail).aggregate(avg_rating=Avg('rating'))
       
        res = dict()
        for key in avg:
            res[key] = round(avg[key],0) if avg[key] else 0
         
            event_detail.average_rating=res[key]
            event_detail.save()
        data={'event_offer': event_offer, 'distance': distance, 'ticket_start_from':ticket_start_from, 'ticket_id': ticket_id, 'attendees_count': attendees_count,'event_detail':event_detail,'ticket':ticket,'food_cost':food_cost,'like_count':like_count,'avg_rating': res[key]}
        return render(request,'frontend/trending_event/event-details.html',data)
    except:
        messages.error(request, "Something Went Wrong")
        return redirect('home')


def private_event(request):
    try:
        private_event_data = PrivateEvent.objects.all()
        private_event = []
        for data in private_event_data:
            private_emails = []
            private_emails.append(data.emails)
            if request.user.email in private_emails:
                private_event.append(data)
                private_emails.clear()
        tickets = EventTicketCreate.objects.all()
        ticket_id = []
        for ticket in tickets:
            ticket_id.append(ticket.ticket_event_id)
        return render(request,'frontend/private_event/private_events.html',{'ticket_id': ticket_id,  'private_event': private_event, 'tickets': tickets}) 
    except:
        messages.error(request, "Something Went Wrong")
        return redirect('my_account')


def private_event_detail(request,slug):
    try:
        event_detail=EventCreate.objects.get(slug=slug)
        ticket=EventTicketCreate.objects.filter(ticket_event_id=event_detail.id)
        ticket_id = []
        for id in ticket:
            ticket_id.append(id.ticket_event_id)
        attendees_data = UserTickets.objects.filter(event_id = event_detail.id).values('user_id').distinct() 
        attendees_count = attendees_data.count()
        food_cost=FoodInEvent.objects.filter(event_id=event_detail)
        like_count=EventLike.objects.filter(event_id=event_detail).count()
        avg=EventRating.objects.filter(event_id=event_detail).aggregate(avg_rating=Avg('rating'))
        res = dict()
        for key in avg:
            res[key] = round(avg[key],0) if avg[key] else 0
            event_detail.average_rating=res[key]
            event_detail.save()  
        data={'ticket_id': ticket_id, 'attendees_count': attendees_count,'event_detail':event_detail,'ticket':ticket,'food_cost':food_cost,'like_count':like_count,'avg_rating': res[key]}
        return render(request,'frontend/private_event/private_event_details.html',data)    
    except:
        messages.error(request, "Something Went Wrong")
        return redirect('my_account')


def show_attendees(request, slug):
    try:
        event_detail=EventCreate.objects.get(slug=slug)
        attendees_data = UserTickets.objects.filter(event_id = event_detail.id).values('user_id').distinct()
        user_data = []
        for data in attendees_data:
            data = User.objects.get(id = data['user_id'])
            user_data.append(data)
        attendees_count = attendees_data.count()
        return render(request,'frontend/event_booking/show_attendees.html',{'slug': slug, 'attendees_data': user_data, 'attendees_count': attendees_count})
    except:
        messages.error(request, 'Something Went Wrong')
        return redirect('home')

def search_trending_event(request):
    try:
        if request.method == "POST":
            search = request.POST.get('search')
            try:
                if search:
                    fliter_data=EventCreate.objects.filter(evnet_name__icontains=search,
                    is_active='1',ticket_create_status=True)
                    category = EventCategory.objects.filter(is_active=True)
                    ticket=EventTicketCreate.objects.all()
                    ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                    favouritees=Favourite.objects.filter(favourite=True,user_id=request.user.id).values_list('event_id',flat=True)
                    data={'fliter_data':fliter_data,'category':category,
                    'ticket_price':ticket_price,'ticket':ticket,'favouritees':favouritees}
                    return render(request,'frontend/trending_event/trending_event_filter.html',data)
                else:
                    category = EventCategory.objects.filter(is_active=True)
                    ticket=EventTicketCreate.objects.all()
                    favouritees=Favourite.objects.filter(favourite=True,user_id=request.user.id).values_list('event_id',flat=True)
                    
                    data={'category':category,'ticket':ticket,'favouritees':favouritees}
                    return render(request,'frontend/trending_event/trending_event_filter.html',data)
            except:
                category = EventCategory.objects.filter(is_active=True)
                ticket=EventTicketCreate.objects.all()
                ticket_price=EventTicketCreate.objects.filter(ticket_event_id__in=fliter_data)
                favouritees=Favourite.objects.filter(favourite=True,user_id=request.user.id).values_list('event_id',flat=True)
                data={'category':category,'ticket_price':ticket_price,'ticket':ticket,'favouritees':favouritees}
                return render(request,'frontend/trending_event/trending_event_filter.html',data)
        else:
            category = EventCategory.objects.filter(is_active=True)
            ticket=EventTicketCreate.objects.all()
            favouritees=Favourite.objects.filter(favourite=True,user_id=request.user.id).values_list('event_id',flat=True)
            data={'category':category,'ticket':ticket,'favouritees':favouritees}
            return render(request,'frontend/trending_event/trending_event_filter.html',data)
    except:
        messages.error(request, 'Something Went Wrong')
        return redirect('home')


def booking_events(request):
    try:
        current_date=datetime.now()
        upcoming_event=EventCreate.objects.filter(start_time__gte = current_date, is_active='1',event_cancel="0").order_by('start_time')
        data={'upcoming_event':upcoming_event}
        return render(request,'frontend/booking_events/booking-events.html',data)
    except:
        messages.error(request, 'Something Went Wrong')
        return redirect('home')


@login_required(login_url='/login/')
def invite_user(request,slug):
    try:
        invite_event=EventCreate.objects.get(slug=slug)
        invite_user=User.objects.filter(roll='2' ,is_active = True, is_superuser = False,is_profile_setup='1').exclude(id=request.user.id)
      
        data=InviteUser.objects.filter(invite_event_id=invite_event,send_user_id=request.user.id).values_list('invite_user_id', flat=True)
        if request.method == "POST":
            user_id = request.POST.get('user_id')
            event_id = request.POST.get('event_id')  
            invite_data = InviteUser.objects.filter(invite_user_id = user_id , invite_event_id=event_id)
            if invite_data:
                invite_data.delete()
            else:
                InviteUser.objects.create(invite_user_id = user_id , invite_event_id=event_id, invitation=True,send_user_id = request.user.id)
                try:
                    notification_data = NotificationSetting.objects.get(user_id = user_id)
                    tocken = notification_data.fcm_tocken
                    registration_ids  = [tocken]
                    send_notification(registration_ids , 'Golden Tick' , 'You have been invited')
                except:
                    pass
                return redirect('/invite-user/' + str(slug))
        return render(request,'frontend/booking_events/click-on-invite.html',{'invite_event':invite_event,'invite_user':invite_user,'data':data})
    except:
        messages.error(request, 'Something Went Wrong')
        return redirect('home')


@login_required(login_url='/login/')
def invite_user_detail(request,slug):
    try:
        user=User.objects.get(slug=slug)
        interests = EventCategory.objects.filter(is_active = True)
        birth_date = user.DOB
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        data=FollowUnfollow.objects.filter(Q(request=True)| Q(follow = True),receiver_id=user,sender_id=request.user.id).first()
        interest_data = []
        try:  
            interest_list = (user.interests).split(',')
            for list in interest_list:
                data_category = EventCategory.objects.get(id = list)
                interest_data.append(data_category)
        except:
            pass
        if request.method == "POST":
            user_id= request.POST.get('receiver')
            if data:
                data.delete()
                return redirect('invite_user_detail', str(slug))
            else:
                data=FollowUnfollow.objects.create(receiver_id=user_id,sender_id=request.user.id,request=True)
                try:
                    notification_data = NotificationSetting.objects.get(user_id = user.id)
                    tocken = notification_data.fcm_tocken
                    registration_ids  = [tocken]
                    send_notification(registration_ids , 'Golden Tick' , 'You are being followed')
                except:
                    pass
                return redirect('invite_user_detail', str(slug)) 
        return render(request,'frontend/booking_events/click-on-user-details.html',{'interest_data': interest_data, 'user':user,'data':data,'interests': interests,'age': age})
    except:
        messages.error(request, 'Something Went Wrong')
        return redirect('home')

@login_required(login_url='/login/')
def request_list(request):
    try:
        requests_list=FollowUnfollow.objects.filter(request=True,receiver_id=request.user.id)
        if request.method =="POST":
            user_id= request.POST.get('sender_id')
            is_accept= request.POST.get('is_accept')
            for i in requests_list:
                if is_accept =='1':
                    if not ChatRoom.objects.filter(Q(user_id_list=f'#{i.receiver_id}#-#{i.sender_id}#') | Q(user_id_list=f'#{i.sender_id}#-#{i.receiver_id}#')).exists():
                        user_ids= f'#{i.receiver_id}#-#{i.sender_id}#'
                        chat_room = ChatRoom.objects.create(user_id_list=user_ids)
                        ChatMessage.objects.create(chat_room_id=chat_room.id, send_by_id=i.sender_id, send_to_id=i.receiver_id)
                    i.follow = is_accept
                    i.request = False
                    i.save()
                    return redirect('my_follower')
                else:
                    is_accept =='0'
                    i.delete()
                    return redirect('request_list')
        return render(request,'frontend/follwer_request/my-request.html',{'requests_list':requests_list})
    except:
        messages.error(request, 'Something Went Wrong')
        return redirect('home')

@login_required(login_url='/login/')
def sender_user_detail(request,slug):
    try:
        sender_list=FollowUnfollow.objects.get(slug=slug)
        interests = EventCategory.objects.filter(is_active = True)
        birth_date = sender_list.sender.DOB
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        interest_data = []
        try:  
            interest_list = (sender_list.sender.interests).split(',')
            for list in interest_list:
                data_category = EventCategory.objects.get(id = list)
                interest_data.append(data_category)
        except:
            pass
        if request.method =="POST":
            user_ids= request.POST.get('sender_ids')

            is_accepts= request.POST.get('is_accepts')
            if  is_accepts =='1':
                sender_list.follow = is_accepts
                sender_list.request = False
                sender_list.save()
                return redirect('my_follower')
            else:
                is_accepts =='0'
                sender_list.delete()
                return redirect('request_list')
        return render(request,'frontend/follwer_request/click-on-user-details.html',{'requests_list':sender_list,'interest_data': interest_data,'age':age,'interest_list':interest_list})
    except:
        messages.error(request, 'Something Went Wrong')
        return redirect('home')

@login_required(login_url='/login/')
def my_follower(request):
    try:
        follower_list=FollowUnfollow.objects.filter(follow=True,receiver_id=request.user.id)
        if request.method == "POST":
            sender= request.POST.get('sender')
            unfollow= request.POST.get('is_unfollow')
            for i in follower_list:
                i.follow == unfollow
                i.delete()
                return redirect('my_follower')
        return render(request,'frontend/follwer_request/my-follower.html',{'follower_list':follower_list})
    except:
        messages.error(request, 'Something Went Wrong')
        return redirect('home')

@login_required(login_url='/login/')
def my_follower_detail(request,slug):
    try:
        followers_list=FollowUnfollow.objects.get(slug=slug)
        interests = EventCategory.objects.filter(is_active = True)
        birth_date = followers_list.sender.DOB
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        interest_data = []
        try:  
            interest_list = (followers_list.sender.interests).split(',')
            for list in interest_list:
                data_category = EventCategory.objects.get(id = list)
                interest_data.append(data_category)
        except:
            pass
        if request.method =="POST":
            followers= request.POST.get('followers')
            is_unfollow= request.POST.get('is_unfollow')
            if followers_list.follow == True:
                followers_list.follow = is_unfollow
                followers_list.delete()
                return redirect('my_follower')
            else:
                pass
        return render(request,'frontend/follwer_request/click-on-follower-details.html',{'requests_list':followers_list,'interest_data': interest_data,'age':age,'interest_list':interest_list})
    except:
        messages.error(request, 'Something Went Wrong')
        return redirect('home')
   
@login_required(login_url='/login/')
def add_my_favourite(request):
    try:
        if request.method == "POST":
            event_id=request.POST.get('event')
            user_id=request.POST.get('user')
            favourite=Favourite.objects.filter(event_id=event_id,user_id=user_id)
            if favourite:
                favourite.delete()
            else:
                favourites=Favourite.objects.create(event_id=event_id,user_id=user_id,favourite=True)
                return redirect('home')
        else:
            pass
    except:
        messages.error(request, 'Something Went Wrong')
        return redirect('home')

def my_favourite(request):
    try:
        event=EventCreate.objects.filter(is_active='1')
        favourite_list=Favourite.objects.filter(event_id__in=event,user_id=request.user.id)      
        return render(request,'frontend/favourite/my-favourite.html',{'favourite_list':favourite_list})
    except:
        messages.error(request, 'Something Went Wrong')
        return redirect('home')
   
@login_required(login_url='/login/')
def event_like(request):
    try:
        if request.method == "POST":
            event_id=request.POST.get('event')
            user_id=request.POST.get('user')
            slug=request.POST.get('slug')
            like=EventLike.objects.filter(event_id=event_id,user_id=user_id)
            if like:
                like.delete() 
            else:
                likes=EventLike.objects.create(event_id=event_id,user_id=user_id,like=True)
            return redirect('/event/individual/detail/' + str(slug))
    except:
        messages.error(request,'Something Went Wrong!!')
        return redirect('/event/individual/detail/' + slug)
        

@login_required(login_url='/login/')    
def event_rating(request):
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if request.method == "POST":
            rating=request.POST.get('rating')
            event_id =request.POST.get('event_id')
            user_id =request.POST.get('user_id')
            event_data = EventCreate.objects.get(id = event_id)
            ratings=UserTickets.objects.filter(date_and_time__lte=current_time,event_id=event_id).order_by('date_and_time')
            if ratings:
                update_data=EventRating.objects.filter(event_id=event_id,user_id=user_id)
                if update_data.exists():
                    update_data = update_data.first()
                    update_data.event_id=event_id
                    update_data.rating=rating
                    update_data.user_id=user_id
                    update_data.save()
                    message = f'Hi {event_data.organizer.first_name} {event_data.organizer.last_name}, your event {event_data.evnet_name} got ratings'
                    OrganizerNotification.objects.create(subject="Event Ratings", message = message, notification_type = 'RATINGS_FOR_EVENT', organizer_id = event_data.organizer_id)
                    return JsonResponse({'status':'success', 'rating': rating, 'message':'Rating  Update Suucessfully!!!'})
                else:  
                    data=EventRating.objects.create(user_id= user_id,event_id=event_id,rating=rating)
                    data.save()
                    message = f'Hi {event_data.organizer.first_name} {event_data.organizer.last_name}, your event {event_data.evnet_name} got ratings'
                    OrganizerNotification.objects.create(subject="Event Ratings", message = message, notification_type = 'RATINGS_FOR_EVENT', organizer_id = event_data.organizer_id)
                    return JsonResponse({'status':'success', 'rating': data.rating, 'message':'Rating Suucessfully!!!'})
            else:
                return JsonResponse({'status':'error', 'message':'You are not eligible for the rating !!!'})
        else:
            pass
    except:
        messages.error(request,'something went wrong')
        return redirect('/event-rating/')
            
@login_required(login_url='/login/')
def booked_event(request):
    try:
        booked=UserTickets.objects.filter(user_id=request.user.id).values_list('event_id', flat=True)
        events = EventCreate.objects.filter(id__in=booked)
        event_form_submited = []
        for event in events:
            ticket_data = UserTickets.objects.filter(event_id = event.id, user_id = request.user.id)
            for ticket in ticket_data:
                if ticket.survey_form_submited == True:
                    event_form_submited.append(event.id)
                    break
        return render(request,'frontend/booked_events/booked_event_listing.html',{'booked':events, 'event_form_submited': event_form_submited})
    except:
        messages.error(request, 'Something Went Wrong')
        return redirect('home')


@login_required(login_url='/login/')
def booked_event_detail(request,slug):
    try:
        event_detail=EventCreate.objects.get(slug=slug)
        try:
            g = geocoder.ip('me') 
            lat_long = g.latlng
            lat_a = lat_long[0]
            long_a = lat_long[1]
            lat_b = event_detail.latitude
            long_b = event_detail.longitude
            lat_a = radians(lat_a)
            lat_b = radians(lat_b)
            delta_long = radians(long_a - long_b)
            cos_x = (
                sin(lat_a) * sin(lat_b) +
                cos(lat_a) * cos(lat_b) * cos(delta_long)
                )
            distance_data = acos(cos_x) * 3958.8 * 1.60934
            distance = "%.2f" % distance_data
        except:
            distance = ""
        ticket=EventTicketCreate.objects.filter(ticket_event_id=event_detail.id)
        ticket_id = []
        for id in ticket:
            ticket_id.append(id.ticket_event_id)
        food_cost=FoodInEvent.objects.filter(event_id=event_detail).exclude(food_id=None)
        like_count=EventLike.objects.filter(event_id=event_detail).count()
        attendees_data = UserTickets.objects.filter(event_id = event_detail.id).values('user_id').distinct() 
        attendees_count = attendees_data.count()
        # event_rating=EventRating.objects.filter(event_id=event_detail)
        refund=UserTickets.objects.filter(is_used=0)

        # rating = None
        # if event_rating.exists():
        #     rating = event_rating.first().rating
        avg=EventRating.objects.filter(event_id=event_detail).aggregate(avg_rating=Avg('rating'))
        res = dict()
        for key in avg:
            res[key] = round(avg[key],0) if avg[key] else 0
         
            event_detail.average_rating=res[key]
            event_detail.save()
        try:
            seat_price = TicketSeats.objects.filter(event_id = event_detail.id).order_by('-seat_price').values('seat_price').last()
            ticket_start_from = seat_price['seat_price']
        except:
            ticket_start_from = None   
    
        data={'ticket_start_from':ticket_start_from,'ticket_id': ticket_id, 'distance': distance, 'attendees_count': attendees_count,'event_detail':event_detail,
            'ticket':ticket,'food_cost':food_cost,'like_count':like_count,'rating': res[key],'refund':refund}
        return render(request,'frontend/booked_events/event-details.html',data)
    except:
        messages.error(request,'something went wrong!!')
        return redirect('my_account')

@login_required(login_url='/login/')
def past_events(request):
    try:
        user_id = request.user.id
        data = UserTickets.objects.filter(user_id = user_id).values('event_id').distinct() 
        events = []
        for id in data:
            events.append(id['event_id'])
        past_event_data = []
        for event_id in events:
            event_data = EventCreate.objects.get(id = event_id)
            past_event_data.append(event_data)
        today_date = timezone.now()
        return render(request, "frontend/past_event/past_event.html", {'past_event_data': past_event_data, 'today_date': today_date})
    except:
        messages.error(request, "Something Went Wrong")
        return redirect('my_account')

@login_required(login_url='/login/')
def survey_answers(request, event_slug):
    try:
        user_id = request.user.id
        event_data = EventCreate.objects.get(slug = event_slug)
        survey_questions = SurveyQuestions.objects.all()
        if request.method == 'POST':
            y = 1
            for survey_question in survey_questions:
                input_name = f'user_answer_{y}'
                answer = request.POST.get(input_name)
                SurveyAnswers.objects.create(survey_questions_id = survey_question.id, user_id = user_id, event_id = event_data.id, answer = answer)
                y += 1
            if UserTickets.objects.filter(user_id = user_id, event_id = event_data.id).exists():
                ticket_data = UserTickets.objects.filter(user_id = user_id, event_id = event_data.id)
                for ticket in ticket_data:
                    ticket.survey_form_submited = True
                    ticket.save() 
            return redirect('booked_event')
        # event_rating=EventRating.objects.filter(event_id=event_data.id)
        # rating = None
        # if event_rating.exists():
        #     rating = event_rating.first().rating
        #     return redirect('booked_event')
                        
        return render(request, 'frontend/event_survey_form.html', {'event_data':event_data,'survey_questions': survey_questions})  
    except:
        messages.error(request, "Something Went Wrong")
        return redirect('booked_event')



def showFirebaseJS(request):
    data='importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-app.js");' \
         'importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-messaging.js"); ' \
         'var firebaseConfig = {' \
         '        apiKey: "AIzaSyDwHKP1YJVtmyBg_ReWMXGPYNGPlqvX_eA",' \
         '        authDomain: "golden-tick-cc77f.firebaseapp.com",' \
         '        databaseURL: "",' \
         '        projectId: "golden-tick-cc77f",' \
         '        storageBucket: "golden-tick-cc77f.appspot.com",' \
         '        messagingSenderId: "112753949003",' \
         '        appId: "1:112753949003:web:57c1e229bf41e55dc2d0ce",' \
         '        measurementId: ""' \
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

    
@login_required(login_url='/login/')
def refund_request(request):
    try:
        user_ticket=UserTickets.objects.filter(is_used=0,user_id=request.user.id,refund_initiated=0)
        if request.method =="POST":
            event=request.POST.get('event')
        for i in user_ticket:
                if i.event_id==int(event):
                    i.refund_request=1
                    i.save()
                    messages.success(request,'Your request has been send admin!!')
        return redirect('booked_event')
    except:
        messages.error(request,'Something Went Wrong!!')
        return redirect('booked_event')

       
      
