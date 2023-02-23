
from django.contrib.messages.api import success
from freegoadmin.form import signupForm 
from django import http
from django.shortcuts import redirect, render
from freegoadmin.models import AboutPage, GlobalModel,Age,Country, HappyUser, OurFeatureModel, User,ContentManagement,TemplateManagemnet, UserMessage
from django.http import HttpRequest, HttpResponse, request, HttpResponseRedirect, JsonResponse, response
from django.contrib.auth import logout, login
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
import datetime
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model
from django.core import serializers
import json
from django.core.mail import send_mail
User = get_user_model()
from django.conf import settings 
from_mail=settings.EMAIL_HOST_USER


# Create your views here.
@login_required(login_url='/freego/admin/login/')
def home_loginView(request):
    
    if request.session.set_test_cookie():
            user=request.COOKIES['user']
            password=request.COOKIES['password']
            login_id=[user,password]
            return JsonResponse({'login':login_id})
    return render(request,'freegoadmin/index.html')

@login_required(login_url='/freego/admin/login/')
def homeView(request):
     return render(request,'freegoadmin/index.html')
       


def loginView(request):

    if request.method == 'POST':
        email_id=request.POST['email_id']
        try:
            obj=User.objects.get(email=email_id)
        except:
            messages.info(request, 'User Email or User name does not match !!! ')
            return render(request, 'freegoadmin/login.html')
        if obj:
            passwd=request.POST.get('pass')

            try:
                user = authenticate(request, email=email_id, password=passwd)
            except:
                messages.info(request, 'User Credentials does not match !!! ')
                return render(request, 'freegoadmin/login.html')

            if user:
                if request.POST.get('value'):
                    response=HttpResponseRedirect("/freego/")
                    response.set_cookie('user',email_id)
                    response.set_cookie('password',passwd)
                    return response
                login(request, user)
                
                return redirect('/freego/')
            else:
                messages.info(request, 'password is wrong so please fill correct password!!! ')
                return render(request, 'freegoadmin/login.html')
        else:
            messages.info(request, 'User Credentials does not match !!! ')
            return render(request, 'freegoadmin/login.html')
        
    else:
        
        return render(request, 'freegoadmin/login.html')

@login_required(login_url='/freego/admin/login/')
def logoutView(request):
    response = HttpResponseRedirect('/login/')
    response.delete_cookie('user')
    response.delete_cookie('password')
    logout(request)
    
    return HttpResponseRedirect('/freego/')    


@login_required(login_url='/freego/admin/login/')
def profileupdateView(request):
    current_user = request.user
    if request.method == 'POST':
        image = request.FILES.get('image')
        email_id = request.POST.get('email')
        f_name = request.POST.get('fname')
        l_name = request.POST.get('lname')
        contact_no = request.POST.get('contact')
        print(image, email_id, f_name, l_name, contact_no)
        if email_id and f_name and l_name and contact_no:
            if current_user is not None:
                obj = User.objects.get(email=current_user)
                if image is not None:
                    
                    obj.user_image=image
                    obj.email = email_id
                    obj.fname = f_name
                    obj.lname = l_name
                    obj.contact = contact_no
                    obj.save()
                else:
                    obj.email = email_id
                    obj.fname = f_name
                    obj.lname = l_name
                    obj.contact = contact_no
                    obj.save()

                ob = User.objects.filter(email=current_user)
                messages.success(request, 'Succefull upate user profile!!')
                return render(request, 'freegoadmin/profile.html', {'fm': ob})
        else:
            ob = User.objects.filter(email=current_user)
            messages.info(
                request, 'something is missing so Please fill complete form!!!')
            return render(request, 'freegoadmin/profile.html', {'fm': ob})
    else:
        ob = User.objects.filter(email=current_user)
        return render(request, 'freegoadmin/profile.html', {'fm': ob})


