# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from levenshteyn import lev_distance

pref_max_len = 5
end_max_len = 3
gram_lengths = [3,2]


class Prefix(models.Model):
    """
    Клас для префікса слова
    """
    name = models.CharField(max_length=7)

    def __unicode__(self):
        return unicode(self.name)

    @staticmethod
    def find(string, not_use=[]):
        """Пошук префікса у слові"""
        if not isinstance(string, unicode):
            string = unicode(string.decode('utf-8'))

        prefs = Prefix.objects.\
            filter(name__istartswith=string[0]).\
            exclude(name__in=not_use).\
            extra(select={'length':'Length(name)'}).\
            order_by('-length').\
            values('name')
        prefix = string[0]
        if prefs:
            for i in range(1, pref_max_len):
                if filter(lambda elem: prefix + string[i] in elem.get('name', ''), prefs):
                    prefix += string[i]
                    if filter(lambda elem: prefix == elem.get('name', ''), prefs):
                        return prefix
                elif filter(lambda elem: prefix == elem.get('name', ''), prefs):
                    return prefix
                else:
                    return ""
        elif len(prefix) == 1 and not prefs:
            prefix = ''
        return prefix

    @staticmethod
    def find_all(word, not_use=[]):
        """Пошук всіх можливих варіантів префіксів у слові"""
        prefixes = []
        while (True):
            _find_pref = Prefix.find(word, prefixes)
            if _find_pref:
                prefixes.append(_find_pref)
            else:
                break
        return prefixes

    def make(self, word):
        if Prefix.objects.filter(name=word):
            return False
        obj = Prefix(
            name=word
        )
        obj.save()
        return obj

class End(models.Model):
    """
    Клас для закінчення слова
    """
    name = models.CharField(max_length=7)

    def __unicode__(self):
        return unicode(self.name)

    @staticmethod
    def find(string, not_use=[]):
        """Пошук закінчення у слові"""
        end = ""

        if not isinstance(string, unicode):
            string = unicode(string.decode('utf-8'))

        _end = string[-1]
        for i in range(end_max_len+1):
            if i == 0:
                ends = End.objects.filter(name__iendswith=_end).exclude(name__in=not_use)
            else:
                ends = filter(lambda x: x.name[len(x.name) - i - 1:len(x.name)] == _end , ends)

            finish = False
            if ends:
                end = filter(lambda x: x.name == _end,ends)
            else:
                finish = True
            if not finish:
                if end:
                    return end[0].name

                try:
                    if len(string) > 2:
                        _end = string[-(i + 2)] + _end
                except Exception, e:
                    print str(e)
            else:
                try:
                    return end[0].name
                except Exception:
                    return ""

    @staticmethod
    def find_all(word):
        """Пошук всіх можливих закінчень у слові"""
        ends = []
        while True:
            _end = End.find(word, ends)
            if _end:
                ends.append(_end)
            else:
                break
        return ends

    def make(self, word):
        if End.objects.filter(name=word):
            return False
        end = End(
            name=word
        )
        end.save()
        return end

