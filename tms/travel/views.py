from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection, transaction
from django.db import connections
from datetime import datetime,timedelta

from notif.views import *

from django.core.files.storage import FileSystemStorage
from django.conf import settings
from PIL import Image
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent


import json
# Create your views here.
from django.http import HttpResponse

def home(request):
	if 'customer_id' in request.session:
		note_count = notecount(request.session['customer_id'])
		with connection.cursor() as cursor:
			cursor.execute("SELECT first_name from customer WHERE customer_id = %s", [request.session['customer_id']])
			name = cursor.fetchone()
		with connection.cursor() as cursor:
			cursor.execute("SELECT title, description,trip_id from trips WHERE customer_id = %s and start_date <= %s and end_date >= %s", [request.session['customer_id'],datetime.now().date(),datetime.now().date()])
			rows = cursor.fetchall()
		with connection.cursor() as cursor:
			cursor.execute("SELECT title, description,trip_id from trips WHERE customer_id = %s and start_date > %s" , [request.session['customer_id'],datetime.now().date()])
			upcoming_rows = cursor.fetchall()
		with connection.cursor() as cursor:
			cursor.execute("SELECT title, description,trip_id from trips WHERE customer_id = %s and end_date < %s" , [request.session['customer_id'],datetime.now().date()])
			past_rows = cursor.fetchall()
		
		log_in = True
		cnt_list = [1,1,1]
		if len(rows) == 0:
			cnt_list[0] = 0
		if len(upcoming_rows) == 0:
			cnt_list[1] = 0
		if len(past_rows) == 0:
			cnt_list[2] = 0
		return render(request, 'travel/home.html', {'rows':rows,'log_in':log_in,'first_name':name[0],'upcoming_rows':upcoming_rows,'past_rows':past_rows,'cnt_list':cnt_list,'note_count':note_count})
	return redirect('user:login')

def addtrip(request):
	if 'customer_id' in request.session:
		note_count = notecount(request.session['customer_id'])
		with connection.cursor() as cursor:
			cursor.execute("SELECT first_name from customer WHERE customer_id = %s", [request.session['customer_id']])
			name = cursor.fetchone()
		if request.method == "POST":
			title = request.POST["title"]
			description = request.POST["description"]
			drive_link = request.POST["drive_link"]
			start_date = request.POST["start_date"]
			end_date = request.POST["end_date"]
			if end_date < str(datetime.now().date()):
				messages.error(request, f'Trip cannot be added as it already ended!')
				return redirect('travel:addtrip')
			if end_date < start_date : 
				messages.error(request, f'Trip cannot be added as end date cannot be before start date!')
				return redirect('travel:addtrip')
			cursor = connections['default'].cursor()
			cursor.execute("INSERT INTO trips(title, description, drive_link, start_date, end_date, customer_id)  VALUES (%s, %s, %s,%s,%s,%s)",
					   [title, description, drive_link, start_date, end_date, request.session['customer_id']])
			with connection.cursor() as cursor:
				cursor.execute("SELECT max(trip_id) from trips WHERE customer_id = %s", [request.session['customer_id']])
				row = cursor.fetchone()
			timing = datetime.strptime(start_date,'%Y-%m-%d')
			timing -= timedelta(days=2) 
			cursor = connections['default'].cursor()
			cursor.execute("INSERT INTO notifications(trip_id,category,time_)  VALUES (%s,%s,%s)",
						[row[0],0,timing])
			timing = datetime.strptime(start_date,'%Y-%m-%d')
			timing -= timedelta(hours=12) 
			cursor = connections['default'].cursor()
			cursor.execute("INSERT INTO notifications(trip_id,category,time_)  VALUES (%s,%s,%s)",
						[row[0],1,timing])
			return redirect('travel:updtrip',tripid=row[0])
		else:
			return render(request, 'travel/addtrip.html',{'log_in':True,'first_name':name[0],'note_count':note_count})
	return redirect('user:login')

def deltrip(request,tripid):
	if 'customer_id' in request.session:
		cursor = connections['default'].cursor()
		cursor.execute("DELETE from trips WHERE trip_id = %s", [tripid])
		return redirect('travel:home')
	return redirect('user:login')


