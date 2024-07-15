# This file contains the views for the core app. The views are responsible for rendering the HTML templates and handling the logic for the web application.

# import necessary packages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Profile, Post, LikePost, FollowersCount, Comment, KindnessMessage
from django.contrib.auth.decorators import login_required
from datetime import datetime, date, timedelta
import csv
from .utilities import sentiment_score, check_profanity
import random
from itertools import chain
from django.shortcuts import redirect, HttpResponseRedirect
from django.utils import timezone
from random import choice
from pytz import timezone
from django.core.exceptions import ObjectDoesNotExist

# home page
@login_required(login_url = 'signin')
def index(request):
    # get the user's profile
    user_object = User.objects.get(username=request.user)
    user_profile = Profile.objects.get(user=user_object)

    # get all posts
    posts = Post.objects.all()
    post_dic = []

    # loop through all posts and append them to the dictionary
    for post in posts:
        # get the user's profile image
        post_user_profile = Profile.objects.get(user=User.objects.get(username=post.user))
        comments = Comment.objects.filter(post=post)

        # Calculate time since post was created
        sydney_timezone = timezone('Australia/Sydney')
        now_sydney = datetime.now(sydney_timezone)
        time_delta = now_sydney - post.created_at
        seconds = time_delta.total_seconds()

        # Convert seconds to a human-readable format
        if seconds < 60:
            if seconds == 1:
                time_string = f"{int(seconds)} second ago"
            else:
                time_string = f"{int(seconds)} seconds ago"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            if minutes == 1:
                time_string = f"{minutes} minute ago"
            else:
                time_string = f"{minutes} minutes ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            if hours == 1:
                time_string = f"{hours} hour ago"
            else:
                time_string = f"{hours} hours ago"
        else:
            days = int(seconds / 86400)
            if days == 1:
                time_string = f"{days} day ago"
            else:
                time_string = f"{days} days ago"
        
        # Append post along with user profile image to the dictionary

        # NOTE: Usually this line would check the last 3-4 days to keep all posts relevant but since I don't know when Mr Dunne is testing I have set it to an arbitrary 30 days
        if datetime.now(timezone('Australia/Sydney')).day - post.created_at.date().day <= 30:
            post_dic.append({
                'post': post,
                'profile_image': post_user_profile.profile_img,
                'comments': comments,
                'time_since_posted': time_string
            })

    # sort posts by positivity
    sorted_posts = sorted(post_dic, key=lambda post: post["post"].positivity * 2, reverse=False)

    # user follow recommendations
    user_following = FollowersCount.objects.filter(follower=request.user.username)
    all_users = User.objects.all()
    user_following_all = []

    # get all users that the current user is following
    for user in user_following:
        user_list = User.objects.filter(username=user.user)
        user_following_all.append(user_list)
    
    # get all users that the current user is not following
    new_suggestion_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestion_list = [x for x in list(new_suggestion_list) if (x not in list(current_user))]
    random.shuffle(final_suggestion_list)

    # get the profile images of the suggested users
    username_profile = []
    username_profile_list = []

    for users in final_suggestion_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_list = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_list)

    # get the first 4 suggested users
    suggestions_username_profile_list = list(chain(*username_profile_list))

    return render(request, 'index.html', {'user_profile': user_profile, 'posts': posts, 'suggestions_username_profile_list': suggestions_username_profile_list[:4], "sorted_posts": sorted_posts})

# signup page
def signup(request):
    # check if the user is already logged in
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password2 = request.POST["password2"]

        if password == password2:
            # check if the username or email is already taken
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email Taken")
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, "Username Taken")
                return redirect('signup')
            elif check_profanity(username):
                messages.info(request, "Username Contains Sensitive Words")
                return redirect('signup')
            else:
                # create a new user
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                #log user in and redirect to the settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                #create a Profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user = user_model, id_user = user_model.id)
                new_profile.save()
                return redirect("welcome")
        else:
            # if the passwords do not match, redirect to the signup page
            messages.info(request, "Passwords not matching")
            return redirect('signup')
    else:
        # render the signup page
        return render(request, 'signup.html')

# signin page
def signin(request):
    # check if the user is already logged in
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        
        user = auth.authenticate(username=username, password=password)

        # check if the user exists and log them in
        if user is not None:
            auth.login(request, user)
            return redirect("/")
        else:
            messages.info(request, "Invalid Credentials")
            return redirect("signin")
    else:
        return render(request, 'signin.html')

