from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from airtable import Airtable
import os
import json
import urllib.request

AT = Airtable('xxxxxxxxxxxxyyyyyyyyyyyy',  # base_id
              'Movies', api_key='xxxxxxxxxxxxxxxx') #apikey

# Create your views here.
def home_page(request):
    user_query = str(request.GET.get('query', ''))
    search_result = AT.get_all(formula="FIND('" + user_query.lower() + "', LOWER({Name}))")
    stuff_for_frontend = {'search_result': search_result}
    return render(request, 'movies/movies_stuff.html', stuff_for_frontend)


def create(request):
    if request.method == 'POST':

        title_search = request.POST.get('name')
        api_url = 'http://www.omdbapi.com/?apikey=68b4a57a&t='
        api_title_search_url = api_url + title_search
        response = urllib.request.urlopen(api_title_search_url)
        result_api = json.loads(response.read())
        #print(result_api['Title'])

        if result_api['Response'] == 'False':
            messages.warning(request, 'no movie avaiable with title : {}'.format(title_search))

        else:
            data = {
            'Pictures': [{'url': request.POST.get('url') or result_api['Poster']}],
            'Rating': int(request.POST.get('rating')),
            'Notes': request.POST.get('notes'),
            'Name': result_api['Title']
        }

            try:
                response = AT.insert(data)
                messages.success(request, 'New movie added: {}'.format(response['fields'].get('Name')))
            except Exception as e:
                messages.warning(request, 'Got an error when trying to create new movie: {}'.format(e))
    return redirect('/')


def edit(request, movie_id):
    if request.method == 'POST':
        data = {
            'Name': request.POST.get('name'),
            'Pictures': [{'url': request.POST.get('url') or 'https://www.classicposters.com/images/nopicture.gif'}],
            'Rating': int(request.POST.get('rating')),
            'Notes': request.POST.get('notes')
        }
        try:
        	response = AT.update(movie_id, data)
        	messages.success(request, 'Updated movie: {}'.format(response['fields'].get('Name')))
        except Exception as e:
            messages.warning(request, 'Got an error when trying to update a movie: {}'.format(e))
    return redirect('/')


def delete(request, movie_id):
    try:
        movie_name = AT.get(movie_id)['fields'].get('Name')
        response = AT.delete(movie_id)
        messages.warning(request, 'Deleted movie: {}'.format(movie_name))
    except Exception as e:
        messages.warning(request, 'Got an error when trying to delete a movie: {}'.format(e))
    return redirect('/')
