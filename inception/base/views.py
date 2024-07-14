from django.shortcuts import render, redirect
from .forms import RoomForm
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
	rooms = Room.objects.filter(
		Q(topic__name__icontains = q) |
		Q(name__icontains = q) |
		Q(description__icontains = q)
	)

	room_count = rooms.count()

	context = {'rooms' : rooms, 'topics' : topics, 'room_count' : room_count}
	return render(request, 'base/home.html', context)

def room(request, pk):
	room = Room.objects.get(id=pk)
	room_messages = room.messages_set.all()
	participants = room.participants.all()

	if request.method == 'POST':
		body = request.POST.get('body')
		
		message = Messages.objects.create(
			user=request.user,
			room=room,
			body=body
		)

		room.participants.add(request.user)
		return redirect('room', pk=room.id)
	
	context = {'room' : room, 'room_messages' : room_messages, 'participants' : participants}
	return render(request, 'base/room.html', context)

@login_required(login_url='login')
def create_room(request):
	form = RoomForm()

	if request.method == 'POST':
		form = RoomForm(request.POST)
		if form.is_valid():
			form.save()
		return redirect('home')

	context = {'form' : form}
	return render(request, 'base/room-form.html', context)

@login_required(login_url='login')
def update_room(request, pk):
	room = Room.objects.get(id=pk)
	form = RoomForm(instance=room)

	if request.method == 'POST':
		form = RoomForm(request.POST, instance=room)
		if form.is_valid():
			form.save()
			return redirect('home')

	context={'form' : form}

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
			return redirect('login-register')

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

	message.delete()
	return redirect('home')