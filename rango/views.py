from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from rango.models import Category
from rango.models import Page

from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm

from datetime import datetime

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
  category_list = Category.objects.order_by('-likes')[:5]
  page_list = Page.objects.order_by('-views')[:5]
  context_dict = {'categories' : category_list, 'pages' : page_list }

  # Get the number of visits to the site
  # use COOKIES.get() to obtain the visits cooke
  # if cookie exists, returned value is casted to an int
  # if it doesn't exist, it defaults to 0
  visits = request.session.get('visits')
  if not visits:
    visits = 1

  reset_last_visit_time = False

  last_visit = request.session.get('last_visit')

  #does the cookie last_vist exist?
  if last_visit:
    print 'foo'
    last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

    #if its been more than a day since the last visit...
    if (datetime.now() - last_visit_time).seconds > 5:
      visits = visits + 1
      # and flag that the cookie last visit needs to be updated
      reset_last_visit_time = True
  else:
    #last_visit doesn't exist, so flag that it should be set
    reset_last_visit_time = True
    context_dict['visits'] = visits

  if reset_last_visit_time:
    request.session['last_visit'] = str(datetime.now())
    request.session['visits'] = visits

  context_dict['visits'] = visits
  response = render(request, 'rango/index.html', context_dict)

  return response



def about(request):
  if request.session.get('visits'):
    count = request.session.get('visits')
  else:
    count = 0
  context_dict = {'boldmessage' : "This is about", 'visits': count}
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


@login_required
def restricted(request):
  return render(request, 'rango/restricted.html', {'boldmessage': 'You can see this because you are logged in!'})

