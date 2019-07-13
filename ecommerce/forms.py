from django import forms

class CartAddForm(forms.Form):
	quantity = forms.IntegerField(initial = 1)
	FormId = forms.IntegerField(widget = forms.HiddenInput(), required = False)

	class Meta:
		fields = ['quantity']

class CheckoutForm(forms.Form):
	Street_Address = forms.CharField(max_length = 10, required = True)
	Suburb = forms.CharField(max_length = 20, required = True)
	City = forms.CharField(max_length = 15, required = True)
	ZipCode = forms.CharField(max_length = 8, required = False)

	class Meta:
		fields = ['Street_Address', 'Suburb', 'City', 'ZipCode']
