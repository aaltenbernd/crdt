from django import forms
from .models import Number

class NumberForm(forms.Form):
	title = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}))

	def clean(self):
		title = self.cleaned_data['title']

		if len(title) == 0:
			self._errors['title_empty'] = "The number needs a title."

		if len(title) > 20:
			self._errors['title_length'] = "The title exceeds maximum length of 20 characters."

		for num in Number.objects.all():
			if num.title == title:
				self._errors['title_unique'] = "The title already exist."

		return title