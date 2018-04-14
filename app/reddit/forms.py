from django import forms


class RedditUserForm(forms.Form):
    username = forms.CharField(
        max_length=32,
        widget=forms.TextInput(
            attrs={
                'class':'form-control',
                'placeholder':'Add a reddit username'
            }
        )
    )
