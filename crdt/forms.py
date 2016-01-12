from django import forms
from django.forms import PasswordInput
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate

from .models import AddMessage, AddFolder, DeleteFolder

class ChangeFolderForm(forms.Form):
	def __init__(self, *args, **kwargs):
		self.active_host = kwargs.pop('active_host')
		self.active_folder_id = kwargs.pop('active_folder_id')
		self.folders = AddFolder.objects.filter(host_id=self.active_host)
		self.del_folders = DeleteFolder.objects.filter(host_id=self.active_host)
		for del_folder in self.del_folders:
			self.folders = self.folders.exclude(uuid=del_folder.uuid)
		super(ChangeFolderForm, self).__init__(*args, **kwargs)

		if self.active_folder_id == 'None':
			self.fields['folder_choice'].empty_label = None
			self.fields['folder_choice'].queryset = self.folders
		else:
			self.fields['folder_choice'].empty_label = "Inbox"
			self.fields['folder_choice'].queryset = self.folders.exclude(uuid=self.active_folder_id)
		

	folder_choice = forms.ModelChoiceField(queryset = AddFolder.objects.none(), required=False, empty_label=None, label='Folder', widget = forms.Select(attrs={'class': "form-control"}))

	def clean(self):
		folder_choice = self.cleaned_data['folder_choice']

		return folder_choice

class AddFolderForm(forms.Form):
	def __init__(self, *args, **kwargs):
		self.host_id = kwargs.pop('host_id')
		super(AddFolderForm, self).__init__(*args, **kwargs)

	title = forms.CharField(required=False, widget=forms.TextInput(
		attrs={'class': 'form-control', 'placeholder': 'Foldertitle'}))

	def clean(self):
		title = self.cleaned_data['title']

		if len(title) == 0:
			self._errors['title_empty'] = "No empty folder title allowed!"

		if len(title) > 10:
			self._errors['title_length'] = "The folder title exceeds maximum length of 10 characters!"

		folders = AddFolder.objects.filter(host_id=self.host_id)
		for delete_folder in DeleteFolder.objects.filter(host_id=self.host_id):
			folders = folders.exclude(uuid=delete_folder.uuid)

		if folders.filter(title=title):
			self._errors['title_unique'] = "The title musst be unique!"

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
			self._errors['text_empty'] = "No empty messages allowed!"

		if len(text) > 320:
			self._errors['text_length'] = "The message exceeds maximum length of 320 characters!"

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