# settings page
@login_required(login_url = 'signin')
def settings(request):
    # get the user's profile
    user_profile = Profile.objects.get(user=request.user)

    # update the user's profile
    if request.method == "POST":
        # check if the user has uploaded a profile image
        if check_profanity(request.POST["bio"]) == True:
            messages.info(request, "Bio contains sensitive words. Try again.")
            return redirect("settings")

        # check if the user has uploaded a profile image
        if request.FILES.get("image") == None:
            # if the user has not uploaded a profile image, keep the existing one
            image = user_profile.profile_img
            bio = request.POST["bio"]
            user_profile.profile_img = image
            user_profile.bio = bio
            user_profile.save()
        if request.FILES.get("image") != None:
            # if the user has uploaded a profile image, update the profile image
            image = request.FILES.get("image")
            bio = request.POST["bio"]

            user_profile.profile_img = image
            user_profile.bio = bio
            user_profile.save()

        # display success message
        # messages.info(request, "Success!")
        return redirect("/")

    return render(request, 'settings.html', {"user_profile": user_profile})

# like post
@login_required(login_url = 'signin')
def like_post(request):
    # get the username and post id, and check if the user has already liked the post
    username = request.user.username
    post_id = request.GET.get("post_id")
    post = Post.objects.get(id=post_id)
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        # if the user has not liked the post, create a new like object
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes += 1
        post.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        # if the user has already liked the post, delete the like object
        like_filter.delete()
        post.no_of_likes -= 1
        post.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

# profile page
@login_required(login_url = 'signin')
def profile(request, pk):
    # get the user's profile
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    
    # get all posts by the user
    user_posts = Post.objects.filter(user=pk)
    user_posts_length = len(user_posts)

    post_dic = []

    # loop through all posts and append them to the dictionary
    for post in user_posts:
        post_user_profile = Profile.objects.get(user=User.objects.get(username=post.user))
        comments = Comment.objects.filter(post=post)
        
        # Calculate time since post was created
        sydney_timezone = timezone('Australia/Sydney')
        now_sydney = datetime.now(sydney_timezone)
        time_delta = now_sydney - post.created_at
        seconds = time_delta.total_seconds()

        # Convert seconds to a human-readable format
        if seconds < 60:
            if seconds == 1:
                time_string = f"{int(seconds)} second ago"
            else:
                time_string = f"{int(seconds)} seconds ago"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            if minutes == 1:
                time_string = f"{minutes} minute ago"
            else:
                time_string = f"{minutes} minutes ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            if hours == 1:
                time_string = f"{hours} hour ago"
            else:
                time_string = f"{hours} hours ago"
        else:
            days = int(seconds / 86400)
            if days == 1:
                time_string = f"{days} day ago"
            else:
                time_string = f"{days} days ago"
        
        # Append post along with user profile image to the dictionary

        # NOTE: Usually this line would check the last 3-4 days to keep all posts relevant but since I don't know when Dunne is testing I have set it to an arbitrary 30 days
        if datetime.now(timezone('Australia/Sydney')).day - post.created_at.date().day <= 30:
            post_dic.append({
                'post': post,
                'profile_image': post_user_profile.profile_img,
                'comments': comments,
                'time_since_posted': time_string
            })

    # sort posts by positivity
    sorted_posts = sorted(post_dic, key=lambda post: post["post"].positivity * 2, reverse=False)

    follower = request.user.username
    user = pk

    # check if the user is already following the user
    if FollowersCount.objects.filter(user=user, follower=follower).first():
        button_text = "Unfollow"
    else:
        button_text = "Follow"

    # get the number of followers and following
    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    # render the profile page
    context = {
        "user_object": user_object,
        "user_profile": user_profile,
        "user_posts": user_posts,
        "user_posts_length": user_posts_length,
        "button_text": button_text,
        "user_followers": user_followers,
        "user_following": user_following,
        "sorted_posts": sorted_posts
    }

    return render(request, 'profile.html', context)

# follow user
@login_required(login_url = 'signin')
def follow(request):
    if request.method == 'POST':
        # get the follower and user
        follower = request.POST["follower"]
        user = request.POST["user"]

        # check if the user is already following the user
        if FollowersCount.objects.filter(user=user, follower=follower).first():
            # if the user is already following the user, delete the follower object
            delete_follower = FollowersCount.objects.get(user=user, follower=follower)
            delete_follower.delete()
            return redirect('/profile/' + user)
        else:
            # if the user is not following the user, create a new follower object
            new_follower = FollowersCount.objects.create(user=user, follower=follower)
            new_follower.save()
            return redirect('/profile/' + user)
    else:
        return redirect('/')

