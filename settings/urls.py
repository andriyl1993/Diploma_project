from django.conf.urls import url
from views import load_prefixes, index, load_littleword, load_words

urlpatterns = [
    url(r'^$', index, name="settings_index"),
    url(r'^load-prefixes/', load_prefixes, name="settings_load_prefixes"),
    url(r'^load-littleword/', load_littleword, name="settings_load_littleword"),
    url(r'^load-words/', load_words, name="load_words"),
]