def updtrip(request,tripid):
	if 'customer_id' in request.session:
		note_count = notecount(request.session['customer_id'])
		with connection.cursor() as cursor:
			cursor.execute("SELECT first_name from customer WHERE customer_id = %s", [request.session['customer_id']])
			name = cursor.fetchone()
		if request.method == 'POST':
			title = request.POST["title"]
			description = request.POST["description"]
			drive_link = request.POST["drive_link"]
			start_date = request.POST["start_date"]
			end_date = request.POST["end_date"]
			cursor = connections['default'].cursor()
			if start_date>end_date :
				messages.error(request, f'Trip cannot be added as end date cannot be before start date!')
				return redirect('travel:updtrip',tripid=tripid)
			if end_date < str(datetime.now().date()) :
				messages.error(request, f'Trip cannot be added as it already ended!')
				return redirect('travel:updtrip',tripid=tripid) 
			cursor.execute("UPDATE trips SET title = %s, description = %s, drive_link = %s, start_date = %s, end_date = %s WHERE trip_id = %s",
					[title, description, drive_link, start_date, end_date, tripid])

		with connection.cursor() as cursor:
			cursor.execute("SELECT * from trips WHERE trip_id = %s", [tripid])
			row = cursor.fetchone()
			cursor.execute("SELECT * from location ")
			location_options = cursor.fetchall()
			cursor.execute("SELECT location_id,place_name from location natural join travels WHERE trip_id = %s", [tripid])
			row1 = cursor.fetchall()
			location_options = [i for i in location_options if i not in row1]
			cursor.execute("SELECT hotelbookid,name,cost,checkin,checkout,booking_doc,id_card from hotel natural join hotelbooking WHERE trip_id= %s", [tripid])
			row4 = cursor.fetchall()
			cursor.execute("SELECT itinerarybookid,name,title,ticket_price,visit_time,itinerarybooking.address from itinerarybooking, itinerary WHERE itinerarybooking.itineraryid=itinerary.itineraryid and trip_id= %s", [tripid])
			row5 = cursor.fetchall()
			cursor.execute("SELECT tr_id,type,trans_name,departure,arrival,from_loc,to_loc,cost,ticket from transportbooking WHERE trip_id= %s", [tripid])
			row6 = cursor.fetchall()
			cursor.execute("SELECT hotelid,name,rating from hotel natural join travels WHERE travels.location_id=hotel.location_id and trip_id= %s", [tripid])
			row2 = cursor.fetchall()
			cursor.execute("SELECT itineraryid,name,rating from travels natural join itinerary WHERE travels.location_id=itinerary.location_id and itineraryid != %s and trip_id= %s", [1,tripid])
			row3 = cursor.fetchall()

		j = 1
		row1f = []
		for i in row1:
			k = list(i)
			k.append(j)
			row1f.append(k)
			j += 1

		j = 1
		row4f = []
		for i in row4:
			k = list(i)
			k.append(j)
			row4f.append(k)
			j += 1

		j = 1
		row5f = []
		for i in row5:
			k = list(i)
			k.append(j)
			row5f.append(k)
			j += 1

		j = 1
		row6f = []
		for i in row6:
			k = list(i)
			k.append(j)
			row6f.append(k)
			j += 1

		context = {
			'log_in': True,
			'first_name': name[0],
			'title': row[2],
			'description': row[3],
			'drive_link': row[4],
			'start_date': str(row[5]),
			'end_date': str(row[6]),
			'locations': location_options,
			'locationlist' : row1f,
			'hotellist' : row4f,
			'itinerarylist' : row5f,
			'transportlist' : row6f,
			'hotels':row2,
			'itinerary': row3,
			'tripid': tripid,
			'note_count':note_count
		}
		return render(request, 'travel/updtrip.html', context)
	return redirect('user:login')



