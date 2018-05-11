from django.shortcuts import render, redirect,reverse, get_object_or_404
from .models import Course,Message,EnrollTime
from .forms import NewCourse, NewPost, NewUser
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User,Group
from datetime import datetime,timedelta
from django.contrib import messages
# Create your views here.


'''Not views, just helper functions'''
def group(name,request):
	return request.user.groups.filter(name=name).exists()
	

def is_professor(user):
	return 'Professor' == user.groups.all()[0].name

def is_student(user):
	return 'Student' == user.groups.all()[0].name
	
def is_admin(user):
	return 'admin'== user.username
	
	
	
'''Views'''

	
@login_required
def home(request):
	'''Home page'''

	posts= Message.objects.exclude(timestamp__lt=(datetime.now()-timedelta(days=1)))
	return render( 
		request, 'home.html' , 
		context = { 'courses':courses , 
		'student':group('Student',request),'professor':group('Professor',request),'posts':posts}
	)


@login_required
@user_passes_test(is_student,'home','')
def courses(request):
	'''Page with all the courses in which student has enrolled'''
	
	courses= Course.objects.filter(student__username=request.user.username)
	return render( 
		request, 
		'courses.html' , 
		context = {'courses':courses,'student':group('Student',request)} 
	)
	

@login_required	
def allcourses(request):
	courses=Course.objects.all()
	return render(
		request, 
		'allcourses.html',
		context = {'courses':courses,'student':group('Student',request),'professor':group('Professor',request)}
	)
	

@login_required	
def courseDetail(request,pk):
	course = get_object_or_404(Course,pk=pk)
	posts= Message.objects.filter(course=course)
	
	full =(course.student.all().count()==course.limit)
	#If the user is a student
	if request.user.groups.all()  and 'Student' == request.user.groups.all()[0].name:
	
		enrolled=request.user in course.student.all()
		#getting enroll time for the student if he is enrolled in the course
		if enrolled:
			enrollt=EnrollTime.objects.filter(relcourse=course).filter(stud=request.user)[0].enrolltime
		else:
			enrollt=datetime.now()
			
		#This queryset contains messages only after the enrollement time
		msg_stud=Message.objects.filter(course=course).filter(timestamp__gt=enrollt)
		
		return render(
			request, 
			'course_student.html',
			context = {'course':course,'enrolled':enrolled,'posts':msg_stud,'student':group('Student',request),'full':full}
		)
	
	#If the user is professor
	else:
	
		#If he is the course professor
		if request.user == course.professor:
		
			if request.method=="POST":
				form=NewPost(request.POST)
		
				if form.is_valid():
					title=form.cleaned_data['title']
					content=form.cleaned_data['content']
					
					message=Message(title=title,content=content,course=request.user.courses)
					message.save()
					
					form=NewPost()
					
					return redirect('course-detail',course.name)
					
			else:
				form = NewPost()

			return render(
				request,
				'course_professor.html',
				 context={'form':form,'posts':posts,'course':course,'check':request.user == course.professor,'professor':True}
			)
			
		# If he is not the course professor
		else:
			return render(
				request , 
				'course_professor.html',				
				context={'course':course,'professor':True,}
			)
		
				
#proxy view for enrolling into a course
@login_required
@user_passes_test(is_student,'home','')
def courseEnroll(request,pk):
	course = get_object_or_404(Course,pk=pk)
	
	course.student.add(request.user)
	course.save()
	
	time=EnrollTime(stud=request.user,relcourse=course)
	time.save()
	return redirect( 'course-detail', course.name)
	

#proxy view for dropping out of a courses
@login_required	
@user_passes_test(is_student,'home','')
def courseDrop(request,pk):
	course = get_object_or_404(Course,pk=pk)
	
	course.student.remove(request.user)
	course.save()
	
	time=EnrollTime.objects.filter(relcourse=course).filter(stud=request.user)[0]
	time.delete()
	
	return redirect( 'course-detail', course.name)


#proxy view for deleting a course
@login_required	
@user_passes_test(is_professor,'home','')
def courseDelete(request,pk):
	course=get_object_or_404(Course,pk=pk)
	if course.professor==request.user:
		course.delete()
		return redirect('new-course')
	else:
		return redirect('home')


@login_required
@user_passes_test(is_professor,'home','')
def newCourse(request):

	if request.method=='POST':
		form=NewCourse(request.POST)
	
		if form.is_valid():
			name=request.POST.get('name')
			limit=request.POST.get('limit')
			
			if Course.objects.filter(name=name).exists():
				form=NewCourse()
				course=Course.objects.filter(name=name)
				messages.add_message(request,messages.ERROR, 'Course with this name has already been offered by'+course.professor.first_name+course.professor.last_name)
				return redirect('new-course')
			else:
				course=Course(name=name,professor=request.user,limit=limit)
				course.save()
				messages.add_message(request,messages.INFO, 'Created a new course')

				return redirect(
					'course-detail',
					course.name
				)
	else:
		form=NewCourse()	
	
	return render( 
		request, 
		'new_course.html',
		context = {'form':form,'professor':True}
	)
	

#proxy view for deleting a message
@user_passes_test(is_professor,'home','')
def msgDelete(request,pk):
	message=get_object_or_404(Message,pk=pk)
	message.delete()
	
	return redirect(
		'course-detail',
		request.user.courses
	)
	
	
	
#view for admin to create new user
@user_passes_test(is_admin,'home','')
def newUser(request):
	if request.method=="POST":
		form=NewUser(request.POST)
		if form.is_valid():
			if not User.objects.filter(username=form.cleaned_data.get('username')).exists():
				user=form.save()
				user.refresh_from_db()
				group=Group.objects.get(name=form.cleaned_data.get('group'))
				fname=form.cleaned_data.get('fname')
				lname=form.cleaned_data.get('lname')
				user.first_name=fname
				user.last_name=lname
				group.user_set.add(user)
				user.save()
				messages.add_message(request,messages.INFO,'New User added')
				return redirect(
					'home'
					)
			
			else:
				return redirect('new-user')
		else:
			return render(request,
				'new_user.html',
				context={'form':form}
				)
	else:
		form=NewUser()
		return render( 
			request,
			'new_user.html',
			context={'form':form}
			)
