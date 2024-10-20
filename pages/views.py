from django.shortcuts import render
from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
import re

# Create your views here.
# def home_page_view(request):
#     return HttpResponse("Hello, World!")
def get_english_words_from_url(url):
    # Send a request to the URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.get_text()
    items = re.findall(r'\b[a-zA-Z0-9]+\b', text)
    english_items = [item.lower() if item.isalpha() else item for item in items]
    return english_items


def get_url_info_view(request):
    result = ""
    if request.method == 'GET' and 'url' in request.GET:
        input_url = request.GET.get('url')
        result = get_english_words_from_url(input_url)

    return render(request, 'pages/index.html', {'result' : result})