from django.conf.urls import patterns, include, url
from grading import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^init_student$', views.init_student, name='init_student'),
    url(r'^add_assign$', views.add_assign, name='add_assign'),
    url(r'^init_grade_table/(?P<assign_name>\w+)/$', views.init_grade_table, name='init_grade_table'),
    url(r'^show_grade/(?P<assign_name>\w+)/$', views.show_grade, name='show_grade'),
    url(r'^grade/(?P<assign_name>\w+)/(?P<netID>\w+)/$', views.grade, name='grade'),
)
