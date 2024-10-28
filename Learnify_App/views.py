import os

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg
import razorpay
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import render,redirect,HttpResponse
from.models import *
from django.contrib import messages, auth
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt






def logout(request):
    auth.logout(request)
    return render(request,'index.html')





def home(request):
    auth.logout(request)

    courses = Course.objects.filter(status=True)
    instructors = Instructor.objects.all()
    return render(request, 'index.html',{'courses':courses,'instructors':instructors})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        login_fetch = Login.objects.filter(username=username,password=password)
        if login_fetch.exists():
            login_get = Login.objects.get(username=username,password=password)
            request.session['lid'] = login_get.id
            if login_get.type == 'admin':
                ob1 = auth.authenticate(username="admin", password="admin")
                if ob1 is not None:
                    auth.login(request,ob1)
                return HttpResponse('''<script>alert('Welcome Admin');window.location='/admin_home';</script>''')
            elif login_get.type == 'instructor':
                ob1 = auth.authenticate(username="admin", password="admin")
                if ob1 is not None:
                    auth.login(request, ob1)
                return HttpResponse('''<script>alert('Welcome Instructor');window.location='/instructor_home';</script>''')
            elif login_get.type == 'student':
                ob1 = auth.authenticate(username="admin", password="admin")
                if ob1 is not None:
                    auth.login(request, ob1)
                return HttpResponse('''<script>alert('Welcome Student');window.location='/student_home';</script>''')
            else:
                return HttpResponse('''<script>alert('Invalid Credentials');window.location='/login';</script>''')
        else:
            return HttpResponse('''<script>alert('Invalid');window.location='/login';</script>''')
    return render(request, 'Learnify/login.html')
@login_required(login_url='/')
def admin_home(request):
    # Fetch or calculate the statistics for courses
    total_courses = Course.objects.count()  # Total number of courses
    verified_courses = Course.objects.filter(status=True).count()  # Assuming 'status' field indicates verification
    total_enrollments = CourseEnrollment.objects.count()  # Total number of enrollments
    pending_courses = Course.objects.filter(status=False).count()  # Assuming 'status' field tracks pending verification

    # Pass the statistics to the template
    context = {
        'total_courses': total_courses,
        'verified_courses': verified_courses,
        'total_enrollments': total_enrollments,
        'pending_courses': pending_courses,
    }
    return render(request, 'admin/admin_home.html', context)


@login_required(login_url='/')
def manage_instructors(request):
    instructors = Instructor.objects.all()
    return render(request, 'admin/view_instructors.html',{'instructors':instructors})

@login_required(login_url='/')
def add_new_instructor(request):
    if request.method == 'POST':
        name = request.POST['name']
        dob = request.POST['dob']
        phone = request.POST['phone']
        email = request.POST['email']
        gender = request.POST['gender']
        password = request.POST['password']
        photo = request.FILES['photo']

        if Login.objects.filter(username=email).exists():
            return HttpResponse('''<script>alert('Username already Exists'); window.location='/add_new_instructor'</script>''')

        login_details = Login(username=email,password=password,type='instructor')
        login_details.save()

        fs = FileSystemStorage()
        fp = fs.save(photo.name,photo)

        profile = Instructor(LOGIN=login_details,name=name,dob=dob,phone=phone,email=email,gender=gender,photo=fp)
        profile.save()
        return HttpResponse('''<script>alert('Instructor Added');window.location='/manage_instructors';</script>''')
    return render(request, 'admin/add_new_instructor.html')


@login_required(login_url='/')
def view_more_instructor(request,id):
    ins = Instructor.objects.get(id=id)
    return render(request, 'admin/view_more_instructors.html',{'ins':ins})

@login_required(login_url='/')
def edit_instructor(request,id):
    ins = Instructor.objects.get(id=id)
    if request.method == 'POST':
        ins.name = request.POST['name']
        ins.dob = request.POST['dob']
        ins.phone = request.POST['phone']
        ins.email = request.POST['email']
        ins.gender = request.POST['gender']

        if 'photo' in request.FILES:
            ins.photo = request.FILES['photo']
            fs = FileSystemStorage()
            fp = fs.save(ins.photo.name,ins.photo)
            ins.photo = fp
            ins.save()
        ins.save()
        return HttpResponse('''<script>alert('Instructor Edited');window.location='/manage_instructors';</script>''')
    return render(request, 'admin/edit_instructor.html',{'ins':ins})


@login_required(login_url='/')
def delete_instructor(request,id):
    ins = Instructor.objects.get(id=id)
    ins.delete()
    return HttpResponse('''<script>alert('Instructor Deleted');window.location='/manage_instructors';</script>''')

