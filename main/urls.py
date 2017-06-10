from django.conf.urls import url
from views import index, check_word, check_text, n_gram, leven, test_script, test_levenshteyn,\
    test_ngram_with, test_ngram_without

urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^check-word/', check_word, name="check_word"),
    url(r'^check-text/', check_text, name="check_text"),
    url(r'^check-ngram/', n_gram, name="check_ngram"),
    url(r'^check-levenshteyn/', leven, name="check_levenshteyn"),
    url(r'^test/', test_script, name="test_script"),
    url(r'^test-levensh/', test_levenshteyn, name="test_levensh"),
    url(r'^test-ngram-without/', test_ngram_without, name="test_ngram_without"),
    url(r'^test-ngram-with/', test_ngram_with, name="test_ngram_with"),

]
