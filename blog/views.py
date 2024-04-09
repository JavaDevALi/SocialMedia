from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from blog.models import Post, MyUser, CommentPost, LikePost, FollowUser


def func(post, comments):
    post.comments = comments.filter(post_id=post.id)
    return post


@login_required(login_url='/auth/login/')
def home_view(request):
    posts = map(lambda post: func(post, CommentPost.objects.all()), Post.objects.all())
    d = {
        'posts': posts,
        'user': MyUser.objects.filter(user=request.user).first(),
        'profiles': MyUser.objects.all().exclude(user=request.user),
    }
    if request.method == 'POST':
        data = request.POST
        message = data['message']
        post_id = data['post_id']
        my_user = MyUser.objects.filter(user=request.user).first()
        comment_post = Post.objects.filter(id=post_id).first()
        obj = CommentPost.objects.create(message=message, post_id=post_id, author=my_user)
        obj.save()
        obj = CommentPost.objects.create(author=my_user, post_id=post_id)
        obj.save()
        comment_post.comment_count += 1
        comment_post.save(update_fields=['comment_count'])
        return redirect('/#{}'.format(post_id))
    return render(request, 'index.html', context=d)


def comments_view(request, post_id):
    post = Post.objects.filter(id=post_id).first()
    comments = CommentPost.objects.filter(post=post).all()
    return render(request, 'index.html', context={'post': post, 'comments': comments})


def upload_view(request):
    if request.method == 'POST':
        my_user = MyUser.objects.filter(user=request.user).first()
        post = Post.objects.create(image=request.FILES['image'], author=my_user)
        post.save()
        my_user.post_count += 1
        my_user.save(update_fields=['post_count'])
        return redirect('/')
    return redirect('/')


def delete_post_view(request):
    data = request.GET
    post_id = data.get("post_id")
    user = request.user
    post = Post.objects.filter(id=post_id).first()
    if post.author.user == user:
        post.delete()
        my_user = MyUser.objects.filter(user=request.user).first()
        my_user.post_count -= 1
        my_user.save(update_fields=['post_count'])
        latest_post = Post.objects.last()
        return redirect('/#{}'.format(latest_post.id))
    else:
        return render(request, 'error.html')


def follow_view(request):
    profile_id = request.GET.get('profile_id')
    my_user = MyUser.objects.filter(user=request.user).first()
    profile = MyUser.objects.filter(id=profile_id).first()
    follow_exists = FollowUser.objects.filter(follower=my_user, following_id=profile.id)
    if follow_exists.exists():
        follow_exists.delete()
        profile.follower_count -= 1
        profile.save(update_fields=['follower_count'])
        my_user.following_count -= 1
        my_user.save(update_fields=['following_count'])
    else:
        obj = FollowUser.objects.create(follower=my_user, following_id=profile.id)
        obj.save()
        profile.follower_count += 1
        profile.save(update_fields=['follower_count'])
        my_user.following_count += 1
        my_user.save(update_fields=['following_count'])
    return redirect('/')


def follow_profile_view(request):
    profile_id = request.GET.get('profile_id')
    profile = MyUser.objects.filter(id=profile_id).first()
    my_user = MyUser.objects.filter(user=request.user).first()
    follow_exists = FollowUser.objects.filter(follower=my_user, following_id=profile.id)
    if follow_exists.exists():
        follow_exists.delete()
        profile.follower_count -= 1
        profile.save(update_fields=['follower_count'])
        my_user.following_count -= 1
        my_user.save(update_fields=['following_count'])
    else:
        obj = FollowUser.objects.create(follower=my_user, following_id=profile.id)
        obj.save()
        profile.follower_count += 1
        profile.save(update_fields=['follower_count'])
        my_user.following_count += 1
        my_user.save(update_fields=['following_count'])
    return redirect(f'/profile_info?profile_id={profile_id}')


def like_view(request):
    post_id = request.GET.get('post_id')
    my_user = MyUser.objects.filter(user=request.user).first()
    like_post = Post.objects.filter(id=post_id).first()
    like_exists = LikePost.objects.filter(author=my_user, post_id=post_id)
    if like_exists.exists():
        like_exists.delete()
        like_post.like_count -= 1
        like_post.save(update_fields=['like_count'])
        return redirect('/#{}'.format(post_id))
    else:
        obj = LikePost.objects.create(author=my_user, post_id=post_id)
        obj.save()
        like_post.like_count += 1
        like_post.save(update_fields=['like_count'])
    return redirect('/#{}'.format(post_id))


def setting_view(request):
    return render(request, 'setting.html')


def profile_view(request):
    profile = MyUser.objects.filter(user=request.user).first()
    followers_count = profile.follower_count
    followings_count = profile.following_count
    posts_count = profile.post_count
    profile_pic = profile.profile_pic
    bio = profile.bio
    user_posts = Post.objects.filter(author=profile)
    d = {
        'profile_pic': profile_pic,
        'bio': bio,
        'profile': profile,
        'user': MyUser.objects.filter(user=request.user).first(),
        'followers': followers_count,
        'followings': followings_count,
        'posts': posts_count,
        'user_posts': user_posts,
    }
    return render(request, 'profile.html', context=d)


def profile_info_view(request):
    data = request.GET
    profile_id = data.get("profile_id")
    profile = MyUser.objects.filter(id=profile_id).first()
    followers_count = profile.follower_count
    followings_count = profile.following_count
    posts_count = profile.post_count
    profile_pic = profile.profile_pic
    bio = profile.bio
    user_posts = Post.objects.filter(author=profile)
    d = {
        'profile_pic': profile_pic,
        'bio': bio,
        'profile': profile,
        'user': MyUser.objects.filter(user=request.user).first(),
        'followers': followers_count,
        'followings': followings_count,
        'posts': posts_count,
        'user_posts': user_posts,
    }

    return render(request, 'profile.html', context=d)


def search_view(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        return redirect(f'/search?u={query}')
    query = request.GET.get('u')
    usernames = MyUser.objects.filter(user__username__icontains=query)
    if query is not None and len(query) >= 1:
        posts = Post.objects.all()
        usernames = MyUser.objects.filter(user__username__icontains=query)
        return render(request, 'index.html', {'usernames': usernames, 'posts': posts,
                                              'user': MyUser.objects.filter(user=request.user).first(),
                                              'profiles': MyUser.objects.all().exclude(user=request.user), })

    elif query != usernames:
        return render(request, 'index.html', {'usernames': usernames})


def post_authorinfo_view(request):
    data = request.GET
    profile_id = data.get("author_id")
    profile = MyUser.objects.filter(id=profile_id).first()
    followers_count = profile.follower_count
    followings_count = profile.following_count
    posts_count = profile.post_count
    profile_pic = profile.profile_pic
    bio = profile.bio
    user_posts = Post.objects.filter(author=profile)
    d = {
        'profile_pic': profile_pic,
        'bio': bio,
        'profile': profile,
        'user': MyUser.objects.filter(user=request.user).first(),
        'followers': followers_count,
        'followings': followings_count,
        'posts': posts_count,
        'user_posts': user_posts,
    }
    return render(request, 'profile.html', context=d)
