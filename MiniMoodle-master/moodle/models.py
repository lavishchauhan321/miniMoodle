from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import uuid

# Create your models here.

class Course(models.Model):
	"""Model representing a course"""
	name = models.CharField(max_length=6,primary_key=True)
	professor = models.OneToOneField(User,blank=False,null=False,on_delete=models.CASCADE,related_name="courses")
	student =models.ManyToManyField(User,blank=True)
	limit = models.PositiveIntegerField(blank=False)

	def __str__(self):
		return self.name
	
	def get_absolute_url(self):
		return reverse('course-detail',args=[str(self.name)])

class Message(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4,)
	title=models.CharField(max_length=100,blank=False)
	content=models.CharField(max_length=500,blank=False)
	course=models.ForeignKey(Course,blank=False,null=False,on_delete=models.CASCADE)
	timestamp=models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.title
		
		
class EnrollTime(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4)
	enrolltime=models.DateTimeField(auto_now=True)
	stud= models.ForeignKey(User,on_delete=models.CASCADE,blank=False,null =False)
	relcourse=models.ForeignKey(Course,on_delete=models.CASCADE,blank=False, null = False)
