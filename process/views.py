import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count
from django.forms import formset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from process.models import *
import datetime
from django.db.models import Q

# Create your views here.

def my_login(request): # function login base django
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.POST.get('next_url')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('../index/')
        else:
            context = {
                'username': username,
                'error': 'Wrong username or password'
            }
    return render(request, template_name='login.html', context=context)

@login_required
def my_create_member(request):
    money = 100
    txt = ''

    if request.method == 'POST':
        name = request.POST.get('first_name')
        last = request.POST.get('last_name')
        member = Member(
            first_name = request.POST.get('first_name'),
            last_name = request.POST.get('last_name'),
            money = money,
        )
        member.save()
        topup_log(member, request.user, '+', money)
        member = Member.objects.filter(first_name=name)[0]
        txt = '<p class="text-success">สมัครสมาชิกให้คุณ '+name+' '+last+' เรียบร้อย ID ของคุณคือ '+'%s'%member.id+' เรียบร้อย</p>'
    context = {
        'txt':txt,
        'username':"'"+request.user.username+"'",
        }
    return render(request, template_name='create_member.html', context=context)

@login_required
def create_zone(request):
    if request.method == 'POST':
        zone = Zone(
            title = request.POST.get('name'),
            description = request.POST.get('description'),
            price = request.POST.get('Price'),
        )
        zone.save()
        return redirect('../index/')
    return render(request, template_name='create_zone.html')

def my_logout(request):
    logout(request)
    return redirect('login')

@login_required
def change_password(request):
    if request.method == 'POST':
        user = request.user
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        # check that the passwords match
        if password1 == password2:
            # reset password
            user.set_password(password1)
            user.save()
            return redirect('logout')
    context = {'username':"'"+request.user.username+"'"}
    return render(request, template_name='change_password.html', context=context)

@login_required
def index(request):
    seatbooking_list = {}
    member = {}
    member_id = ''
    money = 0
    mem_id = ''
    txt = ''

    if request.method == 'POST':
        if request.POST.get("check_in") == "check_in": # ถ้ากดปุ่ม check_in
            mem_id = request.POST.get('check_in_id', '')
            name_zone = request.POST.get("select") # ดึงตัวเลือกมา

            member = Member.objects.filter(id=mem_id)[0]
            zone = Zone.objects.filter(title=name_zone)[0]
            user = request.user
            zone_price = zone.price

            if member.money >= zone_price: # เช็คว่ามีเงินพอไหม
                seatbooking = SeatBooking (
                    member = member,
                    zone = zone,
                    time_in = datetime.datetime.now(),
                    total_price = zone_price,
                    create_date = datetime.datetime.now(),
                    create_by = user
                )
                seatbooking.save()

                seatbooking_list = SeatBooking.objects.filter(member_id=mem_id).order_by('-time_in')
                txt = '<p class="text-success">ดำเนิน Check in : '+name_zone+' สำหรับ ID : '+mem_id+' เรียบร้อย</p>'

            else:
                seatbooking_list = SeatBooking.objects.filter(member_id=mem_id).order_by('-time_in')
                member = Member.objects.filter(id=mem_id)[0]
                txt = '<p class="text-danger">ID : '+mem_id+' มีเงินไม่พอสำหรับการ Check in : '+name_zone+'</p>'

        elif request.POST.get("check_out") == "check_out":
            mem_id = request.POST.get('check_out_id', '')
            seatbooking_list = SeatBooking.objects.filter(member_id=mem_id).order_by('-time_in')
            user = request.user
            member = Member.objects.filter(id=mem_id)[0]

            for i in range(len(seatbooking_list)):
                if not (seatbooking_list[i].time_out):
                    zone_id = seatbooking_list[i].zone_id
                    seatbooking_list[i].time_out = datetime.datetime.now() # + datetime.timedelta(hours=1) # <<<<<<<<<<<< แก้ไขเวลาตรงนี้
                    seatbooking_list[i].save()
                    start = datetime.datetime.fromisoformat(seatbooking_list[i].time_in.strftime("%Y-%m-%d %H:%M:%S"))
                    ends = datetime.datetime.fromisoformat(seatbooking_list[i].time_out.strftime("%Y-%m-%d %H:%M:%S"))
                    diff = -(start - ends) # ที่ใส่ - ด้านหน้าเพราะทำเป็นค่าส่วนกลับของเวลาจะได้มาเป็น ใช้เวลาไปกี่นาที
                    hours_use = diff.seconds // 3600 + 1
                    total_price = hours_use * Zone.objects.filter(id=zone_id)[0].price # ราคาชั่วโมงต่อโซน
                    time_use = str(diff)
                    txt += '<p class="text-danger">ดำเนิน Check out : '+seatbooking_list[i].zone.title+' สำหรับ ID : '+mem_id+' เรียบร้อย ใช้เวลาไป '+time_use+' คิดเป็นค่าบริการ '+'%s'%total_price +' บาท</p>'
                    min(member, total_price, user) # ส่งไปลบ

        else:
            search = request.POST.get('search', '')
            member = Member.objects.filter(Q(id__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search)).order_by('id')[0]

            if search.isnumeric():
                member = Member.objects.filter(id=search)[0]

            seatbooking_list = SeatBooking.objects.filter(member_id=member.id).order_by('-time_in')

        for i in range(len(seatbooking_list)):
            seatbooking_list[i].time_in = seatbooking_list[i].time_in.strftime("%d-%m-%Y %H:%M:%S")
            if (seatbooking_list[i].time_out):
                seatbooking_list[i].time_out = seatbooking_list[i].time_out.strftime("%d-%m-%Y %H:%M:%S")
        money = member.money
        mem_id = '%s'%member.id + ' ('+member.first_name+' '+member.last_name+')'

    zone = ''
    zone_price = '{'
    zone_des = '{'
    zone_list = Zone.objects.all()
    for i in range(len(zone_list)):
        zone += '<option value="'+zone_list[i].title+'">'+zone_list[i].title+'</option>'
        zone_price += '"'+zone_list[i].title+'":"[ ฿'+'%s'%zone_list[i].price+'/คน/ชั่วโมง ]",'
        zone_des += '"'+zone_list[i].title+'":"'+zone_list[i].description+'",'
    zone_price += '}'
    zone_des += '}'

    if member:
        member_id = member.id

    context = {
        'seatbooking_list':seatbooking_list,
        'member':member,
        'money':money,
        'check_in_id':member_id,
        'mem_id':mem_id,
        'txt':txt,
        'zone':zone,
        'zone_price':zone_price,
        'zone_des':zone_des,
        'username':"'"+request.user.username+"'",
    }
    return render(request, template_name='index.html', context=context)