class NGramm(models.Model):
    """
    Клас для грамів
    """
    name = models.CharField(max_length=3)

    @staticmethod
    def get_grams(word, gram_len=3):
        """Поділити слово на грами"""
        if not isinstance(word, unicode):
            word = word.decode('utf-8')
        word = word.strip().strip('﻿')
        return map(lambda i: word[i:i + gram_len], range(len(word)-gram_len+1))

    @staticmethod
    def add_new(word, gram_length=3):
        """Додати до бази даних нові грами із слова"""
        res = []
        for x in NGramm.get_grams(word, gram_length):
            obj = NGramm.objects.filter(name=x)
            if not obj:
                obj = NGramm()
                obj.name = x
                obj.save()
            else:
                obj = obj[0]
            res.append(obj.id)
        return NGramm.objects.filter(id__in = res)

    @staticmethod
    def check_compatibility(arr):
        res = []
        for i, val in enumerate(arr):
            if i < len(arr) - 1:
                prob = ProbUse.objects.filter(first=val, second=arr[i+1])
                compability = True if prob else False
                res.append({'i': i, 'first': val.name, 'second': arr[i + 1].name, 'comp': compability})
        return res

    @staticmethod
    def first_step(word, length=False, use_probs=True):
        error_grams = {}
        true_grams = {}

        if not length:
            gram_length = gram_lengths[0]
        else:
            gram_length = length

        _gram_arr = NGramm.get_grams(word, gram_length)
        _gram_save = NGramm.objects.filter(name__in = _gram_arr)
        grams_arr = {}
        prob_arr = {}

        for i in range(0, len(_gram_arr)):
            gram_obj = filter(lambda x: x.name == _gram_arr[i], _gram_save)
            if not gram_obj:
                error_grams[i] = _gram_arr[i]
            else:
                grams_arr[i] = gram_obj[0]
                if use_probs:
                    if i > 0:
                        if grams_arr.get(i-1, False):
                            prob_use = ProbUse.objects.filter(first=grams_arr[i-1], second=grams_arr[i])
                            prob_arr[str(i-1) + '-' + str(i)] = {
                                'res': True if prob_use else False,
                                'gram1': grams_arr[i-1],
                                'gram2': grams_arr[i],
                            }
                            if prob_use:
                                true_grams[i] = _gram_arr[i]
                                prob_arr_key = str(i-2) + '-' + str(i-1)
                                if prob_arr_key in prob_arr and not prob_arr[str(i-2) + '-' + str(i-1)]['res'] and i-2 in true_grams:
                                    error_grams[i-2] = true_grams[i-2]
                                    del true_grams[i-2]
                                if i-1 in error_grams:
                                    true_grams[i-1] = error_grams[i-1]
                                    del error_grams[i-1]
                            else:
                                error_grams[i] = _gram_arr[i]
                        else:
                            true_grams[i] = _gram_arr[i]
                    else:
                        true_grams[i] = _gram_arr[i]
                else:
                    true_grams[i] = _gram_arr[i]

        # if use_probs:
        #     true_grams, error_grams = NGramm.probs_correct(prob_arr, true_grams, error_grams)

        return [true_grams, error_grams]

    @staticmethod
    def probs_correct(probs, true_arr, error_arr):
        if not true_arr and not error_arr:
            return (true_arr, error_arr)

        length = len(true_arr[0]) if 0 in true_arr else len(error_arr[0])

        for i, err_gr in error_arr.iteritems():
            if i-1 in true_arr and i+1 in true_arr or \
                    (length > 1 and i-2 in true_arr and i-1 in true_arr and i+1 in true_arr or\
                    length > 1 and i+1 in true_arr and i+2 in true_arr and i-1 in true_arr) and \
                    probs.get(str(i - 1) + "-" + str(i), False) and probs.get(str(i - 1) + "-" + str(i)).get('gram2', False):
                true_arr[i] = error_arr[i]
                error_arr[i] = False
        return (true_arr, error_arr)

    @staticmethod
    def second_step(word, true_grams, error_grams):
        res = {}

        for i, el in error_grams.iteritems():
            if not el:
                continue

            analize_str = el

            res_grams = NGramm.get_grams(analize_str, gram_lengths[1])
            objs = NGramm.objects.filter(name__in=res_grams)
            objs_dict = {}
            for j, gram in enumerate(res_grams):
                objs_dict[j] = objs.get(name=gram) if objs.filter(name=gram) else None

            # analize
            errors = []
            fully_true = []

            if 0 in objs_dict and objs_dict[0] and 1 in objs_dict and objs_dict[1]:
                prob = ProbUse.objects.filter(first=objs_dict[0], second=objs_dict[1])
            else:
                prob = False

            for j, el in enumerate(res_grams):
                if j in objs_dict and objs_dict[j] and prob:
                    fully_true.append(el)
                    continue # no mistakes in grams
                else:
                    errors.append(el)

            if objs_dict[0] and not objs_dict[1]:
                errors.append(res_grams[1][1])
            elif objs_dict[1] and not objs_dict[0]:
                errors.append(res_grams[0][0])
            elif not res_grams[0] in fully_true and not res_grams[1] in fully_true:
                errors.extend(res_grams[0][1])

            chs = []

            if res_grams[0] in errors and res_grams[1] not in errors:
                chs.append(res_grams[0][0])
            elif res_grams[0] in errors and res_grams[1]in errors:
                chs.append(res_grams[0][1])
            elif res_grams[0] not in errors and res_grams[1] in errors:
                chs.append(res_grams[1][1])
            for ch in chs:
                res[get_place_char(word, res_grams, ch)] = ch
        if not res:
            res = {}
            res['error'] = error_grams
            res['true'] = true_grams
        return res

