from django import forms

class CartAddForm(forms.Form):
	quantity = forms.IntegerField(initial = 1)
	FormId = forms.IntegerField(widget = forms.HiddenInput())

	class Meta:
		fields = ['quantity']