def updtransport(request,tripid):
	if 'customer_id' in request.session:
		if  request.method == "POST":
			type_t = request.POST["type"]
			from_loc = request.POST["from"]
			to_loc = request.POST["to"]
			trans_name = request.POST["trans_name"]
			cost = request.POST["cost"]
			doc = request.FILES
			if 'document_image' in request.FILES:
				doc_name = doc['document_image']
			else:
				doc_name = False
			if request.method == 'POST' and doc_name:
				image = request.FILES['document_image']
				fs = FileSystemStorage()
				image_name = fs.save(image.name, image)
				uploaded_image_url = fs.url(image_name)
			departure = request.POST["departure"]
			arrival = request.POST["arrival"]
			if arrival < departure:
				messages.error(request, f' You cannot arrive before departing!!')
			elif arrival >= departure and doc_name==False:
				cursor = connections['default'].cursor()
				cursor.execute("INSERT INTO transportbooking(type,from_loc,to_loc,trans_name,cost,departure,arrival,trip_id)  VALUES (%s, %s, %s,%s,%s,%s,%s,%s)",
						[type_t,from_loc,to_loc,trans_name,cost,departure,arrival, tripid])
				date_time_obj = datetime.strptime(departure, '%Y-%m-%dT%H:%M')
				timing = date_time_obj - timedelta(hours=1) 
				cursor = connections['default'].cursor()
				cursor.execute("INSERT INTO notifications(trip_id,category,time_)  VALUES (%s,%s,%s)",[tripid,2,timing])
			elif arrival >= departure and doc_name:
				cursor = connections['default'].cursor()
				cursor.execute("INSERT INTO transportbooking(type,from_loc,to_loc,trans_name,cost,departure,arrival,trip_id,ticket)  VALUES (%s,%s, %s, %s,%s,%s,%s,%s,%s)",
						[type_t,from_loc,to_loc,trans_name,cost,departure,arrival, tripid,uploaded_image_url])
				date_time_obj = datetime.strptime(departure, '%Y-%m-%dT%H:%M')
				timing = date_time_obj - timedelta(hours=1) 
				cursor = connections['default'].cursor()
				cursor.execute("INSERT INTO notifications(trip_id,category,time_)  VALUES (%s,%s,%s)",[tripid,2,timing])

		return redirect('travel:updtrip',tripid=tripid)
	return redirect('user:login')





def updlocation(request,tripid):
	if 'customer_id' in request.session:
		if request.method == "POST":
			location_id = request.POST["location_id"]

			cursor = connections['default'].cursor()
			cursor.execute("INSERT INTO travels(location_id,trip_id) VALUES (%s,%s)",
					[location_id, tripid])
		return redirect('travel:updtrip',tripid=tripid)
	return redirect('user:login')



def updhotel(request,tripid):
	if 'customer_id' in request.session:
		hotel_options=[]
		if request.method == "POST":
			hotelid = request.POST["hotelid"]
			cost=request.POST["cost"]
			checkin = request.POST["checkin"]
			checkout = request.POST["checkout"]
			# id_card VARCHAR(255),
			# booking_doc VARCHAR(255),
			doc = request.FILES
			if 'document_bookdoc' in request.FILES:
				doc_name1 = doc['document_bookdoc']
			else:
				doc_name1 = False
			if request.method == 'POST' and doc_name1:
				image = request.FILES['document_bookdoc']
				fs = FileSystemStorage()
				image_name = fs.save(image.name, image)
				uploaded_image_url1 = fs.url(image_name)

			if 'document_idcard' in request.FILES:
				doc_name2 = doc['document_idcard']
			else:
				doc_name2 = False
			if request.method == 'POST' and doc_name2:
				image = request.FILES['document_idcard']
				fs = FileSystemStorage()
				image_name = fs.save(image.name, image)
				uploaded_image_url2 = fs.url(image_name)
			if checkout < checkin :
				messages.error(request, f'Hotel Booking not added : You cannot checkout before checkin!!')
			elif checkout < str(datetime.now()):
				messages.error(request, f'Hotel Booking not added : You cannot have checkout date before current time!!')
			else:
				if doc_name2==False and doc_name1==False:
					cursor = connections['default'].cursor()
					cursor.execute("INSERT INTO hotelbooking(hotelid,trip_id,checkin,checkout,cost)  VALUES (%s,%s,%s,%s,%s)",
							[hotelid, tripid,checkin,checkout,cost])
				elif doc_name2==False and doc_name1:
					cursor = connections['default'].cursor()
					cursor.execute("INSERT INTO hotelbooking(hotelid,trip_id,checkin,checkout,cost,booking_doc)  VALUES (%s,%s,%s,%s,%s,%s)",
							[hotelid, tripid,checkin,checkout,cost,uploaded_image_url1])
				elif doc_name2 and doc_name1==False:
					cursor = connections['default'].cursor()
					cursor.execute("INSERT INTO hotelbooking(hotelid,trip_id,checkin,checkout,cost,id_card)  VALUES (%s,%s,%s,%s,%s,%s)",
							[hotelid, tripid,checkin,checkout,cost,uploaded_image_url2])
				elif doc_name2 and doc_name1:
					cursor = connections['default'].cursor()
					cursor.execute("INSERT INTO hotelbooking(hotelid,trip_id,checkin,checkout,cost,id_card,booking_doc)  VALUES (%s,%s,%s,%s,%s,%s,%s)",
							[hotelid, tripid,checkin,checkout,cost,uploaded_image_url2,uploaded_image_url1])

				date_time_obj = datetime.strptime(checkin, '%Y-%m-%dT%H:%M')
				timing = date_time_obj - timedelta(hours=1) 
				cursor = connections['default'].cursor()
				cursor.execute("INSERT INTO notifications(trip_id,category,time_)  VALUES (%s,%s,%s)",[tripid,3,timing])
		return redirect('travel:updtrip',tripid=tripid)
	return redirect('user:login')
	


