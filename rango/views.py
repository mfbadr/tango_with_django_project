from django.shortcuts import render
from django.http import HttpResponse


from rango.models import Category
from rango.models import Page

def index(request):
  # Query the database for al ist of ALL categeries currently stored
  # order the categoes by no fo likes descending
  # retrieve the top 5, or all if less than 5
  # place the list in our context_dict
  category_list = Category.objects.order_by('-likes')[:5]
  print category_list
  context_dict = {'categories' : category_list}
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
  except Category.DoesNotExist:
    print 'Exception'
    pass

  return render(request, 'rango/category.html', context_dict)
