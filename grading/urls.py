from django.conf.urls import patterns, include, url
from grading import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^init_student$', views.init_student, name='init_student'),
    url(r'^show_students$', views.show_students, name='show_students'),
    url(r'^add_assign$', views.add_assign, name='add_assign'),
    url(r'^remove_assign/(?P<assign_name>\w+)/$', views.remove_assign, name='remove_assign'),
    url(r'^init_grade_table/(?P<assign_name>\w+)/$', views.init_grade_table, name='init_grade_table'),
    url(r'^show_grade/(?P<assign_name>\w+)/$', views.show_grade, name='show_grade'),
    url(r'^grade/(?P<assign_name>\w+)/(?P<netID>\w+)/$', views.grade, name='grade'),
    url(r'^send_email_all/(?P<assign_name>\w+)/$', views.send_email_all, name='send_email_all'),
    url(r'^compute_grades/(?P<assign_name>\w+)/$', views.compute_grades, name='compute_grades'),
    url(r'^deduction_details/(?P<assign_name>\w+)/(?P<netID>\w+)/$', views.deduction_details, name='deduction_details'),
    url(r'^send_email/(?P<assign_name>\w+)/(?P<netID>\w+)/$', views.send_email, name='send_email'),
    url(r'^output2csv/(?P<assign_name>\w+)/$', views.output2csv, name='output2csv'),
)
