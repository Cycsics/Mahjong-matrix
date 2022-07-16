from django import forms
from .models import Comment_addiction

class CommentForm_addiction(forms.ModelForm):
    class Meta:
        model = Comment_addiction
        fields = ['body']