@login_required(login_url='/')
def view_students(request):
    students = Student.objects.all().order_by('-id')
    return render(request, 'admin/view_students.html',{'students':students})

@login_required(login_url='/')
def view_more_student(request,id):
    student = Student.objects.get(id=id)
    return render(request, 'admin/view_more_student.html',{'student':student})

@login_required(login_url='/')
def accept_student(request,id):
    student = Student.objects.get(id=id)
    student.LOGIN.type = 'student'
    student.LOGIN.save()
    return redirect('/view_students')
@login_required(login_url='/')
def reject_student(request, id):
    student = Student.objects.get(id=id)
    student.LOGIN.type = 'rejected'
    student.save()
    return redirect('/view_students')
@login_required(login_url='/')
def block_student(request, id):
    student = Student.objects.get(id=id)
    student.LOGIN.type = 'blocked'
    student.save()
    return redirect('/view_students')


@login_required(login_url='/')
def unblock_student(request,id):
    student = Student.objects.get(id=id)
    student.LOGIN.type = 'student'
    student.save()
    return redirect('/view_students')


@login_required(login_url='/')
def manage_courses(request):
    course = Course.objects.all().order_by('-id')
    return render(request, 'admin/view_course.html',{'course':course})


@login_required(login_url='/')
def view_more_course(request,id):
    course = Course.objects.get(id=id)
    videos = course.course_video.all()
    return render(request, 'admin/view_more_course.html',{'course':course,'videos':videos})


@login_required(login_url='/')
def accept_course(request,id):
    course = Course.objects.get(id=id)
    course.status = True
    course.save()
    return redirect('/manage_courses')


@login_required(login_url='/')
def reject_course(request,id):
    course = Course.objects.get(id=id)
    course.status = False
    course.save()
    return redirect('/manage_courses')

#-----------------------------------------------------------------------------------------------------------------------
@login_required(login_url='/')
def instructor_home(request):
    ins = Instructor.objects.get(LOGIN=request.session['lid'])
    courses = Course.objects.filter(INSTRUCTOR=ins)
    enrollments = CourseEnrollment.objects.filter(COURSE__in=courses).select_related('COURSE').order_by('-id')

    course_stats = []
    for course in courses:
        total_enrolled = CourseEnrollment.objects.filter(COURSE=course).count()
        avg_progress = CourseEnrollment.objects.filter(COURSE=course).aggregate(Avg('progress'))['progress__avg'] or 0
        completed_courses = sum(
            [enrollment.check_completion() for enrollment in CourseEnrollment.objects.filter(COURSE=course)])

        course_stats.append({
            'course_name': course.name,
            'total_enrolled': total_enrolled,
            'avg_progress': round(avg_progress, 2),
            'completed_courses': completed_courses,
        })

    course_names = [course.name for course in courses]
    total_enrollments = [CourseEnrollment.objects.filter(COURSE=course).count() for course in courses]

    course_names_json = json.dumps(course_names)
    total_enrollments_json = json.dumps(total_enrollments)

    return render(request, 'instructor/instructor_home.html', {
        'enrollments': enrollments,
        'course_stats': course_stats,
        'course_names_json': course_names_json,
        'total_enrollments_json': total_enrollments_json,
    })



@login_required(login_url='/')
def view_course(request):
    instructor = Instructor.objects.get(LOGIN=request.session['lid'])
    courses = Course.objects.filter(INSTRUCTOR=instructor)
    selected_course = None
    videos = []
    if request.method == 'POST':
        selected_course_id = request.POST.get('selected_course')
        if selected_course_id:
            selected_course = Course.objects.get(id=selected_course_id)
            videos = selected_course.course_video.all()

    return render(request, 'instructor/view_course.html', {
        'courses': courses,
        'selected_course': selected_course,
        'videos': videos,
    })


@login_required(login_url='/')
def add_course(request):
    if request.method == 'POST':
        instructor = Instructor.objects.get(LOGIN=request.session['lid'])
        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']
        thumbnail = request.FILES['thumbnail']
        fs = FileSystemStorage()
        fp = fs.save(thumbnail.name,thumbnail)
        course = Course(
            INSTRUCTOR=instructor,
            name=name,
            description=description,
            price=price,
            thumbnail=fp
        )
        course.save()
        return HttpResponse('''<script>alert('Course Added');window.location='/view_course';</script>''')
    return render(request, 'instructor/add_new_course.html')