@login_required
def money(request):
    topup_log = {}
    member = {}
    money = 0
    mem = ''
    member_id = ''
    txt = ''
    txt2 = ''

    if request.method == 'POST':
        if not (request.POST.get('search', '')):
            mem_id = request.POST.get('mem_id', '')
            member = Member.objects.filter(id=mem_id)
            topup_log = TopupLog.objects.filter(member_id=mem_id).order_by('-topup_date')

            if request.POST.get("20") == "20":
                money = 20

            elif request.POST.get("50") == "50":
                money = 50

            elif request.POST.get("100") == "100":
                money = 100

            elif request.POST.get("500") == "500":
                money = 500

            elif request.POST.get("1000") == "1000":
                money = 1000

            money_old = money

            if member[0].money < -40:
                money -= 20
                txt2 = ' โดยได้หักค่าธรรมเนียมออกไป 20 บาท '
            check = add(request, member[0], money)

            txt = '<p class="text-danger">เป็นแค่ staff ไม่สามารถเติมเงินให้ใครได้งับ</p>'
            if check == 1:
                txt = '<p class="text-success">ระบบได้เติมเงินใน ID : '+'%s'%member[0].id+' เป็นจำนวนเงิน '+'%s'%money_old+' บาท'+txt2+'เงินคงเหลือ '+str(member[0].money)+' บาท</p>'

        else:
            search = request.POST.get('search', '')
            member = Member.objects.filter(Q(id__icontains=search) |Q(first_name__icontains=search) | Q(last_name__icontains=search)).order_by('id')

            if search.isnumeric():
                member = Member.objects.filter(id=search)

            topup_log = TopupLog.objects.filter(member_id=member[0].id).order_by('-topup_date')
        for i in range(len(topup_log)):
            topup_log[i].topup_date = topup_log[i].topup_date.strftime("%d-%m-%Y %H:%M:%S")

        money = member[0].money
        mem = '%s'%member[0].id + ' ('+member[0].first_name+' '+member[0].last_name+')'

        if member:
            member_id = member[0].id

    context = {
        'topup_list': topup_log,
        'member':member,
        'money':money,
        'mem':mem,
        'mem_id':member_id,
        'username':"'"+request.user.username+"'",
        'txt':txt,
    }
    return render(request, template_name='money.html', context=context)

@permission_required('process.add_topuplog')
def add (user, mamber, money_update):
    mamber.money += money_update
    mamber.save()
    topup_log(mamber, user.user, '+', money_update)
    return 1

def min (mamber, money_update, user):
    mamber.money -= money_update
    mamber.save()
    topup_log(mamber, user, '-', money_update)

def topup_log(mam, user, add_or_min, money_update):
    topup_log = TopupLog(
        member = mam,
        amount = add_or_min+'%s'%money_update,
        topup_date = datetime.datetime.now(),
        topup_by = user.username
    )
    topup_log.save()