# @login_required(login_url='/freego/admin/login/')
def signupView(request):
    if request.method == 'POST':
        fname1 = request.POST.get('fname')
        lname1 = request.POST.get('lname')
        email_id = request.POST.get('email')
        user_age = request.POST.get('age')
        contact_no = request.POST.get('contact')
        pass1 = request.POST.get('password')
        pass2 = request.POST.get('confirm_pass')
        if pass1 == pass2:
            if fname1 and lname1 and email_id and user_age and contact_no and pass1:
                obj = User(fname=fname1, lname=lname1,
                           email=email_id, age=user_age)
                obj.set_password(pass1)
                obj.save()
                messages.info(request, 'succeful registor ')
                return render(request, 'webauth/signup.html')
            else:
                messages.info(request, 'something is missing ')
                return render(request, 'webauth/signup.html')
        else:
            messages.info(request, 'password does not match')
            return render(request, 'webauth/signup.html')
    else:
        form = signupForm()
        return render(request, 'webauth/signup.html', {'form': form})





@login_required(login_url='/freego/admin/login/')
def userView(request):
    try:
        obj = User.objects.all().order_by('-created_at')
    except User.DoesNotExist:
        obj=None
    ob=obj.values('fname','lname').distinct()
    return render(request, 'freegoadmin/usertable.html', {'form': obj,'fm':ob})


@login_required(login_url='/freego/admin/login/')
def userfilterView(request):

    if request.method=='POST':
        name=request.POST.get("name")
        
        if name:
            
            firstname ,lastname=name.split(' ',1)   
            try:
                obj = User.objects.filter(fname=firstname,lname=lastname)
            except User.DoesNotExist:
                obj=None
            try:
                ob = User.objects.all()
            except User.DoesNotExist:
                ob=None
            ob=ob.values('fname','lname').distinct()
            return render(request, 'freegoadmin/usertable.html', {'form': obj,'fm':ob ,'name':name})

            
        else: 
            try:
                obj = User.objects.all()
            except User.DoesNotExist:
                obj=None
            ob=obj.values('fname','lname').distinct()
            return render(request, 'freegoadmin/usertable.html', {'form': obj,'fm':ob})

        
@login_required(login_url='/freego/admin/login/')
def deleteView(request, a):
    obj = User.objects.get(pk=a)
    obj.delete()
    ob = User.objects.all()
    messages.success(request,'Successfully delete user !!!')
    return render(request, 'freegoadmin/usertable.html', {'form': ob})


@login_required(login_url='/freego/admin/login/')
def deactiveView(request, d):
    obj = User.objects.get(pk=d)
    obj.is_active = False
    obj.save()
    ob = User.objects.all()
    messages.success(request,'Successfully deactive user account ')
    return render(request, 'freegoadmin/usertable.html', {'form': ob})


@login_required(login_url='/freego/admin/login/')
def activeView(request,a):
    obj = User.objects.get(pk=a)
    print(obj)
    obj.is_active = True
    obj.save()
    ob = User.objects.all()
    messages.success(request,'successfully active user account')
    return render(request, 'freegoadmin/usertable.html', {'form': ob})


@login_required(login_url='/freego/admin/login/')
def editView(request, a):
    id = a
    obj1=Age.objects.all()
    obj2=Country.objects.all()
    if request.method == 'POST':
        obj = User.objects.get(pk=id)
        image = request.FILES.get('image')

        email_id = request.POST.get('email')
        f_name = request.POST.get('fname')
        l_name = request.POST.get('lname')
        age1 = request.POST.get('age')
        desh = request.POST.get('country')
        if f_name and l_name and age1 and desh:  
            obj.fname = f_name
            obj.lname = l_name
           
            obj.age_id = age1
            obj.country_id = desh
            if image != None:
                obj.user_image = image
                obj.save()
                obj = User.objects.get(id=id)
                messages.success(request, 'Succefully Update User data')
                return render(request, 'freegoadmin/edituser.html', {'fm': obj, 'id': id,'fm1':obj1,'fm2':obj2})
            else:
                obj.save()
                obj = User.objects.get(id=id)
                messages.success(request, 'Succefully Update User data')
                return render(request, 'freegoadmin/edituser.html', {'fm': obj, 'id': id,'fm1':obj1,'fm2':obj2})
        else:
            obj = User.objects.get(id=id)


            messages.error(
                request, 'Something is missing so please fill complete form!!! ')
            return render(request, 'freegoadmin/edituser.html', {'fm': obj, 'id': id,'fm1':obj1,'fm2':obj2})

    else:
        obj = User.objects.get(id=id)
        
        return render(request, 'freegoadmin/edituser.html', {'fm': obj, 'id': id,'fm1':obj1,'fm2':obj2})