@login_required(login_url='/')
def add_video_for_course(request):
    if request.method == 'POST':
        course_id = request.POST['course_id']
        course = Course.objects.get(id=course_id)
        video_file = request.FILES.get('video_file')
        image = request.FILES['image']

        fs = FileSystemStorage()
        fp = fs.save(image.name,image)

        if video_file:
            course_video = CourseVideos(
                COURSE=course,
                file=video_file,
                thumbnail=fp
            )
            course_video.save()
            messages.success(request, 'Video uploaded successfully!')
        else:
            messages.error(request, 'No video file uploaded.')
            return redirect('/view_course')
        return redirect('/view_course')


@login_required(login_url='/')
def view_enrolled_students(request):
    ins = Instructor.objects.get(LOGIN=request.session['lid'])
    courses = Course.objects.filter(INSTRUCTOR=ins)
    enroll = CourseEnrollment.objects.filter(COURSE__in=courses).order_by('-id')
    return render(request, 'instructor/view_enroll.html',{'enroll':enroll})

@login_required(login_url='/')
def change_password(request):
    if request.method == 'POST':
        old = request.POST['old']
        new = request.POST['new']
        confirm = request.POST['confirm']

        instructor = Login.objects.get(id=request.session['lid'])
        if instructor.password == old:
            if new == confirm:
                instructor.password = confirm
                instructor.save()
                return HttpResponse('''<script>alert("Password changed successfully!");window.location='/instructor_home';</script>''')
            else:
                return HttpResponse('''<script>alert("New Password and Confirm Password do not match");window.location='/change_password';</script>''')
        return HttpResponse('''<script>alert("Old Password is incorrect");window.location='/change_password';</script>''')
    return render(request, 'instructor/change_password.html')



#-----------------------------------------------------------------------------------------------------------------------


#@login_required(login_url='/')
def student_registration(request):
    if request.method == 'POST':
        name = request.POST['name']
        gender  =request.POST['gender']
        phone = request.POST['phone']
        email = request.POST['email']
        photo = request.FILES['photo']
        dob = request.POST['dob']
        password = request.POST['password']

        if Login.objects.filter(username=email).exists():
            return HttpResponse('''<script>alert('Username already exists');window.location='/student_registration';</script>''')

        fs = FileSystemStorage()
        fp = fs.save(photo.name,photo)

        login_details = Login(
            username=email,
            password=password,
            type='student'
        )
        login_details.save()

        profile = Student(
            LOGIN=login_details,
            name=name,
            gender=gender,
            phone=phone,
            email=email,
            photo=fp,
            dob=dob,
        )
        profile.save()
        return redirect('/')
    return render(request, 'student/registration.html')


@login_required(login_url='/')
def student_change_password(request):
    if request.method == 'POST':
        old = request.POST['old']
        new = request.POST['new']
        confirm = request.POST['confirm']

        student = Login.objects.get(id=request.session['lid'])
        if student.password == old:
            if new == confirm:
                student.password = confirm
                student.save()
                return HttpResponse('''<script>alert("Password changed successfully!");window.location='/student_profile';</script>''')
            else:
                return HttpResponse('''<script>alert("New Password and Confirm Password do not match");window.location='/student_change_password';</script>''')
        return HttpResponse('''<script>alert("Old Password is incorrect");window.location='/student_change_password';</script>''')
    return render(request, 'student/change_password.html')



@login_required(login_url='/')
def student_home(request):
    courses = Course.objects.filter(status=True)
    instructors = Instructor.objects.all()
    return render(request, 'student/student new home.html',{'courses':courses,'instructors':instructors})

@login_required(login_url='/')
def edit_profile(request, id):
    profile = Student.objects.get(LOGIN_id=request.session['lid'])
    if request.method == 'POST':
        profile.name = request.POST.get('name')
        profile.gender = request.POST.get('gender')
        profile.phone = request.POST.get('phone')
        profile.email = request.POST.get('email')
        profile.dob = request.POST.get('dob')
        if 'photo' in request.FILES:
            profile.photo = request.FILES['photo']
            fs = FileSystemStorage()
            fp = fs.save(profile.photo.name,profile.photo)
            profile.photo = fp
            profile.save()
        profile.save()
        return HttpResponse('''<script>alert("Edited successfully!");window.location='/student_profile';</script>''')
    return render(request, 'student/edit_profile.html', {'profile': profile})



@login_required(login_url='/')
def student_view_more_course_details(request,id):
    course = Course.objects.get(id=id)
    videos = CourseVideos.objects.filter(COURSE_id=course)
    student = Student.objects.get(LOGIN_id=request.session['lid'])
    enrollment = CourseEnrollment.objects.filter(COURSE=course, STUDENT=student).exists()
    return render(request, 'student/view_more_course_details.html',{'course':course,'videos':videos,'enrollment':enrollment})


