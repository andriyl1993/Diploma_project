from django.conf.urls import url
from views import index, check_word, check_text

urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^check-word/', check_word, name="check_word"),
    url(r'^check-text/', check_text, name="check_text"),
]
