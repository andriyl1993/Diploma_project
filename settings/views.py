from django.shortcuts import render, redirect

from main.models import LittleWord, NGramm, Full, ProbUse, End, Main, Full
from word import split_row
from main.views import code_class
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def index(request):
    return render(request, 'settings_index.html')

@staff_member_required
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

@staff_member_required
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

@staff_member_required
def load_words(request):
    if request.method == "GET":
        return render(request, 'settings_loadwords.html')
    else:
        f = request.POST.get('file')
        res = split_row(f)
        for r in res:
            full_obj = Full()
            full_obj.make_obj(
                '',
                r,
                '',
            )
            ProbUse.compute(full_obj, 3)
            ProbUse.compute(full_obj, 2)
        return render(request, 'result.html', {'res': True, 'result_str': ','.join(res)})

@staff_member_required
def show_words(request):
    if request.method == 'GET':
        part = request.GET.get('part', False)
        method = request.GET.get('method', False)
        limit = request.GET.get('limit', 100)
        start = request.GET.get('start', 0)
        objs = Full.objects
        if method == 'start':
            words = objs.filter(word__startswith=part)
        elif method == 'middle':
            words = objs.filter(word__contains=part)
        elif method == 'end':
            words = objs.filter(word__endswith=part)
        else:
            words = objs.all()
        words = words[int(start):int(start)+int(limit)]
        for word in words:
            print word.main.grams.all()
        return render(request, 'show_words.html', {'words': words})

@staff_member_required
def add_manually(request):
    if request.method == 'GET':
        return render(request, 'manually_add.html')
    elif request.method == "POST":
        type = request.POST.get('type')
        word = request.POST.get('word')
        if type and word:
            cls = code_class[type]()
            cls.make(word)
        return render(request, 'result.html', {'res': word, 'result_str': word})

@staff_member_required
def load_all_words(request):
    f = open('base.lst.txt')
    for line in f:
        word = line.split('/')[0].strip(' ')
        end = End.find(word.decode('utf-8'))
        main = Main()
        end_cut = -len(end)
        word = word.decode('utf-8')[:end_cut] if end_cut < 0 else word.decode('utf-8')
        main.make(word=word)
    return redirect('/settings/show-words/')
