from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
	path('',views.home,name='home'),
	path('courses/',views.courses,name='courses'),
	url(r'^courses/(?P<pk>\w+)/$',views.courseDetail,name='course-detail'),
	url(r'^courses/(?P<pk>\w+)/enroll/$',views.courseEnroll,name='enroll'),
	url(r'^courses/(?P<pk>\w+)/drop/$',views.courseDrop,name='drop'),
	url(r'^courses/(?P<pk>\w+)/delete/$',views.courseDelete,name='delete'),
	path('newcourse/',views.newCourse,name='new-course'),
	url(r'^message/(?P<pk>[-\w]+)/delete/$',views.msgDelete,name='msg-delete'),
	path('newuser/',views.newUser,name='new-user'),
	path('allcourses/',views.allcourses,name='allcourses'),
]