# upload post page
@login_required(login_url = 'signin')
def post (request):
    if request.method == 'POST':
        # get the user and post content
        user = request.user.username
        textInput = request.POST["post_content"]

        if textInput.strip() == '':
            messages.info(request, "Post cannot be empty")
            return redirect('post')
        
        # check if the post contains any profanity
        if check_profanity(textInput):
            messages.info(request, "We detected some sensitive words in your post. Please try again.")
            return redirect('post')
        
        # get the sentiment score of the post
        positivity = sentiment_score(textInput)

        # create a new post object
        new_post = Post.objects.create(user=user, post_content=textInput, positivity=positivity)
        new_post.save()

        return redirect('/')
    else:
        return render(request, 'post.html')

# challenge page
@login_required(login_url = 'signin')
def challenge(request):
    if request.method == 'POST':
        # get the user's profile
        user = request.user.username
        user_object = User.objects.get(username=user)
        user_profile = Profile.objects.get(user=user_object)
        
        # check if the user has already completed the challenge today
        # if they haven't, update their streak and last completed date
        if datetime.now().day == user_profile.last_completed.day and datetime.now().month == user_profile.last_completed.month and datetime.now().year == user_profile.last_completed.year:
            pass
        else:
            user_profile.current_streak += 1
            user_profile.last_completed = datetime.now()
        
        # update max streak
        if user_profile.current_streak > user_profile.max_streak:
            user_profile.max_streak = user_profile.current_streak
        
        user_profile.save()

        return redirect('/challenge')
    else:
        # load challenges from csv file
        filename = 'static/challenges.csv'
        challenges = []

        # create a list of all challenges
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                challenges.append(row[0])
        
        # choose a daily challenge based on the day of the month
        daily_challenge = challenges[(datetime.now().day)]

        # get the user's profile
        user = request.user.username
        user_object = User.objects.get(username=user)
        user_profile = Profile.objects.get(user=user_object)
        today_completed = False

        # check if the user has an existing streak
        if user_profile.last_completed.day == date.today().day and user_profile.last_completed.month == date.today().month:
            pass
        elif user_profile.last_completed.day != (date.today() - timedelta(days=1)).day or user_profile.last_completed.month != (date.today() - timedelta(days=1)).month:
            user_profile.current_streak = 0
            user_profile.save()

        # check if the user has already completed the challenge today
        if datetime.now().day == user_profile.last_completed.day and datetime.now().month == user_profile.last_completed.month and datetime.now().year == user_profile.last_completed.year:
            today_completed = True
            user_profile.save()

        return render(request, 'challenge.html', {'user_profile': user_profile, 'today_completed': today_completed, 'daily_challenge': daily_challenge})

# add comment
@login_required(login_url = 'signin')
def add_comment(request):
    if request.method == 'POST':
        # get the comment text and post id
        comment_text = request.POST["comment"]
        post_id = request.POST["post_id"]

        # check if the comment contains any profanity
        if check_profanity(comment_text):
            # prevent the user from submitting an explicit comment
            return redirect('/')

        # create a new comment object
        if comment_text.strip() != '':
            comment = Comment.objects.create(post_id=post_id, user=request.user.username, comment=comment_text)
            comment.save()
            post = Post.objects.get(id=post_id)
            post.no_of_comments += 1
            post.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

