from django.shortcuts import render, redirect, get_object_or_404
from .models import Post,Friend,Notification
from .forms import PostForm,CommentForm,FriendRequestForm,GroupForm,MessageForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User

@login_required
def home(request):
    posts = Post.objects.all()
    friends = Friend.objects.filter(user=request.user)
    friend_form = FriendRequestForm()
    return render(request, 'social/home.html', {'posts': posts, 'friends': friends, 'friend_form': friend_form})

# Promotion View

@login_required
@require_POST
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user.is_authenticated:
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
    else:
        liked = False
    
    return JsonResponse({'liked': liked, 'count': post.likes.count()})

@login_required
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user 
            comment.save()
            return redirect('home') 
    else:
        form = CommentForm()

    return render(request, 'social/promotion/post_comment.html', {'form': form, 'post': post})

# Profile View
@login_required
def profile_management(request):
    friends = Friend.objects.filter(user=request.user)
    friend_requests = FriendRequest.objects.filter(to_user=request.user)
    all_users = User.objects.exclude(id=request.user.id).exclude(id__in=friends.values_list('friend_id', flat=True))

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)  
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('home')
    else:
        form = PostForm()
    posts = Post.objects.all().order_by('-created_at')
    context = {
        'friends': friends,
        'friend_requests': friend_requests,
        'all_users': all_users,
        'form': form,
        'posts': posts
    }
   
    return render(request, 'social/profile/profile_management.html', context)


# Friend View
from .models import FriendRequest
@login_required
def friend_view(request):
    friend_requests = FriendRequest.objects.filter(to_user=request.user)
    friends = Friend.objects.filter(user=request.user).values_list('friend', flat=True)
    sent_requests = FriendRequest.objects.filter(from_user=request.user).values_list('to_user', flat=True)
    all_users = User.objects.exclude(id__in=friends).exclude(id=request.user.id).exclude(id__in=sent_requests)

    context = {
        'friend_requests': friend_requests,
        'all_users': all_users,
    }

    return render(request, 'social/friend/friend_list.html', context)

@login_required
def send_friend_request(request, user_id):
    to_user = User.objects.get(id=user_id)
    if not FriendRequest.objects.filter(from_user=request.user, to_user=to_user).exists():
        FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    return redirect('friend-view')

@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id)
    if friend_request.to_user == request.user:
        Friend.objects.create(user=friend_request.from_user, friend=friend_request.to_user)
        Friend.objects.create(user=friend_request.to_user, friend=friend_request.from_user)
        friend_request.delete()
    return redirect('friend-view')

# Group View
from .models import Group, Membership
from .forms import GroupForm

@login_required
def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.admin = request.user
            group.save()
            Membership.objects.create(group=group, user=request.user)
            return redirect('group_list')
    else:
        form = GroupForm()
    return render(request, 'social/group/create_group.html', {'form': form})

@login_required
def group_list(request):
    groups = Group.objects.all()
    return render(request, 'social/group/group_list.html', {'groups': groups})


@login_required
def join_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.method == 'POST':
        Membership.objects.get_or_create(group=group, user=request.user)
        return redirect('group_chat', group_id=group.id)
    return redirect('group_list')

@login_required
def leave_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.method == 'POST':
        membership = get_object_or_404(Membership, group=group, user=request.user)
        membership.delete()
    return redirect('group_list')

@login_required
def group_chat(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if not Membership.objects.filter(group=group, user=request.user).exists():
        return redirect('group_list')
    
    messages = group.messages.all().order_by('timestamp')
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.group = group
            message.user = request.user
            message.save()
            return redirect('group_chat', group_id=group.id)
    else:
        form = MessageForm()
    
    return render(request, 'social/group/group_chat.html', {'group': group, 'messages': messages, 'form': form})

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if Membership.objects.filter(group=group, user=request.user).exists():
        return redirect('group_chat', group_id=group.id)
    return redirect('group_list')

# Notification Views
@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')
    return render(request, 'social/notification/notification_list.html', {'notifications': notifications})

@login_required
def mark_as_read(request, notification_id):
    notification = Notification.objects.get(id=notification_id, recipient=request.user)
    notification.read = True
    notification.save()
    return redirect('notification_list')

from django.http import JsonResponse
from django.template.loader import render_to_string

@login_required
def fetch_notifications(request):
    notifications = request.user.received_notifications.all()
    unread_count = notifications.filter(read=False).count()
    html = render_to_string('notification/notifications.html', {'notifications': notifications})
    return JsonResponse({'unread_count': unread_count, 'html': html})