@login_required(login_url='/freego/admin/login/')
def changepassView(request):
    if request.method == 'POST':
        old_password = request.POST.get("old_pass")
        new_password = request.POST.get("new_pass")
        confirmed_new_password = request.POST.get("new_pass2")

        if old_password and new_password and confirmed_new_password:
            if request.user.is_authenticated:

                user = User.objects.get(email=request.user)
                if not user.check_password(old_password):

                    messages.warning(
                        request, "your old password is not correct!")
                    return render(request, 'freegoadmin/changepassword.html')
                else:
                    if new_password != confirmed_new_password:
                        messages.warning(
                            request, "your new password not match the confirm password !")
                        return render(request, 'freegoadmin/changepassword.html')

                    else:
                        user.set_password(new_password)

                        user.save()

                        messages.success(
                            request, "your password has been changed successfuly.!")
                        return render(request, 'freegoadmin/changepassword.html')

        else:
            messages.warning(request, " sorry , all fields are required !")
            return render(request, 'freegoadmin/changepassword.html')

    return render(request, 'freegoadmin/changepassword.html')


@login_required(login_url='/freego/admin/login/')
def profileView(request):
    current_user=request.user
    obj=User.objects.values().get(email=current_user)
    image=obj['user_image']
    fname=obj['fname']
    lname=obj['lname']
    email=obj['email']

    l=[image,fname,lname,email]   
    
    return JsonResponse({'joson':l})



#contentManagemetn View
@login_required(login_url='/freego/admin/login/')
def contentManagement(request):
    obj=ContentManagement.objects.all()
    return render(request,'pages/contentMangement/content_management.html',{'form':obj})

@login_required(login_url='/freego/admin/login/')
def contentView(request ,a):
    pk=a
    obj=ContentManagement.objects.get(id=pk)
    return render(request,'pages/contentMangement/show.html',{'fm':obj})

@login_required(login_url='/freego/admin/login/')
def contentEditView(request,a):
    pk=a
    obj=ContentManagement.objects.get(id=pk)
    if request.method=='POST':
        title1=request.POST.get('title')
        content=request.POST.get('content')
        print(content)
        if title1 and content:
            
            obj.title=title1
            obj.description=content
            print(title1)
            obj.save()
            messages.success(request,'succfully change content !!!!')
            return render(request,'pages/contentMangement/edit.html',{'fm':obj})
        else:
            messages.warning(request,'something is missing !!!')
            return render(request,'pages/contentMangement/edit.html')

    else:
       
        return render(request,'pages/contentMangement/edit.html',{'fm':obj})


@login_required(login_url='/freego/admin/login/')
def templateManagement(request):
    obj=TemplateManagemnet.objects.all()
    return render(request,'pages/templateMangement/template_management.html',{'form':obj})

@login_required(login_url='/freego/admin/login/')
def templateView(request,a):
    pk=a
    obj=TemplateManagemnet.objects.get(id=a)
    print(obj.title)
    return render(request,'pages/templateMangement/show.html',{'fm':obj})

