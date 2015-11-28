from django import forms

class NumberForm(forms.Form):
	title = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}))

	def clean(self):
		title = self.cleaned_data['title']

		if len(title) == 0:
			self._errors['text_empty'] = "The number needs a title."

		if len(title) > 20:
			self._errors['text_length'] = "The title exceeds maximum length of 20 characters."

		return title