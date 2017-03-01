from django.shortcuts import render

from main.models import LittleWord, NGramm, Full, ProbUse
from word import split_row
from main.views import code_class


def index(request):
    return render(request, 'settings_index.html')

def load_prefixes(request):
    if request.method == "GET":
        return render(request, 'settings_prefixes_load.html')
    else:
        f = request.POST.get('file')
        res = split_row(f)
        for r in res:
            cls = code_class[request.POST.get('part')]
            if not cls.objects.filter(name=r):
                obj = cls(name=r)
                obj.save()
        return render(request, 'result.html', {'res': True, 'result_str': ','.join(res)})

def load_littleword(request):
    if request.method == "GET":
        return render(request, 'settings_littleword.html')
    else:
        f = request.POST.get('file')
        res = split_row(f)
        for r in res:
            if not LittleWord.objects.filter(name=r):
                obj = LittleWord(name=r, type=request.POST.get('type'))
                obj.save()
        return render(request, 'result.html', {'res': True, 'result_str': ','.join(res)})

def load_words(request):
    if request.method == "GET":
        return render(request, 'settings_loadwords.html')
    else:
        f = request.POST.get('file')
        res = split_row(f)
        for r in res:
            NGramm.add_new(r, 3)
            NGramm.add_new(r, 2)
            word_res = Full.check_word(r, False, False)
            full_obj = Full()
            full_obj.make_obj(
                word_res.get('prefix'),
                word_res.get('main'),
                word_res.get('end')
            )
            ProbUse.compute(full_obj)
        return render(request, 'result.html', {'res': True, 'result_str': ','.join(res)})