def upditinerary(request,tripid):
	if 'customer_id' in request.session:
		itinerary_options=[]
		if request.method == "POST":
			itineraryid =request.POST["itineraryid"]
			title= request.POST["title"]
			address = request.POST["address"]
			visit_time= request.POST["visit_time"]
			ticket_price= request.POST["ticket_price"]
			if itineraryid != "Custom" :
				cursor = connections['default'].cursor()
				with connection.cursor() as cursor:
					cursor.execute("SELECT address from itinerary  WHERE  itineraryid= %s", [itineraryid])
					row = cursor.fetchone()
				address=row[0]
			else : 
				itineraryid="1"
			if visit_time < str(datetime.now()):
				messages.error(request, f'Itinerary Booking not added : You cannot have visit time date before current time!!')
			else:
				cursor = connections['default'].cursor()
				cursor.execute("INSERT INTO itinerarybooking(trip_id,itineraryid,title,address,visit_time,ticket_price)  VALUES (%s,%s,%s,%s,%s,%s)",
						[tripid,itineraryid,title,address,visit_time,ticket_price])
				date_time_obj = datetime.strptime(visit_time, '%Y-%m-%dT%H:%M')
				timing = date_time_obj - timedelta(hours=1) 
				cursor = connections['default'].cursor()
				cursor.execute("INSERT INTO notifications(trip_id,category,time_)  VALUES (%s,%s,%s)",[tripid,4,timing])
		return redirect('travel:updtrip',tripid=tripid)
	return redirect('user:login')


def deltransport(request,tr_id):
	if 'customer_id' in request.session:
		if  request.method == "POST":
			with connection.cursor() as cursor:
				cursor.execute("SELECT trip_id from transportbooking  WHERE tr_id= %s", [tr_id])
				row = cursor.fetchone()
			tripid=row[0]
			cursor = connections['default'].cursor()
			cursor.execute("DELETE from transportbooking  WHERE tr_id= %s", [tr_id])
		return redirect('travel:updtrip',tripid=tripid)
	return redirect('user:login')
		


def dellocation(request,tripid,location_id):
	if 'customer_id' in request.session:
		if request.method == "POST":
			cursor = connections['default'].cursor()
			cursor.execute("DELETE from travels WHERE location_id = %s and trip_id=%s", [location_id,tripid])
			with connection.cursor() as cursor:
				cursor.execute("SELECT hotelbookid from hotel natural join hotelbooking WHERE hotel.location_id= %s and hotelbooking.trip_id = %s", [location_id,tripid])
				row = cursor.fetchall()
			for i in row:
				cursor = connections['default'].cursor()
				cursor.execute("DELETE from hotelbooking WHERE hotelbookid = %s", [i[0]])
			with connection.cursor() as cursor:
				cursor.execute("SELECT itinerarybookid from itinerary,itinerarybooking WHERE itinerary.location_id= %s and itinerarybooking.trip_id = %s and itinerarybooking.itineraryid = itinerary.itineraryid", [location_id,tripid])
				row = cursor.fetchall()
			for i in row:
				cursor = connections['default'].cursor()
				cursor.execute("DELETE from hotelbooking WHERE hotelbookid = %s", [i[0]])
		return redirect('travel:updtrip',tripid=tripid)
	return redirect('user:login')



