# -*- coding:utf-8 -*-
from django.conf.urls import patterns, include, url


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'ueditor.app.Ueditor.views.testueditor'),
    
    url(r'^ueditor_imgup$','ueditor.app.Ueditor.views.ueditor_ImgUp'),
    url(r'^ueditor_fileup$','ueditor.app.Ueditor.views.ueditor_FileUp'),
    url(r'^ueditor_getRemoteImage$','ueditor.app.Ueditor.views.ueditor_getRemoteImage'),
    url(r'^ueditor_scrawlUp$','ueditor.app.Ueditor.views.ueditor_ScrawUp'),
    url(r'^ueditor_getMovie$','ueditor.app.Ueditor.views.ueditor_getMovie'),
    url(r'^ueditor_imageManager$','ueditor.app.Ueditor.views.ueditor_imageManager'),
)