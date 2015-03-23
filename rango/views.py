from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse


from rango.models import Category
from rango.models import Page

from rango.forms import CategoryForm, PageForm

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
  print category_list
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


