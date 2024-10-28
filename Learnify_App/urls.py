from django.urls import path
from Learnify_App import views

urlpatterns = [
    path('',views.home),
    path('login',views.login),
    path('admin_home',views.admin_home),
    path('manage_instructors',views.manage_instructors),
    path('add_new_instructor',views.add_new_instructor),
    path('view_more_instructor/<id>',views.view_more_instructor),
    path('edit_instructor/<id>',views.edit_instructor),
    path('delete_instructor/<id>',views.delete_instructor),

    path('view_students',views.view_students),
    path('view_more_student/<id>',views.view_more_student),
    path('accept_student/<id>',views.accept_student),
    path('reject_student/<id>',views.reject_student),
    path('block_student/<id>',views.block_student),
    path('unblock_student/<id>',views.unblock_student),

    path('manage_courses',views.manage_courses),
    path('view_more_course/<id>',views.view_more_course),
    path('accept_course/<id>',views.accept_course),
    path('reject_course/<id>',views.reject_course),


    path('instructor_home',views.instructor_home),
    path('view_course',views.view_course),
    path('add_course',views.add_course),
    path('add_video_for_course',views.add_video_for_course),
    path('view_enrolled_students',views.view_enrolled_students),
    path('change_password',views.change_password),

    path('student_registration',views.student_registration),
    path('student_home',views.student_home),
    path('student_change_password',views.student_change_password),
    path('student_profile',views.student_profile),
    path('edit_profile/<id>',views.edit_profile,name='edit_profile'),

    path('update_video_progress/', views.update_video_progress, name='update_video_progress'),
    path('get_certificate/<int:enrollment_id>/', views.get_certificate, name='get_certificate'),

    path('student_view_more_course_details/<id>',views.student_view_more_course_details),

    path('user_pay_proceed/<id>/<amt>', views.user_pay_proceed),
    path('on_payment_success', views.on_payment_success),
    path('logout', views.logout),

]
