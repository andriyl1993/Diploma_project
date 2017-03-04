from django.shortcuts import render
from models import Prefix, Main, End, Full

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
            res = cls.check_word(word, True, True, True)
            error_str = ", ".join(res.get('error').values())
            true_str = ", ".join(res.get('true').values())
            res = "Find error - " + error_str + " " if error_str else " "
            res += "Correct - " + true_str + " " if true_str else " "
        else:
            res = cls.find(word)
        return render(request, 'result.html', {'res':True, 'result_str': res})