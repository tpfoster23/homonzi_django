from django.shortcuts import render
from django.template import loader
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import homonzi.utils as utils

# Create your views here.

def index(request):
    template = loader.get_template('main.html')
    return HttpResponse(template.render())

@csrf_exempt
def runPrompt(request):
    user_prompt = request.POST['prompt']
    message = utils.generate_response(user_prompt)
    voice = utils.get_voice(message)
    # template = loader.get_template('main.html')
    return TemplateResponse(request, 'main.html', {'message':message, 'audioplay':voice})