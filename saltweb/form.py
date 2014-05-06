#!/usr/bin/env python
#coding=utf-8
#author: hhr
from django import forms

class upfileForm(forms.Form):
    file = forms.FileField(label='选择文件')

class downfileForm(forms.Form):
    file = forms.CharField(label = '选择文件')


#class chpasswdForm(forms.Form):
#    host = forms.CharField(max_length=10,label = '匹配主机')
#    username = forms.CharField(max_length=10,label = '用户名')
#    passwd = forms.CharField(max_length=10,label = '密码',widget=forms.PasswordInput())
   
