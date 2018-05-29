from django import forms

class PostSearchForm(forms.Form):
    search_word = forms.CharField(label='Search Word')
    #cat_economy = forms.IntegerField(label='Cat_economy')