# for 2-grams
def get_place_char(word, grams, ch):
    st = ""
    for i, gram in enumerate(grams):
        if i == 0:
            st += gram
        else:
            st += gram[1]
    return word.find(st) + st.find(ch)

class Main(models.Model):
    name = models.CharField(max_length=256)
    grams = models.ManyToManyField(NGramm)

    def __unicode__(self):
        return unicode(self.name)

    @staticmethod
    def find(word):
        """Пошук головної частини слова"""
        result = []
        prefixes = Prefix.find_all(word) + ['']
        ends = End.find_all(word) + ['']
        for pref in prefixes:
            for end in ends:
                _word = word[len(pref):-len(end)] if len(end) > 0 else word[len(pref):]
                res = Main.compute(_word)
                result.append(res)
        return result

    @staticmethod
    def compute(word):
        true_grams, error_grams = NGramm.first_step(word)
        res = NGramm.second_step(word, true_grams, error_grams)

        if len(word) <= 3 and not res:
            res = LittleWord.check_error(word)
            res = _get_result(word=word, main='', prefix='', end='', start_dict=res)

        return res

    @staticmethod
    def check_exist(word):
        is_exist = Main.objects.filter(name=word).exists()
        return is_exist

    def make(self, word):
        if Main.objects.filter(name=word):
            return False
        main = Main(
            name=word,
        )
        main.save()
        grams0 = NGramm.add_new(word, gram_lengths[0])
        grams1 = NGramm.add_new(word, gram_lengths[1])
        map(lambda x: main.grams.add(x), grams0)
        map(lambda x: main.grams.add(x), grams1)
        full = Full()
        full.make_obj('', word, '')
        ProbUse.compute(full, gram_lengths[0])
        ProbUse.compute(full, gram_lengths[1])
        return main


class LittleWord(models.Model):
    """
    Особливий клас для коротких слів (орієнтовно не більше 3-ох символів)
    Будуть переважно прийменники, сполучники і частки (можливо додати і інші частини мови)
    """
    name = models.CharField(max_length=7)

    @staticmethod
    def check_exist(word):
        if len(word) <= 3:
            res = LittleWord.objects.filter(name = word)
        else:
            res = False
        return res

    @staticmethod
    def check_error(word):
        words_statr_with = LittleWord.objects.filter(name__istartswith=word[0])
        length = 10
        reses = []

        def _check(w, old_length, reses):
            leven_dist = lev_distance(word, w)
            if leven_dist < old_length:
                length = leven_dist
                reses = [w]
            elif leven_dist == old_length:
                reses.append(w)
            return (length, reses)

        for w in words_statr_with:
            _check(w, length, reses)

        words_ends_with = LittleWord.objects.filter(name__iendswith=word[-1])
        for w in words_ends_with:
            _check(w, length, reses)
        return reses

class ProbUse(models.Model):
    """
    Клас для імовірності між грамами
    поля:
        - first - перша грама
        - second - друга грама
        - count_value - кількість зустрінутих таких пар
        - value - імовірнісна величина (кількість входжень/на кількість всіх грам)
    """
    first = models.ForeignKey(NGramm, related_name='first')
    second = models.ForeignKey(NGramm, related_name='second')
    count_value = models.IntegerField(default=0)
    value = models.FloatField(default=0)

    @staticmethod
    def compute(full_obj, gram_length):
        if not isinstance(full_obj, Full):
            return False
        word = full_obj.main.name
        _gram_arr = NGramm.get_grams(word, gram_length)
        for i in range(len(_gram_arr) - 1):
            gram_first = NGramm.objects.get_or_create(name=_gram_arr[i])[0]
            gram_first.save()
            gram_second = NGramm.objects.get_or_create(name=_gram_arr[i+1])[0]
            gram_second.save()
            prob = ProbUse.objects.get_or_create(first=gram_first, second=gram_second)[0]
            prob.count_value += 1
            prob.save()


