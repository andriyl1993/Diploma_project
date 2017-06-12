# -*- coding: utf-8 -*-

from django.shortcuts import render
from models import Prefix, Main, End, Full, NGramm, lev_distance
import re
import random
from datetime import datetime

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
            prefix = ",".join(res.get('prefix')) if isinstance(res.get('prefix'), list) else res.get('prefix')
            end = ",".join(res.get('end')) if isinstance(res.get('end'), list) else res.get('end')
            # word = res.get('word').name if isinstance(res.get('word'), Main) else res.get('word')

            result_str = "Word - " + word \
                         + "\nPrefix - " + prefix + \
                        "\nMain - " + res.get('main') + \
                        "\nEnd - " + end
        else:
            res = cls.find(word)
        return render(request, 'result.html', {'res':True if res.get('main') else False, 'result_str': result_str})

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

def n_gram(request):
    if request.method == 'GET':
        return render(request, 'ngrams.html')
    else:
        text = request.POST.get('text')
        data = re.findall(ur'(?u)\w+', text)
        length = request.POST.get('gram_length')
        use_probs = request.POST.get('use_probs')
        reses = []

        for word in data:
            res = NGramm.first_step(word, int(length), use_probs)
            reses.append(res)

        res_str = "True - " + "\n".join(map(lambda x: ",".join(x[0].values()), reses))
        res_str += 'Error - '
        for res in reses:
            res_str += ",".join(filter(lambda el: isinstance(el, unicode), res[1].values()))
        return render(request, 'result.html', {'res': True, 'result_str': res_str})

from django.db.models.functions import Length
def leven(request):
    if request.method == 'GET':
        return render(request, 'leven.html')
    else:
        text = request.POST.get('text')
        res_str = run_levenshteyn(text)
        return render(request, 'result.html', {'res': True, 'result_str': res_str})

def run_levenshteyn(text):
    data = re.findall(ur'(?u)\w+', text)
    res_str = ""
    result = {}
    for word in data:
        res = []
        ends = End.find(word)
        result['end'] = ends
        _word = word[0:-len(ends)] if len(ends) > 0 else word
        length = len(_word)
        words = Main.objects.annotate(text_len=Length('name')).filter(text_len__in=[length - 1, length + 1]).values(
            'name')
        min = 10
        for w in words:
            dist = lev_distance(_word, w['name'])
            if dist < min:
                min = dist
                res = [w['name']]
            elif dist == min:
                res.append(w['name'])
        res_str += "\n".join(res)
        res_str += '\n'
        result['main'] = res
        result['word'] = text
    return result

import os

def open_and_get_list():
    f = open('uk_wordlist.xml')
    lines = [line.strip() for line in f.readlines()]
    file_count_lines = 70000
    correct = []
    incorrect = []
    for i in range(0, 100):
        a = random.randint(0, file_count_lines)
        words = lines[a].split('\"\">')
        if len(words) > 1:
            word = words[1].strip(' ')
            word = word.split('</w>')[0]
            word = unicode(word.decode('utf-8'))
            correct.append(word)
            random_letter = random.choice(u'йцукенгшщзхїфівапрлджєячсмитьбю')
            rand_i_ch = random.randrange(0, len(word), 2)
            # rand_i_ch = len(word)
            if rand_i_ch != len(word) - 1:
                end = word[rand_i_ch + 1:]
            else:
                end = u''
            if rand_i_ch > 0:
                start = word[:rand_i_ch]
            else:
                start = u''
            incorrect_word = start + random_letter + end
            incorrect.append(incorrect_word)
    return (correct, incorrect)

def run_method(name, word):
    if name == 'my':
       return Full.check_word(word)
    elif name == 'leven':
        return run_levenshteyn(word)
    elif name == 'ngram_without':
        true_grams, error_grams = NGramm.first_step(word, 3, False)
        main = "True:\n"
        main += ",".join(true_grams.values())
        main += "\nError:\n"
        main += ",".join(error_grams.values())
        return {
            'main': main,
            'word': word,
        }
    elif name == 'ngram_with':
        true_grams, error_grams = NGramm.first_step(word, 3, True)
        main = "True:\n"
        main += ",".join(true_grams.values())
        main += "\nError:\n"
        main += ",".join(error_grams.values())
        return {
            'main': main,
            'word': word,
        }

def to_file(name, add_to_file=True):
    correct, incorrect = open_and_get_list()

    results = []
    date_time_1 = datetime.now()
    file_res = u''
    for w in incorrect:
        # try:
            d1 = datetime.now()
            r = run_method(name, w)
            for key, v in r.iteritems():
                if v and isinstance(v, list) and (isinstance(v[0], str) or isinstance(v[0], unicode)):
                    r[key] = ",".join(v)
                elif isinstance(v, Main):
                    r[key] = ",".join(v.name)
            r['word'] = w
            results.append(r)
            w = unicode(w.name) if isinstance(w, Main) else unicode(w)
            file_res += u'Word - ' + w + u', time - ' + unicode(datetime.now() - d1) + u'\n'
            if isinstance(r, dict):
                for k, v in r.iteritems():
                    value = False
                    if v and isinstance(v, list) and (isinstance(v[0], str) or isinstance(v[0], unicode)):
                        value = u",".join(v)
                    elif v and isinstance(v, str) or isinstance(v, unicode):
                        value = unicode(v)
                    if value:
                        file_res += str(k) + ' - ' + value + '\n'
            else:
                file_res += r

            file_res += u'\n\n'

    time_word = datetime.now() - date_time_1
    file_res += "Full - " + str(time_word) + '\n'
    print time_word

    if add_to_file:
        file_res += "\n\nCorrect:\n"
        file_res = "\n".join(correct)

        if isinstance(results[0], dict):
            file_res += u"Summa - " + str(sum(map(lambda res: 1 if res.get('main') else 0, results))) + '\n'
        else:
            file_res += u"Summa - " + str(0)

        result_dir = os.path.join(os.getcwd(), 'results')

        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

        with open(os.path.join(os.getcwd(), 'results', 'result_1' + '.txt'), 'w') as f:
            f.write(file_res.encode('utf-8'))
    return results

def test_script(request):
    results = to_file('my')
    return render(request, 'result_test.html',
                  {
                      'res': True,
                      'results': results
                  })

def test_levenshteyn(request):
    results = to_file('leven')
    return render(request, 'result_test.html',
                  {
                      'res': True,
                      'results': results
                  })

def test_ngram_without(request):
    results = to_file('ngram_without')
    return render(request, 'result_test.html',
                  {
                      'res': True,
                      'results': results
                  })

def test_ngram_with(request):
    results = to_file('ngram_with')
    return render(request, 'result_test.html',
                  {
                      'res': True,
                      'results': results
                  })

def test_all(request):
    counts_my = {}
    counts_lev = {}
    counts_n = {}
    counts_nn = {}

    vars = ['leven', 'my', 'ngram_without', 'ngram_with']
    count_meth = {
        'leven': counts_lev,
        'my': counts_my,
        'ngram_without': counts_n,
        'ngram_with': counts_nn,
    }

    for i in range(10):
        for name in vars:
            results = to_file(name)
            not_empty = filter(lambda x: x['main'], results)
            _count_variants = sum(map(lambda x: len(x['main'].split(',')), not_empty))
            count = len(not_empty)
            count_meth[name][i] = count

    return render(request, 'resultt.html', {'res': 'Calcalated'})