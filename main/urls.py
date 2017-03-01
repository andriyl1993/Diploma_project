from django.conf.urls import url
from views import index, check_word

urlpatterns = [
    url(r'^$', index, name="settings_index"),
    url(r'^check-word/', check_word, name="settings_index"),
]