@login_required(login_url='/freego/admin/login/')
def templateEditView(request,a):
    pk=a
    obj=TemplateManagemnet.objects.get(id=a)
    if request.method=='POST':
        title1=request.POST.get('title')
        content1=request.POST.get('content')
        sub=request.POST.get('subject')

        if title1 and content1 and sub:
            obj.subject=sub
            obj.title=title1
            obj.content=content1
            
            obj.save()
            print(content1)
            messages.success(request,'succfully change content !!!!')
            return render(request,'pages/templateMangement/edit.html',{'fm':obj})
        else:
            messages.warning(request,'something is missing !!!')
            return render(request,'pages/templateMangement/edit.html',{'fm':obj})

    else:
       
        return render(request,'pages/templateMangement/edit.html',{'fm':obj})

@login_required(login_url='/freego/admin/login/')
def globalView(request):
    try:
        ob=GlobalModel.objects.get(pk=1)
    except GlobalModel.DoesNotExist:
        ob=None
    try:
        obj=OurFeatureModel.objects.get(pk=1)
    except OurFeatureModel.DoesNotExist:
        obj=None
    

    return render(request,'freegoadmin/global.html' ,{'fm':ob,'fm1':obj,'val':1})



import datetime
# home page view
@login_required(login_url='/freego/admin/login/')
def testView(request, n):
    obj=GlobalModel.objects.get(slug='global')
    print(obj)
    ob=OurFeatureModel.objects.get(pk=1)
    a=n
    if request.method=='POST':
        about_descriptions=request.POST.get('about_description')
        about_imgs=request.FILES.get('about_image')
        about_imgs2=request.FILES.get('about_image2')
        
        about_links=request.POST.get('about_link')
        about_title1=request.POST.get('about_title')

       
       
        sec1_descriptions=request.POST.get('sec1_description')
        sec1_imgs=request.FILES.get('sec1_image')
        sec1_links=request.POST.get('sec1_link')
        sec1_title1=request.POST.get('sec1_title')

        sec2_descriptions=request.POST.get('sec2_description')
        sec2_imgs=request.FILES.get('sec2_image')
        sec2_links=request.POST.get('sec2_link')
        sec2_titles=request.POST.get('sec2_title')
        
       
        
        #our feature
        first_title1=request.POST.get('f_title')
        first_descriptions=request.POST.get('f_desc')
        first_imgs=request.FILES.get('f_image')
        second_title1=request.POST.get('s_title')
        second_descriptions=request.POST.get('s_desc')
        second_imgs=request.FILES.get('s_image')
        third_title1=request.POST.get('t_title')
        third_descriptions=request.POST.get('t_desc')
        third_imgs=request.FILES.get('t_image')
        disc=request.POST.get('desc')

        if a==7:
            if first_descriptions and first_title1 and second_descriptions and second_title1 and third_title1 and third_descriptions:
                ob.description=disc
                ob.first_desc=first_descriptions
                ob.first_title=first_title1
                ob.second_title=second_title1
                ob.second_desc=second_descriptions
                ob.third_title=third_title1
                ob.third_desc=third_descriptions
                ob.save()
                if first_imgs:
                    ob.first_img=first_imgs
                    ob.save()
                if second_imgs:
                    ob.second_img=second_imgs
                    ob.save()
                if third_imgs:
                    ob.third_img=third_imgs
                    ob.save()

                messages.success(request,'data is update is succefully')
                return render(request,'freegoadmin/global.html',{'fm':obj,'fm1':ob,'val':7})
            else:
                messages.info(request,'something is missing !!!' )
                return render(request,'freegoadmin/global.html',{'fm':obj,'fm1':ob,'val':7})

    
        elif a==6:
            mails=request.POST.get('mail')
            contacts=request.POST.get('contact')
            address1=request.POST.get('address')
            fb_ids=request.POST.get('fb_id')
            twit_ids=request.POST.get('twit_id')
            linkdins=request.POST.get('linkdin')
            paypals=request.POST.get('paypal')
            utube=request.POST.get('youtube')
            insta_id=request.POST.get('insta')

            descriptions=request.POST.get('desc')
     

            if  mails and fb_ids and linkdins and contacts and address1 and paypals and descriptions and  twit_ids and utube and insta_id: 
                obj.mail=mails
                obj.contact=contacts
                obj.address=address1
                obj.linkdin=linkdins
                obj.paypal=paypals
                obj.twit_id=twit_ids
                obj.fb_id=fb_ids
                obj.youtube=utube
                obj.insta=insta_id
                obj.description=descriptions
                obj.save()
                messages.success(request,'data is update is succefully')
                return render(request,'freegoadmin/global.html',{'fm':obj,'fm1':ob,'val':6})
            else:
                messages.info(request,'something is missing !!!')
                return render(request,'freegoadmin/global.html',{'fm':obj,'fm1':ob,'val':6})


        elif a==1:
            ban_descriptions=request.POST.get('ban_description')
            ban_imgs=request.FILES.get('ban_image')
            ban_links=request.POST.get('ban_link')
            ban_title1=request.POST.get('ban_title')
            if ban_descriptions and ban_links and ban_title1:
                obj.ban_description=ban_descriptions
                obj.ban_link=ban_links
                obj.ban_title=ban_title1
                obj.save()
                if ban_imgs:
                    obj.ban_img=ban_imgs
                    obj.save()
            
                messages.success(request,'data is update is succefully')
                return render(request,'freegoadmin/global.html',{'fm':obj,'fm1':ob,'val':1})
            else:
                messages.info(request,'something is missing !!!')
                return render(request,'freegoadmin/global.html',{'fm':obj,'fm1':ob,'val':1})


        elif a==2:
            if about_descriptions and about_title1 and about_links:    
                obj.about_description=about_descriptions
                obj.about_link=about_links
                obj.about_title=about_title1
                obj.save()
                if about_imgs:
                    obj.about_img=about_imgs
                    obj.save()
                if about_imgs2:
                    obj.about_img2=about_imgs2
                    obj.save()
                messages.success(request,'data is update is succefully')
                return render(request,'freegoadmin/global.html',{'fm':obj,'fm1':ob,'val':2})
            else:
                messages.info(request,'something is missing !!!')
                return render(request,'freegoadmin/global.html',{'fm':obj,'fm1':ob,'val':2})

            
           
            
        elif a==3:
    
            if sec1_descriptions and sec1_links and sec1_title1 and sec1_links:  
                obj.sec1_description=sec1_descriptions
                obj.sec1_link=sec1_links
                obj.sec1_title=sec1_title1
                obj.save()
                if sec1_imgs:
                    obj.sec1_img=sec1_imgs
                    obj.save()
                messages.success(request,'data is update is succefully')
                return render(request,'freegoadmin/global.html',{'fm':obj,'fm1':ob,'val':3})
            else:
                messages.info(request,'something is missing !!!')
                return render(request,'freegoadmin/global.html',{'fm':obj,'fm1':ob,'val':3})


        elif a==4:
            if sec2_descriptions and sec2_links and sec2_titles:
                obj.sec2_description=sec2_descriptions
                obj.sec2_link=sec2_links
                obj.sec2_title=sec2_titles
                obj.save()
                if sec2_imgs:
                    obj.sec2_img=sec2_imgs
                    obj.save()
                messages.success(request,'data is update is succefully')
                return render(request,'freegoadmin/global.html',{'fm':obj,'fm1':ob ,'val':4})
            else:
                messages.info(request,'something is missing !!!')
                return render(request,'freegoadmin/global.html',{'fm':obj,'fm1':ob,'val':4})


        elif a==5:
            get_title1=request.POST.get('get_title')
            get_descriptions=request.POST.get('get_description')
            get_imgs=request.FILES.get('get_image')
            get_links=request.POST.get('get_link')
            get_link2s=request.POST.get('get_link2')

            print(request.POST)

            print(request.POST) 
            if get_descriptions and get_link2s and get_title1 and get_links:  
                obj.get_title=get_title1
                obj.get_discription=get_descriptions
                obj.get_link=get_links
                obj.get_link2=get_link2s
                obj.save()
                if get_imgs:
                    obj.get_img=get_imgs
                    obj.save()
                messages.success(request,'data is update is succefully')
                return render(request,'freegoadmin/global.html',{'fm':obj,'fm1':ob,'val':5})
            else:
                messages.info(request,'something is missing !!!')
                return render(request,'freegoadmin/global.html',{'fm':obj,'fm1':ob,'val':5})

        
    else:
        return render(request,'freegoadmin/global.html',{'fm':obj,'fm1':ob,'val':1})


