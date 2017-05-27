from django.conf.urls import url
from views import load_prefixes, index, load_littleword, load_words, show_words, add_manually,\
    load_all_words

urlpatterns = [
    url(r'^$', index, name="settings_index"),
    url(r'^load-prefixes/', load_prefixes, name="settings_load_prefixes"),
    url(r'^load-littleword/', load_littleword, name="settings_load_littleword"),
    url(r'^load-words/', load_words, name="load_words"),
    url(r'^show-words/', show_words, name="show_words"),
    url(r'^add-manually/', add_manually, name="add-manually"),
    url(r'^load-all-words/', load_all_words, name="load_all_words"),
]
