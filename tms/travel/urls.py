from django.urls import path
from . import views

app_name = 'travel'

urlpatterns = [

	path('', views.home, name='home'),
	path('addtrip/', views.addtrip, name='addtrip'),
	path('deltrip/tripid=<tripid>', views.deltrip, name='deltrip'),
	path('updtrip/tripid=<tripid>', views.updtrip, name='updtrip'),
	path('updhotel/tripid=<tripid>', views.updhotel, name='updhotel'),
	path('upditinerary/tripid=<tripid>', views.upditinerary, name='upditinerary'),
	path('updlocation/tripid=<tripid>', views.updlocation, name='updlocation'),
	path('updtransport/tripid=<tripid>', views.updtransport, name='updtransport'),
	path('deltransport/trid=<tr_id>', views.deltransport, name='deltransport'),
	path('delitinerary/itineraryid=<itinerarybookid>', views.delitinerary, name='delitinerary'),
	path('dellocation/tripid=<tripid>/locationid=<location_id>', views.dellocation, name='dellocation'),
	path('delhotel/hotelid=<hotelbookid>', views.delhotel, name='delhotel'),
	path('details/tripid=<tripid>', views.details, name='details')

]