#aboutpage view
@login_required(login_url='/freego/admin/login/')
def aboutView(request):
    try:
        obj=AboutPage.objects.get(pk=1)
    except AboutPage.DoesNotExist:
        obj=None
    return render(request,'setting/about_page.html',{'fm':obj,'val':1})

@login_required(login_url='/freego/admin/login/')
def aboutPageView(request,a):
    obj=AboutPage.objects.get(pk=1)
    

    if request.method=='POST':
        if a==1:
            ab_title=request.POST.get('about_title')
            ab_subtitle=request.POST.get('about_subtitle')
            ab_desc=request.POST.get('about_desc')
            ab_img1=request.FILES.get('about_image1')
            ab_img2=request.FILES.get('about_image2')
    
            
            
            if ab_title and ab_subtitle and ab_desc:  
                        obj.title=ab_title
                        obj.subtitle=ab_subtitle
                        obj.desc=ab_desc
                        obj.save()
                        if ab_img1:
                            obj.img1=ab_img1
                            obj.save()
                        if ab_img2:
                            obj.img2=ab_img2
                            obj.save()
                        messages.success(request,'data is update is succefully')
                        return render(request,'setting/about_page.html',{'fm':obj,'val':1})
            else:
                messages.info(request,'something is missing !!!')
                return render(request,'setting/about_page.html',{'fm':obj, 'val':1})
        elif a==2:
           
           print(request.POST)
           sec1_title=request.POST.get('sec1_title') 
           sec1_desc=request.POST.get('sec1_desc') 
           sec1_title2=request.POST.get('sec1_title2') 
           sec1_desc2=request.POST.get('sec1_desc2') 
           sec1_title3=request.POST.get('sec1_title3') 
           sec1_desc3=request.POST.get('sec1_desc3') 
           if sec1_title and sec1_title and sec1_desc and sec1_desc2 and sec1_title3 and sec1_desc3:
               obj.sec1_title=sec1_title
               obj.sec1_desc=sec1_desc
               obj.sec1_title2=sec1_title2
               obj.sec1_desc2=sec1_desc2
               obj.sec1_title3=sec1_title3
               obj.sec1_desc3=sec1_desc3
               obj.save()
               messages.success(request,'data is update is succefully')
               return render(request,'setting/about_page.html',{'fm':obj,'val':2})
           else:
                messages.info(request,'something is missing !!!')
                return render(request,'setting/about_page.html',{'fm':obj,'val':2})

        elif a==3:
            cfb_title=request.POST.get('cf_title')
            cfb_subtitle=request.POST.get('cf_subtitle')
            cfb_desc=request.POST.get('cf_desc')
            cfb_img=request.FILES.get('cf_image')
            if cfb_desc and cfb_subtitle and cfb_title:
                obj.cf_title=cfb_title
                obj.cf_subtitle=cfb_subtitle
                obj.cf_desc=cfb_desc
                obj.save()
                if cfb_img:
                    obj.cf_img1=cfb_img
                    obj.save()
                messages.success(request,'data is update is succefully')
                return render(request,'setting/about_page.html',{'fm':obj,'val':3})
            else:
                messages.info(request,'something is missing !!!')
                return render(request,'setting/about_page.html',{'fm':obj,'val':3})



    else:
        return render(request,'setting/about_page.html',{'fm':obj})