class Full(models.Model):
    """
    Клас для повного слова
    обов'язковими є лише поля: word
    """
    word = models.CharField(max_length = 256)
    is_error = models.BooleanField(default=False)
    prefix = models.ForeignKey(Prefix, null=True, blank=True)
    end = models.ForeignKey(End, null=True, blank=True)
    main = models.ForeignKey(Main)

    @staticmethod
    def check_word(word, check_pref=True, check_end=True):
        if not isinstance(word, unicode):
            word = unicode(word.decode('utf-8'))

        prefixes = []
        prefix = True
        first = True

        if len(word) <= 3:
            little_word_res = LittleWord.check_exist(word)
            if little_word_res:
                return _get_result(
                    word=word,
                    main=little_word_res[0].name,
                    prefix='',
                    end='',
                )

        # check word is exist
        is_exists = Main.check_exist(word)
        if is_exists:
            _get_result(word=word, main=word, prefix='', end='')
        while prefix:
            end = True
            if prefix == True:
                prefix = ''
            ends = []
            while end:
                end = End.find(word, ends) if check_end else ""
                _word = word[len(prefix):-len(end)] if len(end) > 0 else word[len(prefix):]
                main = _word

                # check part exist
                is_exists = Main.check_exist(_word)
                if is_exists:
                    return _get_result(word=word, main=main, prefix=prefix, end=end)
                elif end:
                    ends.append(end)
            if prefix or first:
                first = False
                if prefix:
                    prefixes.append(prefix)
                prefix = Prefix.find(word, prefixes) if check_pref else ""

        prefixes = [''] + prefixes
        ends = [''] + ends

        reses = []

        def levenshteyn_ckeck(r, less):
            if isinstance(r, int):
                r = Main.objects.get(id=r)
            dist = lev_distance(_word, r.name)
            levenshteyn_distances[r.id] = dist
            is_one = False
            obj = False
            if less > dist:
                less = dist
                is_one = True
                obj = r
            elif less == dist:
                is_one = False
                obj = r
            return (less, is_one, obj)

        for prefix in prefixes:
            for end in sorted(ends, key=len, reverse=True):
                _word = word[len(prefix):-len(end)] if len(end) > 0 else word[len(prefix):]
                res = Main.compute(_word)
                res['word'] = _word
                reses.append(res)
                if isinstance(res, dict) and 'error' in res:
                    continue
                else:
                    for add in [0, -1, 1]:
                        erors_check_arr = Errors.check_word(_word, res, add)
                        if erors_check_arr:
                            break
                if 'error' not in res and (len(res) <= 3 or len(reses) <= 3):
                    step_result = {
                        'error': reses,
                        'variants': res,
                    }
                    levenshteyn_distances = {}
                    less = 10
                    is_one = True

                    exists_objs = []

                    for r in erors_check_arr:
                        less, is_one, obj = levenshteyn_ckeck(r, less)
                        if obj:
                            if is_one:
                                exists_objs = [obj]
                            else:
                                exists_objs.append(obj)

                    if not exists_objs:
                        try:
                            keys = filter(lambda x: isinstance(x, int), res.keys())
                            name = [_word[:keys[0]], _word[keys[-1]:]]
                        except Exception, e:
                            print str(e)
                        if name[0] and name[1]:
                            words = Main.objects.filter(name__istartswith=name[0]).filter(name__iendswith=name[1])
                        elif name[0]:
                            words = Main.objects.filter(name__istartswith=name[0])
                        elif name[1]:
                            words = Main.objects.filter(name__iendswith=name[1])
                        for r in words:
                            less, is_one, obj = levenshteyn_ckeck(r, less)
                            if obj:
                                if is_one:
                                    exists_objs = [obj]
                                else:
                                    exists_objs.append(obj)

                    if less >= 3:
                        continue
                    if exists_objs:
                        return _get_result(word=word, main=exists_objs[0].name, prefix=prefix, end=end, start_dict=step_result)



        words = {}
        incorrects = []
        for res in reses:
            parts = []
            if 'true' in res:
                keys = res['true'].keys()
                str = ""
                for i, key in enumerate(keys):
                    if i > 0 and \
                            is_one_by_one(keys[i-1], key) and \
                            res['true'][key] and res['true'][keys[i-1]] and \
                            not i + 1 in res['error']:
                        str += res['true'][key] if str == "" else res['true'][key][-1]
                    elif i > 0 and not is_one_by_one(keys[i-1], key):
                        parts.append(str)
                        str = ''
                    elif str == '' and res['true'][key]:
                        str += res['true'][key]
                if str:
                    parts.append(str)
            else:
                arr = res.items()
                if arr and (isinstance(arr[0], dict) and len(arr[0].items()) == 1) or\
                        (isinstance(arr[0], tuple) and len(arr[0][1]) == 1):
                    prev_key = 0
                    for key in filter(lambda x: isinstance(x, int), res.keys()):
                        parts.append(res['word'][prev_key:key])
                        prev_key = key + 1
                    parts.append(res['word'][prev_key:])
                else:
                    prev_key = 0
                    for key in filter(lambda x: isinstance(x, int), res.keys()):
                        if len(res['word']) > key:
                            parts.append(_word[prev_key:key])
                            prev_key = key + 2
                    if len(res['word']) > prev_key:
                        parts.append(_word[prev_key:])

            if parts and ('error' in res and 0 not in res['error'] or 0 not in res):
                try:
                    parts[0] = parts[0][:-1]
                except Exception, e:
                    print str(e)
            elif 'error' in res and 0 in res['error'] or 0 in res:
                parts[0] = parts[0][1:]
            if len(parts) > 1:
                parts[1] = parts[-1][1:]
            elif len(parts) == 0:
                continue

            if len(parts) >= 2:
                _word = Main.objects.filter(name__istartswith=parts[0], name__iendswith=parts[-1])
            elif len(parts) == 1 and 'error' in res and 0 in res['error']:
                _word = Main.objects.filter(name__iendswith=parts[0])
            elif len(parts) == 1:
                _word = Main.objects.filter(name__icontains=parts[0])
            if _word:
                try:
                    _word = filter(lambda x: len(res['word']) in range(len(x.name)-1, len(x.name) + 2), _word)
                    words[res['word']] = _word
                except Exception, e:
                    print str(e)

        less = 10
        correct = []

        for key, word_list in words.iteritems():
            for word in word_list:
                dist = lev_distance(word.name, key)
                if dist < less:
                    less = dist
                    correct = [word]
                elif dist == less:
                    correct.append(word)

        res.pop('word')
        return _get_result(word=word, main=map(lambda x: x.name, correct), prefix=prefixes, end=ends, start_dict=res)

    def make_obj(self, prefix_str, main_str, end_str):
        self.prefix = Prefix.objects.get(name=prefix_str) if prefix_str else None
        self.end = End.objects.get(name=end_str) if end_str else None
        self.word = unicode(prefix_str) + unicode(main_str) + unicode(end_str)
        grams3 = NGramm.add_new(main_str, 3)
        grams2 = NGramm.add_new(main_str, 2)
        self.main = Main.objects.get_or_create(name=main_str)[0]
        self.main.save()
        map(lambda x: self.main.grams.add(x), grams2)
        map(lambda x: self.main.grams.add(x), grams3)
        self.save()

