from django import forms
from rango.models import Page, Category

class CategoryForm(forms.ModelForm):
  name = forms.CharField(max_length=128, help_text='Please enter the category name')
  views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
  likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
  slug = forms.CharField(widget=forms.HiddenInput(), required=False)

  #an inline class to provide additional information on the form.
  class Meta:
    #link to a model
    model = Category
    fields = ('name',)

class PageForm(forms.ModelForm):
  title = forms.CharField(max_length=128, help_text='Please enter title of the page')
  url = forms.URLField(max_length=200, help_text="Please enter the URL of the page")
  views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

  #an inline class to provide additional information on the form.
  def clean(self):
    cleaned_data = self.cleaned_data
    url = cleaned_data.get('url')

    #if url is not empty and doesn't start with 'http://, prepend
    if url and not url.startswith('http://'):
      print 'clean()'
      url = 'http://' + url
      cleaned_data['url'] = url

    return cleaned_data
  class Meta:
    model = Page
    exclude = ('category',)
