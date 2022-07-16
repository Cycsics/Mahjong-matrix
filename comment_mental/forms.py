from django import forms
from .models import Comment_mental

class CommentForm_mental(forms.ModelForm):
    class Meta:
        model = Comment_mental
        fields = ['body']