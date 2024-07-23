from django.shortcuts import render, redirect
from .forms import RoomForm, UserForm
from .models import Room, Topic, Messages
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required

# Create your views here.

def home(request):
	q = request.GET.get('q') if request.GET.get('q') != None else ''
	
	topics = Topic.objects.all()
	room_messages = Messages.objects.filter(Q(room__topic__name__icontains=q))

	rooms = Room.objects.filter(
		Q(topic__name__icontains = q) |
		Q(name__icontains = q) |
		Q(description__icontains = q)
	)

	room_count = rooms.count()

	context = {'rooms' : rooms, 'topics' : topics, 'room_count' : room_count, 'room_messages': room_messages}
	return render(request, 'base/home.html', context)

def room(request, pk):
	room = Room.objects.get(id=pk)
	room_messages = room.messages_set.all()
	participants = room.participants.all()

	if request.method == 'POST':
		body = request.POST.get('body')
		
		message = Messages.objects.create (
			user=request.user,
			room=room,
			body=body
		)

		room.participants.add(request.user)
		return redirect('room', pk=room.id)
	
	context = {'room' : room, 'room_messages' : room_messages, 'participants' : participants}
	return render(request, 'base/room.html', context)

def user_profile(request, pk):
	user = User.objects.get(id=pk)
	room_messages = user.messages_set.all()
	topics = Topic.objects.all()
	rooms = user.room_set.all()
	room_count = rooms.count()

	context = {'room_messages' : room_messages, 'topics' : topics, 'rooms' : rooms, 'room_count' : room_count, 'user' : user}

	return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def create_room(request):
	form = RoomForm()
	topics = Topic.objects.all()

	if request.method == 'POST':
		form = RoomForm(request.POST)
		topic_name = request.POST.get('topic')
		topic, created = Topic.objects.get_or_create(name=topic_name)

		room = Room.objects.create(
			host=request.user,
			topic=topic,
			description=request.POST.get('description'),
			name=request.POST.get('name')
		)
		room.participants.add(request.user)
		return redirect('home')

	context = {'form' : form, 'topics' : topics}
	return render(request, 'base/room-form.html', context)

@login_required(login_url='login')
def update_room(request, pk):
	topics = Topic.objects.all()
	room = Room.objects.get(id=pk)
	form = RoomForm(instance=room)


	if request.method == 'POST':
		topic_name = request.POST.get('topic')
		topic, created = Topic.objects.get_or_create(name=topic_name)		
		room.name = request.POST.get('name')
		room.description = request.POST.get('description')
		room.topic = topic
		room.save()
		return redirect('home')
	context={'form' : form, 'topics' : topics, 'room' : room}

	return render(request, 'base/room-form.html', context)

@login_required(login_url='login')
def delete_room(request, pk):
	room = Room.objects.get(id=pk)

	if request.method == 'POST':
		room.delete()
		return redirect('home')

	context = {'room' : room}

	return render(request, 'base/delete-room.html', context)

def login_page(request):
	if request.user.is_authenticated:
		return redirect('home')

	page = 'login'

	if request.method == 'POST':
		username = request.POST.get('username').lower()
		password = request.POST.get('password')

		try:
			user = User.objects.get(username=username)
		except:
			messages.error(request, "Username does not exist.")
			return redirect('login')

		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request, user)
			return redirect('home')
		else:
			messages.error(request, 'Incorrect Password Specified')

	context = {'page' : page}
	return render(request, 'base/login-register.html', context)

def logout_user(request):
	logout(request)
	return redirect('home')

def register_page(request):
	if request.user.is_authenticated:
		return redirect('home')
	
	form = UserCreationForm()

	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			user.username = user.username.lower()
			user.save()
			login(request, user)
			return redirect('home')
	context = {'form' : form}

	return render(request, 'base/login-register.html', context)

def delete_message(request, pk):
	message = Messages.objects.get(id=pk)
	room_id = message.room.id
	message.delete()
	return redirect('room', pk=room_id)

@login_required(login_url='login')
def update_user(request):
	user = request.user
	form = UserForm(instance=user)

	if request.method == 'POST':
		form = UserForm(request.POST, instance=user)	
		if form.is_valid():
			form.save()
			return redirect('user-profile', pk=user.id)
		
	context = {'form' : form}
	return render(request, 'base/update-user.html', context)