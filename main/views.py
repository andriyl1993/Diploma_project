from django.shortcuts import render
from models import Prefix, Main, End, Full, Errors
from models import is_one_by_one
import re

code_class = {
    'pref': Prefix,
    'main': Main,
    'end': End,
    'full': Full,
}

# Create your views here.
def index(request):
    return render(request, 'index.html')

def check_word(request):
    if request.method == "GET":
        return render(request, 'check_word.html')
    else:
        cls = code_class[request.POST.get('elem')]
        word = request.POST.get('word')
        if cls is Full:
            res = cls.check_word(word)
            result_str = "Word (correct) - " + res.get('prefix') + res.get('main') + res.get('end')
        else:
            res = cls.find(word)
        return render(request, 'result.html', {'res':True, 'result_str': result_str})

def check_text(request):
    if request.method == "GET":
        return render(request, 'check_text.html')
    else:
        text = request.POST.get('text')
        data = re.findall(ur'(?u)\w+', text)
        result = []

        for w in data:
            res = Full.check_word(w)
            result.append(res.get('prefix') + res.get('main') + res.get('end'))

        result_str = " ".join(result)
        return render(request, 'result.html', {'res': True, 'result_str': result_str})
