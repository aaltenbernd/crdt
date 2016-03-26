from django import forms
from django.forms import PasswordInput
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate
from .operation import *

class ChangeFolderForm(forms.Form):
	def __init__(self, *args, **kwargs):
		self.user_id = kwargs.pop('user_id')
		super(ChangeFolderForm, self).__init__(*args, **kwargs)
		self.fields['folder_choice'].choices = [('Inbox', 'Inbox')]
		self.fields['folder_choice'].choices.extend([(f.uuid, f.title) for f in getAllFolders(self.user_id)])

	folder_choice = forms.ChoiceField(widget = forms.Select(attrs={'class': "form-control input-sm"}), choices=[])
  
  	def clean(self):
  		folder_choice = self.cleaned_data['folder_choice']

  		return folder_choice

class AddFolderForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(AddFolderForm, self).__init__(*args, **kwargs)

	title = forms.CharField(required=False, widget=forms.TextInput(
		attrs={'class': 'form-control input-sm', 'placeholder': 'Foldertitle'}))

	def clean(self):
		title = self.cleaned_data['title']

		if len(title) == 0:
			self._errors['title_empty'] = "No empty folder title allowed!"

		if len(title) > 10:
			self._errors['title_length'] = "The folder title exceeds maximum length of 10 characters!"

		return title

class AddMessageForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(AddMessageForm, self).__init__(*args, **kwargs)
		self.fields['reader'].choices=[(user.username, user.username) for user in User.objects.all()]

	reader = forms.ChoiceField(widget = forms.Select(attrs={'class': "form-control input-sm"}), choices=[])

	text = forms.CharField(required=False, widget=forms.Textarea(
        attrs={'class': 'form-control text-input input-sm', 'placeholder': 'Message', 'rows': '3', 'style':'resize:none;'}))

	#reader = forms.CharField(required=False, widget=forms.Textarea(
    #    attrs={'class': 'form-control text-input input-sm', 'placeholder': 'User', 'rows': '1', 'style':'resize:none;'}))
	
	def clean(self):
		text = self.cleaned_data['text']
		reader = self.cleaned_data['reader']

		if len(text) == 0:
			self._errors['text_empty'] = "No empty messages allowed!"

		if len(text) > 320:
			self._errors['text_length'] = "The message exceeds maximum length of 320 characters!"

		return text, reader

class LoginForm(forms.Form):
	username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'class': "form-control input-sm"}),required=False)
	password = forms.CharField(label='Password', widget=PasswordInput(attrs={'class': "form-control input-sm"}), required=False)

	def clean(self):
		username = self.cleaned_data['username']
		password = self.cleaned_data['password']

		try:
			user = User.objects.get(username=username)
		except ObjectDoesNotExist:
			self._errors['user_not_exist'] = "User don't exist."

		user = authenticate(username=username, password=password)

		if not user:
			self._errors['wrong_password'] = "Wrong password."

		return user, password

class RegisterForm(forms.Form):
	username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'class': "form-control input-sm"}),required=False)
	password = forms.CharField(label='Password', widget=PasswordInput(attrs={'class': "form-control input-sm"}), required=False)
	password_confirm = forms.CharField(label='Password Confirm', widget=PasswordInput(attrs={'class': "form-control input-sm"}), required=False)

	def clean(self):
		username = self.cleaned_data['username']
		password = self.cleaned_data['password']
		password_confirm = self.cleaned_data['password_confirm']

		if len(username) == 0:
			self._errors['username_empty'] = "No empty username allowed."

		if len(password) == 0:
			self._errors['password_empty'] = "No empty password allowed."

		try:
			user = User.objects.get(username=username)
			self._errors['username_exist'] = "Username allready exists."
		except ObjectDoesNotExist:
			pass

		if password != password_confirm:
			self._errors['password_match_error'] = "Passwords don't match."

		return username, password
