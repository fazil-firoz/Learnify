from django.db import models

class Login(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    type = models.CharField(max_length=20)

class Instructor(models.Model):
    LOGIN = models.ForeignKey(Login, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    dob = models.DateField()
    phone = models.BigIntegerField()
    email = models.CharField(max_length=40)
    gender = models.CharField(max_length=30)
    photo = models.ImageField(upload_to='Instructor/')


class Course(models.Model):
    INSTRUCTOR = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name='course')
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=200)
    price = models.IntegerField()
    thumbnail = models.ImageField(upload_to='thumbnails/')
    status = models.BooleanField(default=False)

class CourseVideos(models.Model):
    COURSE =  models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_video')
    thumbnail = models.ImageField(upload_to='video_thumbnails/')
    file = models.FileField(upload_to='course_video_file/')
    duration = models.FloatField(default=0.0)

class Student(models.Model):
    LOGIN = models.ForeignKey(Login, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    gender = models.CharField(max_length=40)
    phone = models.BigIntegerField()
    email = models.CharField(max_length=40)
    photo = models.ImageField(upload_to='Student/')
    dob = models.DateField()

class CourseEnrollment(models.Model):
    STUDENT = models.ForeignKey(Student, on_delete=models.CASCADE,related_name='enrollment')
    COURSE = models.ForeignKey(Course, on_delete=models.CASCADE,related_name='enrollment')
    payment_status = models.BooleanField(default=False)  # True if payment is completed
    date_enrolled = models.DateTimeField(auto_now_add=True)
    progress = models.FloatField(default=0.0)  # Track video completion progress

    def check_completion(self):
        total_videos = CourseVideos.objects.filter(COURSE=self.COURSE).count()
        completed_videos = CourseProgress.objects.filter(ENROLLMENT=self, completed=True).count()
        return completed_videos == total_videos

class CourseProgress(models.Model):
    ENROLLMENT = models.ForeignKey(CourseEnrollment,on_delete=models.CASCADE)
    VIDEO = models.ForeignKey(CourseVideos, on_delete=models.CASCADE)
    watched_time = models.FloatField(default=0.0)
    completed = models.BooleanField(default=False)
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('ENROLLMENT', 'VIDEO')