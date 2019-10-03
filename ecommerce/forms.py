from django import forms

class CartAddForm(forms.Form):
	quantity = forms.IntegerField(initial = 1, widget = forms.NumberInput(attrs = {'style': 'width:60px', 'size': '10'}))
	FormId = forms.IntegerField(widget = forms.HiddenInput(), required = False)
	Size = True


	class Meta:
		fields = ['quantity']

	def clean(self):
		if self.Size == False:
			raise forms.ValidationError("Please pick a size")
		return super().clean()

class CheckoutForm(forms.Form):
	Street_Address = forms.CharField(max_length = 50, required = True)
	Suburb = forms.CharField(max_length = 50, required = True)
	City = forms.CharField(max_length = 50, required = True)
	ZipCode = forms.CharField(max_length = 15, required = False)

	class Meta:
		fields = ['Street_Address', 'Suburb', 'City', 'ZipCode']

