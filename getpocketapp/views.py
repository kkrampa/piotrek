from django.core.urlresolvers import reverse_lazy
from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.views.generic.base import View
from django.views.generic.edit import FormView
from django.conf import settings

from getpocketapp.forms import FileForm
from pocket import Pocket


class HomeView(FormView):
    form_class = FileForm
    template_name = 'getpocketapp/home.html'
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('access_token'):
            request_token = Pocket.get_request_token(consumer_key=settings.CONSUMER_KEY)
            request.session['request_token'] = request_token
            auth_url = Pocket.get_auth_url(code=request_token, redirect_uri='http://localhost:8000/token')
            return HttpResponseRedirect(auth_url)
        return super(HomeView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        pocket_instance = Pocket(settings.CONSUMER_KEY, self.request.session['access_token'])
        file = self.request.FILES['file']
        for url in file.readlines():
            pocket_instance.add(url.decode().rstrip())
            # pocket_instance.bulk_add(item_id='', url=url.decode().rstrip())
        # pocket_instance.commit()
        return super(HomeView, self).form_valid(form)


class TokenView(View):
    def get(self, request, *args, **kwargs):
        user_credentials = Pocket.get_credentials(
            consumer_key=settings.CONSUMER_KEY, code=request.session.get('request_token')
        )
        request.session['access_token'] = user_credentials['access_token']
        return redirect('home')