def delhotel(request,hotelbookid):
	if 'customer_id' in request.session:
		if request.method == "POST":
			with connection.cursor() as cursor:
				cursor.execute("SELECT trip_id from hotelbooking  WHERE hotelbookid= %s", [hotelbookid])
				row = cursor.fetchone()
			tripid=row[0]
			cursor = connections['default'].cursor()
			cursor.execute("DELETE from hotelbooking  WHERE hotelbookid= %s", [hotelbookid])
		return redirect('travel:updtrip',tripid=tripid)
	return redirect('user:login')
	


def delitinerary(request,itinerarybookid):
	if 'customer_id' in request.session:
		if request.method == "POST":
			with connection.cursor() as cursor:
				cursor.execute("SELECT trip_id from itinerarybooking  WHERE itinerarybookid= %s", [itinerarybookid])
				row = cursor.fetchone()
			tripid=row[0]
			cursor = connections['default'].cursor()
			cursor.execute("DELETE from itinerarybooking  WHERE itinerarybookid= %s", [itinerarybookid])
		return redirect('travel:updtrip',tripid=tripid)
	return redirect('user:login')
		



def details(request,tripid):
	if 'customer_id' in request.session:
		note_count = notecount(request.session['customer_id'])
		context={}
		with connection.cursor() as cursor:
			cursor.execute("SELECT first_name from customer WHERE customer_id = %s", [request.session['customer_id']])
			name = cursor.fetchone()
			cursor.execute("SELECT type,trans_name,from_loc,to_loc,departure,arrival,cost,ticket from transportbooking WHERE trip_id = %s", [tripid])
			transports = cursor.fetchall()
			cursor.execute("SELECT name,address,checkin,checkout,cost,booking_doc,id_card from hotelbooking natural join hotel WHERE trip_id = %s", [tripid])
			hotels = cursor.fetchall()
			cursor.execute("SELECT name,itinerarybooking.address,visit_time,ticket_price as cost from itinerarybooking ,  itinerary WHERE itinerarybooking.itineraryid = itinerary.itineraryid  and trip_id = %s", [tripid])
			itineraries = cursor.fetchall()
			cursor.execute("SELECT * from trips WHERE trip_id = %s", [tripid])
			trip_data = cursor.fetchone()
			total=len(transports)+len(hotels)+len(itineraries)
			i=0
			j=0
			k=0
			idx=0
			l1=["ID","Type","Transport Name","From Location","To Location","Departure","Arrival","Cost"]
			l2=["ID","Hotel Name","Address","Checkin","Checkout","Cost"]
			l3=["ID","Itinerary Title","Address","Visit Time","Ticket Price"]
			final_list=[]
			total_cost=0
			for itr in range(total) :
				s=""
				l=[]
				if i < len(transports) :
					idx=0
					s=transports[i][4]
				if j<len(hotels) :
					if s=="" or s>hotels[j][2] :
						idx=1
						s=hotels[j][2]
				if k<len(itineraries) :
					if s=="" or s>itineraries[k][2] :
						idx=2
						s=itineraries[k][2]
				if idx==0 : 
					l.append("0")
					l.append(transports[i])
					total_cost+=int(transports[i][6])
					i=i+1
					
				elif idx==1 : 
					l.append("1")
					l.append(hotels[j])
					total_cost+=int(hotels[j][4])
					j=j+1
				else : 
					l.append("2")
					l.append(itineraries[k])
					total_cost+=int(itineraries[k][3])
					k=k+1	
				final_list.append(l)

		flag2 = True
		if trip_data[6] < datetime.now().date():
			flag2 = False

		flag1 = True
		if trip_data[4] is None:
			flag1 = False
		if trip_data[4] == "":
			flag1 = False
		context = {
			'log_in': True,
			'first_name': name[0],
			'final_list': final_list,
			'trip_data':trip_data,
			'flag1':flag1,
			'flag2':flag2,
			'total_cost':total_cost,
			'note_count':note_count

		}
		return render(request, 'travel/details.html', context)
	return redirect('user:login')

def for_details(request):
	if 'customer_id' in request.session:
		return render(request, 'travel/details.html')