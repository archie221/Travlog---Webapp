from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection, transaction
from django.db import connections
from datetime import datetime

# Create your views here.
from django.http import HttpResponse

# from django.core.files.storage import FileSystemStorage
# from django.conf import settings
# from PIL import Image
# from pathlib import Path
# BASE_DIR = Path(__file__).resolve().parent.parent

def register(request):
	if 'customer_id' in request.session:
		messages.error(request, f'Please Logout First')
		return redirect('user:profile')
	context = {}
	if request.method == 'POST':
		first_name = request.POST["first_name"]
		last_name = request.POST["last_name"]
		gender = request.POST["gender"]
		address = request.POST["address"]
		mobile = request.POST["mobile"] 
		emailid = request.POST["email"]
		password = request.POST["password"]
		confirm_password = request.POST["confirm_password"]
		date_of_birth = request.POST["dob"]
		passkey = request.POST["passkey"]
		moderator = 0
		if passkey != "" and passkey != "mod":
			messages.error(request, f'Wrong moderator passkey')
			return redirect('user:signup')
		elif passkey == "mod":
			moderator = 1
		if len(mobile) != 10:
			messages.error(request, f'Mobile No. should be of exactly 10 digits')
			return redirect('user:signup')
		if password != confirm_password:
			messages.error(request, f'Password and Confirm Password do not match')
			context = {
				'log_in': False
			}
			return redirect('user:signup')
		cursor = connections['default'].cursor()
		try:
			cursor.execute("INSERT INTO customer(first_name, last_name, gender, address, mobile, emailid, password, dob, moderator)  VALUES (%s, %s, %s,%s,%s,%s,%s,%s,%s)",
					   [first_name, last_name, gender, address, mobile, emailid, password, date_of_birth,moderator])
		except Exception as error:
			error_str = str(error)
			if 'customer_chk_2' in error_str:
				messages.error(request, f'Mobile No. in Wrong Format')
			if 'customer_chk_3' in error_str:
				messages.error(request, f'Email ID in Wrong Format')
			return redirect('user:signup')
		return redirect('user:login')
	else:
		return render(request, 'user/register.html',{'log_in':False,'mod':False})


def login(request):
	if 'customer_id' in request.session:
		messages.error(request, f'Please Logout First')
		return redirect('user:profile')
	context = {}
	if request.method == 'POST':
		emailid = request.POST["email"]
		password = request.POST["password"]
		with connection.cursor() as cursor:
			cursor.execute("SELECT * from customer WHERE emailid = %s AND password = %s", [emailid, password])
			row = cursor.fetchone()
			if row is None:
				messages.error(request, f'User Not found! If you are new you may register first.')
				context = {
					'log_in': False
				}
				return render(request, 'user/login.html', {'log_in': False,'mod':False})

			request.session['customer_id'] = row[0]  
			return redirect('user:profile')

	else:
		return render(request, 'user/login.html',{'log_in': False,'mod':False})


def logout(request):
	if 'customer_id' in request.session:
		del request.session['customer_id']
		messages.success(request, f'Successfully Logged Out!!')
		return redirect('user:login')
	else:
		return redirect('user:login')

def profile(request):
	context = {}
	if 'customer_id' in request.session:
		if request.method == 'POST':
			first_name = request.POST["first_name"]
			last_name = request.POST["last_name"]
			emailid = request.POST["email"]
			address = request.POST["address"]
			mobile = request.POST["mobile"]
			#gender = request.POST["gender"]
			curr_password=request.POST["curr_password"]
			new_password=request.POST["new_password"]
			confirm_password=request.POST["confirm_password"]
			if len(mobile) != 10:
				messages.error(request, f'Mobile No. should be of exactly 10 digits')
				return redirect('user:profile')

			
			cursor = connections['default'].cursor()
			cursor.execute("SELECT * from customer WHERE customer_id = %s", [request.session['customer_id']])
			row = cursor.fetchone()
			if curr_password=="" and new_password=="" and confirm_password=="":
				curr_password=row[7]
				new_password=row[7]
				confirm_password=row[7]
			if curr_password!=row[7] :
				messages.error(request, f'Current Password incorrect')
				return redirect('user:profile')
			if new_password != confirm_password:
				messages.error(request, f'Password and Confirm Password do not match')
				return redirect('user:profile')
			try:
				cursor.execute(
					"UPDATE customer SET first_name = %s, last_name = %s, emailid = %s, mobile = %s, address = %s,password=%s WHERE customer_id = %s",
					[first_name, last_name, emailid, mobile, address,new_password,request.session['customer_id']])
				messages.success(request,f'Update Successful!!')
			except Exception as error:
				error_str = str(error)
				if 'customer_chk_2' in error_str:
					messages.error(request, f'Mobile No. in Wrong Format')
				if 'customer_chk_3' in error_str:
					messages.error(request, f'Email ID in Wrong Format')
				return redirect('user:profile')

		# print(first_name, last_name, email)
		with connection.cursor() as cursor:
			cursor.execute("SELECT * from customer WHERE customer_id = %s", [request.session['customer_id']])
			row = cursor.fetchone()
		context = {
			'log_in': True,
			'first_name': row[1],
			'last_name': row[2],
			'gender': row[3],
			'address': row[4],
			'mobile': row[5],
			'email': row[6],
			'curr_password' : "",
			'dob': row[8],
			'mod': row[9]
		}
		return render(request, 'user/profile.html', context)
	return redirect('user:login')

