from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection, transaction
from django.db import connections
from datetime import datetime, timedelta

# Create your views here.
from django.http import HttpResponse

def notecount(userid):
	with connection.cursor() as cursor:
		cursor.execute("SELECT time_ from trips as t, notifications as n WHERE customer_id = %s and n.trip_id = t.trip_id ORDER BY time_ ASC", [userid])
		rows = cursor.fetchall()
	count = 0
	for row in rows:
		if row[0] <= datetime.now():
			count += 1
		else:
			break
	return count


def notify(request):
	if 'customer_id' in request.session:
		with connection.cursor() as cursor:
			cursor.execute("SELECT first_name from customer WHERE customer_id = %s", [request.session['customer_id']])
			name = cursor.fetchone()
		with connection.cursor() as cursor:
			cursor.execute("SELECT n.time_,n.category,n.trip_id,n.note_id from trips as t, notifications as n WHERE customer_id = %s and n.trip_id = t.trip_id ORDER BY n.time_ DESC", [request.session['customer_id']])
			rows = cursor.fetchall()
		notifs = []
		for row in rows:
			notif_dict = []
			if row[0] <= datetime.now():
				time1 = row[0] + timedelta(hours=1)
				notif_dict.append(row[2]) 
				with connection.cursor() as cursor:
						cursor.execute("SELECT title, start_date from trips WHERE trip_id = %s", [row[2]])
						trip = cursor.fetchone()
				if row[1] == 0:
					header = "Attention!!"
					notif_dict.append(header) 
					msg = "PACK UP YOUR THINGS: Your trip titled " + str(trip[0]) + " is going to start in 2 days i.e. from " + str(trip[1])
					notif_dict.append(msg) 
				elif row[1] == 1:
					header = "Best Wishes!!"
					notif_dict.append(header) 
					msg = "HAPPY JOURNEY: For Your trip titled " + str(trip[0])
					notif_dict.append(msg) 
				elif row[1] == 2:
					with connection.cursor() as cursor:
						cursor.execute("SELECT type from transportbooking WHERE trip_id = %s and departure = %s", [row[2],time1])
						transport = cursor.fetchone()
					if(transport is None):
						cursor = connections['default'].cursor()
						cursor.execute("DELETE from notifications WHERE note_id = %s", [row[3]])
						continue
					header = "Hurry!!"
					notif_dict.append(header) 
					msg = str(trip[0]) + ": You have your " + str(transport[0]) + " in 1 hour i.e. at " + str(time1.time()) + " . Buckle up faster for this ride"
					notif_dict.append(msg) 
				elif row[1] == 3:
					with connection.cursor() as cursor:
						cursor.execute("SELECT hotelid from hotelbooking WHERE trip_id = %s and checkin = %s", [row[2],time1])
						hotel = cursor.fetchone()
					if(hotel is None):
						cursor = connections['default'].cursor()
						cursor.execute("DELETE from notifications WHERE note_id = %s", [row[3]])
						continue
					with connection.cursor() as cursor:
						cursor.execute("SELECT name from hotel WHERE hotelid = %s", [hotel[0]])
						hotelname = cursor.fetchone()
					header = "Hurry!!"
					notif_dict.append(header) 
					msg = str(trip[0]) + ": You have your " + str(hotelname[0]) + " hotel checkin in 1 hour i.e. at " + str(time1.time()) + " . Buckle up faster for this ride"
					notif_dict.append(msg) 
				elif row[1] == 4:
					with connection.cursor() as cursor:
						cursor.execute("SELECT itineraryid from itinerarybooking WHERE trip_id = %s and visit_time = %s", [row[2],time1])
						itinerary = cursor.fetchone()
					if(itinerary is None):
						cursor = connections['default'].cursor()
						cursor.execute("DELETE from notifications WHERE note_id = %s", [row[3]])
						continue
					with connection.cursor() as cursor:
						cursor.execute("SELECT name from itinerary WHERE itineraryid = %s", [itinerary[0]])
						itineraryname = cursor.fetchone()
					header = "Hurry!!"
					notif_dict.append(header) 
					msg = str(trip[0]) + ": You have your " + str(itinerary[0]) + " visiting time in 1 hour i.e. at " + str(time1.time()) + ". Buckle up faster for this adventure"
					notif_dict.append(msg) 
				notifs.append(notif_dict)
				cursor = connections['default'].cursor()
				cursor.execute("DELETE from notifications WHERE note_id = %s", [row[3]])

		note_count = notecount(request.session['customer_id'])
		context = {'log_in': True, 'ndict': notifs, 'first_name':name[0],'note_count':note_count}
		return render(request, 'notif/notifications.html', context)
	return redirect('user:login')