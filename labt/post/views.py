from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection, transaction
from django.db import connections
from datetime import datetime

# Create your views here.
from django.http import HttpResponse

def home(request):
	if 'customer_id' in request.session:
		with connection.cursor() as cursor:
			cursor.execute("SELECT first_name, moderator from customer WHERE customer_id = %s", [request.session['customer_id']])
			name = cursor.fetchone()
		with connection.cursor() as cursor:
			cursor.execute("SELECT * from post WHERE status = %s and customer_id != %s", [1,request.session['customer_id']])
			rows = cursor.fetchall()
		context = {
			'rows': rows,
			'log_in': True,
			'first_name': name[0],
			'mod': name[1]
		}
		return render(request, 'post/home.html', context)
	return redirect('user:login')


def create(request):
	if 'customer_id' in request.session:
		with connection.cursor() as cursor:
			cursor.execute("SELECT first_name, moderator from customer WHERE customer_id = %s", [request.session['customer_id']])
			name = cursor.fetchone()

		if request.method == 'POST':
			title = request.POST["title"]
			description = request.POST["description"]
			maxlimit = request.POST["maxlimit"]
			attendance = 0
			status = 0
			cursor = connections['default'].cursor()
			cursor.execute("INSERT INTO post(title, description, status, attendance, maxlimit, customer_id)  VALUES (%s, %s, %s,%s,%s,%s)",
					   [title, description, status, attendance, maxlimit, request.session['customer_id']])
			mstatus = 0
			with connection.cursor() as cursor:
				cursor.execute("SELECT post_id from post WHERE customer_id = %s ORDER BY post_id DESC", [request.session['customer_id']])
				row = cursor.fetchone()
			post_id = row[0]
			cursor = connections['default'].cursor()
			cursor.execute("INSERT INTO mrequest(post_id, status)  VALUES (%s, %s)",
					   [post_id,mstatus])
			messages.success(request, f'Post Created Successfully!')
			return redirect('post:create')
		context = {
			'log_in': True,
			'first_name': name[0],
			'mod': name[1]
		}
		return render(request, 'post/create.html', context)
	return redirect('user:login')

def join(request,post_id):
	if 'customer_id' in request.session:
		with connection.cursor() as cursor:
			cursor.execute("SELECT first_name, moderator from customer WHERE customer_id = %s", [request.session['customer_id']])
			name = cursor.fetchone()
		with connection.cursor() as cursor:
			cursor.execute("SELECT * from post WHERE post_id = %s", [post_id])
			row = cursor.fetchone()
		with connection.cursor() as cursor:
			cursor.execute("SELECT first_name from customer WHERE customer_id = %s", [row[1]])
			first_name = cursor.fetchone()
		if request.method == 'POST':
			description = request.POST["description"]
			cursor = connections['default'].cursor()
			cursor.execute("INSERT INTO request(host_id, customer_id,description,post_id)  VALUES (%s, %s, %s,%s)",
					   [row[1],request.session['customer_id'],description,post_id])
			return redirect('post:home')

		context = {
			'log_in': True,
			'first_name': name[0],
			'mod': name[1],
			'row': row,
			'hname': first_name[0]
		}
		return render(request, 'post/join.html', context)
	return redirect('user:login')

def joinrequest(request):
	if 'customer_id' in request.session:
		with connection.cursor() as cursor:
			cursor.execute("SELECT first_name, moderator from customer WHERE customer_id = %s", [request.session['customer_id']])
			name = cursor.fetchone()
		with connection.cursor() as cursor:
			cursor.execute("SELECT * from request WHERE host_id = %s", [request.session['customer_id']])
			rows = cursor.fetchall()
		context = {
			'log_in': True,
			'first_name': name[0],
			'mod': name[1],
			'rows': rows
		}
		return render(request, 'post/joinrequest.html', context)
	return redirect('user:login')

def joinapprove(request,request_id):
	if 'customer_id' in request.session:
		with connection.cursor() as cursor:
			cursor.execute("SELECT post_id, customer_id from request WHERE request_id = %s", [request_id])
			row1 = cursor.fetchone()
		with connection.cursor() as cursor:
			cursor.execute("SELECT maxlimit, attendance from post WHERE post_id = %s", [row1[0]])
			row = cursor.fetchone()
		cursor = connections['default'].cursor()
		cursor.execute(
					"DELETE from request where post_id=%s and customer_id=%s",
					[row1[0],row1[1]])
		maxlimit = row[0]
		print(maxlimit)
		attendance = row[1]
		print(attendance)
		attendance += 1
		print(attendance)
		status = 1
		print(row1[0])
		if attendance == maxlimit:
			status = 0
		cursor = connections['default'].cursor()
		cursor.execute(
					"UPDATE post SET attendance=%s, status=%s WHERE post_id = %s",
					[attendance,status,row1[0]])

		return redirect('post:home')
	return redirect('user:login')


def mrequest(request):
	if 'customer_id' in request.session:
		with connection.cursor() as cursor:
			cursor.execute("SELECT first_name, moderator from customer WHERE customer_id = %s", [request.session['customer_id']])
			name = cursor.fetchone()
		with connection.cursor() as cursor:
			cursor.execute("SELECT post_id from mrequest WHERE status = %s", [0])
			rows = cursor.fetchall()
		postrow = []
		for row in rows:
			with connection.cursor() as cursor:
				cursor.execute("SELECT title from post WHERE post_id = %s", [row[0]])
				prow = cursor.fetchone()
			ls = []
			ls.append(prow[0])
			ls.append(row[0])
			postrow.append(ls)
		context = {
			'log_in': True,
			'first_name': name[0],
			'mod': name[1],
			'postrow': postrow
		}
		return render(request, 'post/mrequest.html', context)
	return redirect('user:login')

def approve(request,post_id):
	if 'customer_id' in request.session:
		cursor = connections['default'].cursor()
		cursor.execute(
					"UPDATE post SET status=%s WHERE post_id = %s",
					[1,post_id])
		cursor = connections['default'].cursor()
		cursor.execute(
					"UPDATE mrequest SET status=%s WHERE post_id = %s",
					[1,post_id])
		return redirect('post:mrequest')
	return redirect('user:login')

