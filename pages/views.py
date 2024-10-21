from django.shortcuts import render
from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
import re
from .services import predict_entities

# Create your views here.
# def home_page_view(request):
#     return HttpResponse("Hello, World!")

def get_english_words_from_url(url):
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
        words = get_english_words_from_url(input_url)
        text_from_url = ' '.join(words)
        result = predict_entities(text_from_url)
    return render(request, 'pages/index.html', {'entities' : set(result)})