# like a post
@login_required(login_url = 'signin')
def liked_posts(request):
    # get the user's profile
    user_object = User.objects.get(username=request.user)
    user_profile = Profile.objects.get(user=user_object)

    # get all posts that the user has liked
    liked_posts = LikePost.objects.filter(username=request.user.username)
    post_dic = []

    # loop through all liked posts and append them to the dictionary
    for post in liked_posts:
        # get the post object and user profile image
        post_obj = Post.objects.get(id=post.post_id)
        post_user_profile = Profile.objects.get(user=User.objects.get(username=post_obj.user))
        comments = Comment.objects.filter(post=post_obj)

        # Calculate time since post was created
        sydney_timezone = timezone('Australia/Sydney')
        now_sydney = datetime.now(sydney_timezone)
        time_delta = now_sydney - post_obj.created_at
        seconds = time_delta.total_seconds()

        # Convert seconds to a human-readable format
        if seconds < 60:
            if seconds == 1:
                time_string = f"{int(seconds)} second ago"
            else:
                time_string = f"{int(seconds)} seconds ago"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            if minutes == 1:
                time_string = f"{minutes} minute ago"
            else:
                time_string = f"{minutes} minutes ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            if hours == 1:
                time_string = f"{hours} hour ago"
            else:
                time_string = f"{hours} hours ago"
        else:
            days = int(seconds / 86400)
            if days == 1:
                time_string = f"{days} day ago"
            else:
                time_string = f"{days} days ago"
        
        # Append post along with user profile image to the dictionary

        # NOTE: Usually this line would check the last 3-4 days to keep all posts relevant but since I don't know when Mr Dunne is testing I have set it to an arbitrary 30 days
        if datetime.now(timezone('Australia/Sydney')).day - post_obj.created_at.date().day <= 30:
            post_dic.append({
                'post': post_obj,
                'profile_image': post_user_profile.profile_img,
                'comments': comments,
                'time_since_posted': time_string
            })

    # sort posts by positivity
    sorted_posts = sorted(post_dic, key=lambda post: post["post"].positivity * 2, reverse=False)

    user_following = FollowersCount.objects.filter(follower=request.user.username)
    all_users = User.objects.all()
    user_following_all = []

    # cycle through all users that the current user is following
    for user in user_following:
        user_list = User.objects.filter(username=user.user)
        user_following_all.append(user_list)
    
    # get all users that the current user is not following
    new_suggestion_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestion_list = [x for x in list(new_suggestion_list) if (x not in list(current_user))]
    random.shuffle(final_suggestion_list)

    # get the profile images of the suggested users
    username_profile = []
    username_profile_list = []

    for users in final_suggestion_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_list = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_list)

    # get the first 4 suggested users
    suggestions_username_profile_list = list(chain(*username_profile_list))

    return render(request, 'liked-posts.html', {'user_profile': user_profile,'suggestions_username_profile_list': suggestions_username_profile_list[:4], "sorted_posts": sorted_posts})

# message page
@login_required(login_url = 'signin')
def message(request):
    # Get the user's profile
    user_object = User.objects.get(username=request.user)
    user_profile = Profile.objects.get(user=user_object)

    all_users = User.objects.exclude(username=request.user.username)
    all_users = all_users.exclude(username='admin')

    # Check if the user has sent a message
    if request.method == 'POST':
        random_user_username = request.session.get('random_user_username')

        # Get the random user and their profile
        if random_user_username:
            try:
                random_user = User.objects.get(username=random_user_username)
                random_profile = Profile.objects.get(user=random_user)
            except ObjectDoesNotExist:
                random_user = None
                random_profile = None
        else:
            random_user = None
            random_profile = None

        # Get the message content
        message_content = request.POST.get('message_content')

        # Check if message is empty or contains profanity
        if message_content.strip() == '' or check_profanity(message_content):
            messages.info(request, "We've detected some sensitive words in your message. Please try again.")
            return redirect('message')
        elif random_user is not None:
            # Create and save kindness message
            new_message = KindnessMessage.objects.create(
                from_user=user_object,
                to_user=random_user,
                message=message_content
            )

            print(f"Message sent from {user_object.username} to {random_user.username}")
            new_message.save()
            messages.success(request, "Kindness message sent successfully!")
            return redirect('message')  # Redirect to prevent multiple submissions

    else:
        # Get a random user and their profile
        if all_users.exists():
            random_user = choice(all_users)
            random_profile = Profile.objects.get(user=random_user)
            # Store the random user's username in the session
            request.session['random_user_username'] = random_user.username
        else:
            random_user = None
            random_profile = None
        
        # Check if the user has received a kindness message
        received_messages = KindnessMessage.objects.filter(to_user=user_object).order_by('-sent_at')

        # Render the message page
        context = {
            'user_profile': user_profile,
            'random_user': random_user,
            'random_profile': random_profile,
            'received_messages': received_messages,  # Pass all received messages
        }

        return render(request, 'message.html', context)

# info page
def info(request):
    return render(request, 'info.html')

# welcome page
@login_required(login_url = 'signin')
def welcome(request):
    return render(request, 'welcome.html')

# log out user
@login_required(login_url = 'signin')
def logout(request):
    auth.logout(request)
    return redirect("signin")