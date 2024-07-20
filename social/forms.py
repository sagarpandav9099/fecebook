from django import forms
from .models import Post, Comment,Group,Message

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']  # fields to be displayed in the form

        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),  # customize widget for content field
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']  # fields to be displayed in the form

        widgets = {
            'content': forms.TextInput(attrs={'placeholder': 'Add a comment...', 'class': 'form-control'}),
        }

class FriendRequestForm(forms.Form):
    friend_username = forms.CharField(max_length=150, help_text='Enter the username of the friend you want to add.')


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description']
        
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),  # customize widget for content field
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter your message here...'}),
        }