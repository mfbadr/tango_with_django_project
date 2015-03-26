from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from rango.models import Category
from rango.models import Page

from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm

@login_required
def add_page(request, category_name_slug):
  try:
    cat = Category.objects.get(slug=category_name_slug)
  except Category.DoesNotExist:
    cat = None

  if request.method == 'POST':
    form = PageForm(request.POST)
    if form.is_valid():
      if cat:
        page = form.save(commit=False)
        page.category = cat
        page.views = 0
        page.save()
        #why is this reverse of category and not rango:category
        #compare to official django tutorial
        return HttpResponseRedirect(reverse('category', args=(category_name_slug,)))
    else:
      print form.errors
  else:
    form = PageForm()

  context_dict = {'form': form, 'category': cat}
  return render(request, 'rango/add_page.html', context_dict)

@login_required
def add_category(request):
  #post?
  if request.method == 'POST':
    form = CategoryForm(request.POST)

    #have we been provided with a valid form?
    if form.is_valid():
      #then save it
      form.save(commit=True)
      #then return to index
      return index(request)
    else: 
      #the supplied form had errors
      print form.errors
  else:
    #not a post
    form = CategoryForm()

  return render(request, 'rango/add_category.html', {'form': form})

def index(request):
  context_dict = {}
  # Query the database for al ist of ALL categeries currently stored
  # order the categoes by no fo likes descending
  # retrieve the top 5, or all if less than 5
  # place the list in our context_dict
  category_list = Category.objects.order_by('-likes')[:5]
  context_dict['categories'] = category_list
  page_list = Page.objects.order_by('-views')[:5]
  context_dict['pages'] = page_list
  print 'request', request
  return render(request, 'rango/index.html', context_dict)

def about(request):
  context_dict = {'boldmessage' : "This is about"}
  return render(request, 'rango/about.html', context_dict)

def category(request, category_name_slug):
  # create a context dict 
  context_dict = {}

  try:
    #can we find a cat name slug that matches?
    category = Category.objects.get(slug=category_name_slug)
    context_dict['category_name'] = category.name

    pages = Page.objects.filter(category=category)
    context_dict['pages'] = pages
    context_dict['category'] = category
    context_dict['category_name_slug'] = category_name_slug
  except Category.DoesNotExist:
    print 'Exception'
    pass

  return render(request, 'rango/category.html', context_dict)

def register(request):
  #bool values for registration
  #changes to true on success

  registered = False

  #if it's a post, process the form data
  if request.method == 'POST':
    #grab info from both forms
    user_form = UserForm(data=request.POST)
    profile_form = UserProfileForm(data=request.POST)

    if user_form.is_valid() and profile_form.is_valid():
      user = user_form.save()
      #hash the password with the set_password method
      #save the user object
      user.set_password(user.password)
      user.save()

      #commit = false delays saving the model 
      profile = profile_form.save(commit=False)
      profile.user = user


      #did the user provide a profile picture?
      #if so get it form input form 

      if 'picture' in request.FILES:
        profile.picture = request.FILES['picture']

      #now save it
      profile.save()

      #and update our variable
      registered = True
    else:
      print user_form.errors, profile_form.errors

  #not an HTTP post, so render using modelform instances
  else:
    user_form = UserForm()
    profile_form = UserProfileForm()

  return render(request, 'rango/register.html', {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):
  #if request is post pull out data
  if request.method == 'POST':
    #get username and passwrod
    username = request.POST.get('username')
    password = request.POST.get('password')

    #user django's machinery to attempt to see if u/p
    #combo is valid, return user object if it is

    user = authenticate(username = username, password = password)

    #if we have a user object, credentials were good
    #otherwise user = None
    if user:
      #is this account active? it could have been disabled
      print user
      if user.is_active:
        login(request, user)
        return HttpResponseRedirect('/rango/')
      else:
        #no logging in with an inactive account
        return HttpResponse('Your rango account is disabled')
    else:
      #bad login details
      print "Invalid login details: {0}, {1}".format(username, password)
      return HttpResponse("Invalid login details supplied.")

  #not a post, so display the login form
  else:
    #no context variables to pass to the template, so blank dictionary
    return render(request, 'rango/login.html', {})

@login_required
def restricted(request):
  return HttpResponse('You are logged in and can see this text!')

@login_required
def user_logout(request):
  logout(request)
  return HttpResponseRedirect('/rango/')