@login_required(login_url='/freego/admin/login/')
def sliderView(request):
    return render(request,'setting/slider.html')

@login_required(login_url='/freego/admin/login/')
def userMessageView(request):
    ob=UserMessage.objects.all()
    return render(request,'setting/user_msg.html',{'fm':ob})

@login_required(login_url='/freego/admin/login/')
def messageView(request,a):
    id=a
    ob=UserMessage.objects.get(pk=id)
    return render(request,'setting/msg_view.html',{'fm':ob})

@login_required(login_url='/freego/admin/login/')
def msg_deleteView(request,a):
    id=a
    obj=UserMessage.objects.get(pk=a)
    obj.delete()
    ob=UserMessage.objects.all()
    messages.success(request,'Successfully delete user message')

    return render(request,'setting/user_msg.html',{'fm':ob})


@login_required(login_url='/freego/admin/login/')
def msg_replyView(request,a):
    id=a
    ob=UserMessage.objects.get(pk=id)
    if request.method=="POST":
        sub=request.POST.get('subject')
        msg=request.POST.get('message')
        send_to=ob.email_id
        try:
            send_mail(sub,msg,from_mail,[send_to],fail_silently=False,)
            ob.status=False
            ob.save()
        except:
            messages.success(request,'email cannot send. Please check email id !!!! ')
            return render(request,'setting/user_msg_reply.html',{'fm':ob})
        messages.success(request,'email send succesfully to user !!!! ')
        return render(request,'setting/user_msg_reply.html',{'fm':ob})
    else:
        return render(request,'setting/user_msg_reply.html',{'fm':ob})

