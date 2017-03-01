# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models

pref_max_len = 5
end_max_len = 3

class Prefix(models.Model):
    name = models.CharField(max_length=7)

    def __unicode__(self):
        return self.name

    @staticmethod
    def find(string, not_use=[]):
        prefs = Prefix.objects.\
            filter(name__istartswith=string[0]).\
            exclude(name__in=not_use).\
            extra(select={'length':'Length(name)'}).\
            order_by('-length').\
            values('name')
        prefix = ''
        _prefix = string[0]
        if prefs:
            for i in range(1, pref_max_len):
                if filter(lambda elem: _prefix + string[i] in elem.get('name', ''), prefs):
                    _prefix += string[i]
                    if filter(lambda elem: _prefix == elem.get('name', ''), prefs):
                        prefix = _prefix
                else:
                    return prefix
        return prefix

    @staticmethod
    def find_all(word, not_use=[]):
        prefixes = []
        while (True):
            _find_pref = Prefix.find(word, prefixes)
            if _find_pref:
                prefixes.append(_find_pref)
            else:
                break
        return prefixes

class End(models.Model):
    name = models.CharField(max_length=7)

    def __unicode__(self):
        return self.name

    @staticmethod
    def find(string, not_use=[]):
        end = ""
        _end = string[-1]
        for i in range(3):
            if i == 0:
                ends = End.objects.filter(name__iendswith=_end).exclude(name__in=not_use)
            else:
                ends = filter(lambda x: x.name[:-(len(_end) + 1)] == _end, ends)
            if ends:
                end = _end
                _end = string[-(i + 2)] + _end
            else:
                return end

    @staticmethod
    def find_all(word):
        ends = []
        while True:
            _end = End.find(word, ends)
            if _end:
                ends.append(_end)
            else:
                break
        return ends

class NGramm(models.Model):
    name = models.CharField(max_length=3)

    @staticmethod
    def get_grams(word, gram_len=3):
        if not isinstance(word, unicode):
            word = word.decode('utf-8')
        word = word.strip().strip('﻿')
        return map(lambda i: word[i:i + gram_len], range(len(word)-gram_len+1))

    @staticmethod
    def add_new(word, gram_length=3):
        for x in NGramm.get_grams(word, gram_length):
            if not NGramm.objects.filter(name = x):
                obj = NGramm()
                obj.name = x
                obj.save()


class Main(models.Model):
    name = models.CharField(max_length=31)
    grams = models.ManyToManyField(NGramm)

    def __unicode__(self):
        return self.name

    @staticmethod
    def find(word):
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
        _gram_arr = NGramm.get_grams(word, 3)
        _gram_save = NGramm.objects.filter(name__in = _gram_arr)
        _error_grams = {}
        _true_grams = {}
        for i in range(0, len(_gram_arr)):
            gram_obj = filter(lambda x: x.name == _gram_arr[i], _gram_save)
            if not gram_obj:
                _error_grams[i] = _gram_arr[i]
            else:
                _true_grams[i] = _gram_arr[i]
        return {
            'error': _error_grams,
            'true': _true_grams,
        }


class LittleWord(models.Model):
    name = models.CharField(max_length=7)
    type = models.CharField(
        choices=(
            ('pr', 'Preposition'),
            ('cn', 'Conjuction'),
            ('fr', 'Fraction'),
        ),
        max_length=2
    )


#клас для імовірності між грамами
class ProbUse(models.Model):
    first = models.ForeignKey(NGramm, related_name='first')
    second = models.ForeignKey(NGramm, related_name='second')
    count_value = models.IntegerField(default=0)
    value = models.FloatField(default=0)

    @staticmethod
    def compute(full_obj):
        if not isinstance(full_obj, Full):
            return False
        word = full_obj.main.name
        _gram_arr = NGramm.get_grams(word, 3)
        for i in range(len(_gram_arr) - 1):
            gram_first = NGramm.objects.get_or_create(name=_gram_arr[i])[0]
            gram_first.save()
            gram_second = NGramm.objects.get_or_create(name=_gram_arr[i+1])[0]
            gram_second.save()
            prob = ProbUse.objects.get_or_create(first=gram_first, second=gram_second)[0]
            prob.count_value += 1
            prob.save()


class Full(models.Model):
    word = models.CharField(max_length = 63)
    is_error = models.BooleanField(default=False)
    prefix = models.ForeignKey(Prefix, null=True, blank=True)
    end = models.ForeignKey(End, null=True, blank=True)
    main = models.ForeignKey(Main)

    @staticmethod
    def check_word(word, check_pref=True, check_end=True):
        prefix = Prefix.find(word) if check_pref else ""
        end = End.find(word) if check_end else ""
        _word = word[len(prefix):-len(end)] if len(end) > 0 else word[len(prefix):]
        main = _word

        res = Main.compute(_word)
        res['word'], res['prefix'],res['end'], res['main'] = word, prefix, end, main
        return res

    def make_obj(self, prefix_str, main_str, end_str):
        self.prefix = Prefix.objects.get(name=prefix_str) if prefix_str else None
        self.end = End.objects.get(name=end_str) if end_str else None
        self.word = str(prefix_str) + str(main_str) + str(end_str)
        self.main = Main.objects.get_or_create(name=main_str)[0]
        self.main.save()
        self.save()