def _get_result(word, main, prefix, end, start_dict={}):
    if isinstance(main, list):
        main = ", ".join(main)

    start_dict.update({
        'word': word,
        'prefix': prefix,
        'end': end,
        'main': main,
    })
    return start_dict

def is_one_by_one(ind1, ind2):
    if int(ind2) == int(ind1) + 1:
        return True
    else:
        return False

def next_key(i, word, _dict):
    for j in range(i+1, len(word)):
        if j in _dict:
            return j
    return False

class Errors(models.Model):
    error = models.CharField(max_length = 5)
    answer = models.CharField(max_length=5)
    count = models.IntegerField(default=0)

    def __unicode__(self):
        return unicode(self.error) + u' - ' + unicode(self.answer)

    @staticmethod
    def check_word(word, res, add=0):
        errors_to_check = []
        if res:
            str = ""
            count = 0
            for i, r in res.iteritems():
                if not isinstance(i, int):
                    continue

                if add < 0:
                    start = i + add if i > 0 else 0
                else:
                    start = i if i > 0 else 0
                if add > 0:
                    end = i if i + 1 == len(word) else i
                else:
                    end = i + add if i + 1 == len(word) else i

                str += r
                n_key = next_key(i, word, res)
                if not len(res.items()) > count + 1 or not n_key or not is_one_by_one(i, n_key):
                    errors_to_check.append({'str': str, 'start': start, 'end': end})
                    str = ''
                count += 1
        results = []
        for err_dict in errors_to_check:
            errors = Errors.objects.filter(error=err_dict.get('str'))
            if errors:
                for variant in errors:
                    main = Main.objects.filter(name__istartswith=variant)
                    if main:
                        results.append(map(lambda x: x.id, main))
            else:
                main = Main.objects.filter(name__istartswith=word[:err_dict['start']]).\
                    filter(name__endswith=word[err_dict['end']+1:])
                if main:
                    results.extend(map(lambda x: x.id, main))
        return results