from django import forms
from django.forms import PasswordInput
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate

from .models import AddMessage, AddFolder

class ChangeFolderForm(forms.Form):
	folder_choice = forms.ModelChoiceField(label='Folder', empty_label="Inbox", queryset = AddFolder.objects.all(), widget=forms.Select(attrs={'class': "form-control"}), required=False)

	def clean(self):
		folder_choice = self.cleaned_data['folder_choice']

		return folder_choice

class AddFolderForm(forms.Form):
	title = forms.CharField(required=False, widget=forms.TextInput(
		attrs={'class': 'form-control', 'placeholder': 'Foldertitle'}))

	def clean(self):
		title = self.cleaned_data['title']

		if len(title) == 0:
			self._errors['title_empty'] = "No empty messages allowed"

		if len(title) > 10:
			self._errors['title_length'] = "The title exceeds maximum length of 10 characters"

		return title

class AddMessageForm(forms.Form):
	to = forms.CharField(required=False, widget=forms.TextInput(
		attrs={'class': 'form-control', 'placeholder': 'myself', 'readonly':'readonly'}))
	text = forms.CharField(required=False, widget=forms.Textarea(
        attrs={'class': 'form-control text-input', 'placeholder': 'Message', 'rows': '3', 'style':'resize:none;'}))

	def clean(self):
		text = self.cleaned_data['text']
		to = self.cleaned_data['to']

		if len(text) == 0:
			self._errors['text_empty'] = "No empty messages allowed"

		if len(text) > 320:
			self._errors['text_length'] = "The text exceeds maximum length of 320 characters"

		return text, to

class LoginForm(forms.Form):
	username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'class': "form-control"}),required=False)
	password = forms.CharField(label='Password', widget=PasswordInput(attrs={'class': "form-control"}), required=False)

	def clean(self):
		username = self.cleaned_data['username']
		password = self.cleaned_data['password']

		try:
			user = User.objects.get(username=username)
		except ObjectDoesNotExist:
			self._errors['user_not_exit'] = "User don't exist."
			return username, password

		user = authenticate(username=username, password=password)

		if not user:
			self._errors['wrong_password'] = "Wrong password."

		return user, password