@login_required(login_url='/')
def user_pay_proceed(request,id,amt):
    request.session['rid'] = id
    request.session['pay_amount'] = amt
    client = razorpay.Client(auth=("rzp_test_edrzdb8Gbx5U5M", "XgwjnFvJQNG6cS7Q13aHKDJj"))
    print(client)
    payment = client.order.create({'amount': str(amt)+"00", 'currency': "INR", 'payment_capture': '1'})
    return render(request,'student/UserPayProceed.html',{'p':payment,'val':[],"lid":request.session['lid'],"id":request.session['rid']})


def on_payment_success(request):
    request.session['rid'] = request.GET['id']
    request.session['lid'] = request.GET['lid']
    student = Student.objects.get(LOGIN_id=request.session['lid'])
    course = Course.objects.get(id=request.session['rid'])
    ob1 = auth.authenticate(username="admin", password="admin")
    if ob1 is not None:
        auth.login(request, ob1)
    CourseEnrollment.objects.create(
        STUDENT=student,
        COURSE=course,
        payment_status=True,  # Mark payment as completed
        progress=0.0  # Initial course progress
    )
    return redirect("/student_profile")


def calculate_course_progress(enrollment):
    print("==========================1")
    total_videos = CourseVideos.objects.filter(COURSE=enrollment.COURSE).count()
    if total_videos == 0:
        return 0
    print("==========================2")
    completed_videos = CourseProgress.objects.filter(ENROLLMENT=enrollment, completed=True).count()
    return (completed_videos / total_videos) * 100


@csrf_exempt
def update_video_progress(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            enrollment_id = data.get('enrollment_id')
            video_id = data.get('video_id')
            watched_time = data.get('watched_time')
            duration = data.get('duration')

            print(
                f'Received data: enrollment_id={enrollment_id}, video_id={video_id}, watched_time={watched_time}, duration={duration}')

            if not all([enrollment_id, video_id, watched_time is not None, duration is not None]):
                return JsonResponse({'success': False, 'error': 'Missing required parameters'})

            try:
                enrollment = CourseEnrollment.objects.get(id=enrollment_id)
                video = CourseVideos.objects.get(id=video_id)
            except (CourseEnrollment.DoesNotExist, CourseVideos.DoesNotExist) as e:
                return JsonResponse({'success': False, 'error': str(e)})

            progress, created = CourseProgress.objects.update_or_create(
                ENROLLMENT=enrollment,
                VIDEO=video,
                defaults={
                    'watched_time': watched_time,
                    'completed': watched_time >= (duration * 0.9)  # Mark as completed if 90% watched
                }
            )

            course_progress = calculate_course_progress(enrollment)
            enrollment.progress = course_progress
            enrollment.save()

            return JsonResponse({
                'success': True,
                'course_progress': course_progress,
                'video_progress': progress.watched_time,
                'video_completed': progress.completed
            })

        except Exception as e:
            print(f'Error in update_video_progress: {str(e)}')
            return JsonResponse({'success': False, 'error': f'An error occurred: {str(e)}'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})



@login_required(login_url='/')
def student_profile(request):
    my_profile = Student.objects.get(LOGIN_id=request.session['lid'])
    my_courses = CourseEnrollment.objects.filter(STUDENT__LOGIN_id=request.session['lid'])

    course_progress_data = []
    for enrollment in my_courses:
        course = enrollment.COURSE
        course_progress = calculate_course_progress(enrollment)
        course_videos = CourseVideos.objects.filter(COURSE=course)

        # Get progress for all videos in this course
        video_progress = CourseProgress.objects.filter(
            ENROLLMENT=enrollment,
            VIDEO__in=course_videos
        ).values('VIDEO_id', 'watched_time', 'completed')

        # Create a dictionary for easy lookup
        video_progress_dict = {vp['VIDEO_id']: vp for vp in video_progress}

        videos_with_progress = [
            {
                'video': video,
                'enrollment_id': enrollment.id,
                'progress': video_progress_dict.get(video.id, {'watched_time': 0, 'completed': False})
            } for video in course_videos
        ]

        course_progress_data.append({
            'enrollment': enrollment,
            'course': course,
            'course_progress': course_progress,
            'videos': videos_with_progress,
            'is_completed': course_progress == 100
        })
    return render(request, 'student/my_profile.html', {
        'my_profile': my_profile,
        'course_progress_data': course_progress_data
    })



@login_required(login_url='/')
def get_certificate(request, enrollment_id):
    default_pdf_path = os.path.join(settings.MEDIA_ROOT, 'certificate.pdf')  # Change 'default_certificate.pdf' to your file name

    if os.path.exists(default_pdf_path):
        with open(default_pdf_path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="COURSE_CERTIFICATE.pdf"'
            return response
    else:
        return HttpResponse("Certificate not found", status=404)