@login_required(login_url='/freego/admin/login/')       
def sliderView(request):
    obj=HappyUser.objects.all()
    return render(request,'setting/slider.html',{'fm':obj})

@login_required(login_url='/freego/admin/login/')
def editHappyView(request,a):
      id=a
      print(request.POST)
      obj=HappyUser.objects.get(pk=id)
      if request.method=='POST':
        name1=request.POST.get('name')
        position=request.POST.get('position')
        desc1=request.POST.get('desc')
        img1=request.FILES.get('image')
        print(name1,desc1 ,position)
        if name1 and position and desc1:
            obj.name=name1
            obj.postison=position
            obj.desc=desc1.strip()
            obj.save()
            if img1:
                obj.img=img1
                obj.save()
            messages.info(request,'succefully edit user data!!!')
            return render(request,'setting/happy_user.html',{'fm':obj})
        else:
            messages.info(request,'something is missing so plz check it!!!')
            return render(request,'setting/happy_user.html',{'fm':obj})
      else:
        return render(request,'setting/happy_user.html',{'fm':obj})

@login_required(login_url='/freego/admin/login/')
def addHappyView(request):
    if request.method=='POST':
        name1=request.POST.get('name')
        position=request.POST.get('position')
        desc1=request.POST.get('desc')
        img1=request.FILES.get('image')
        if name1 and position and desc1  and img1:
            obj=HappyUser(name=name1,postison=position,desc=desc1,img=img1)
            obj.save()
            messages.info(request,'succefully add happy user data!!!')
            return render(request,'setting/add_happy_user.html')
        else:
            messages.info(request,'something is missing so plz check it!!!')
            return render(request,'setting/add_happy_user.html')
    else:
        return render(request,'setting/add_happy_user.html')


@login_required(login_url='/freego/admin/login/')
def deleteHappyView(request,a):
    obj=HappyUser.objects.get(pk=a)
    obj.delete()
    obj=HappyUser.objects.all()
    messages.success(request,'succefully delete User details')
    return render(request,'setting/slider.html',{'fm':obj})

@login_required(login_url='/freego/admin/login/')
def firstView(request):

    return HttpResponse('send message succefully')


