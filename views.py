#!/usr/bin/env python

from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseRedirect
from  django.shortcuts import render_to_response
from django.views.generic.base import TemplateView
from json import dumps
import models
from google.appengine.api import users
from django.middleware.csrf import get_token

class BlofView(TemplateView):
    """ serve main page """

    template_name = 'blof.html'

    def dispatch(self, request):

        # making easily accessible to get_context_data
        self.request = request

        # get logged in google user.
        self.blof_user = users.get_current_user()

        # redirect to login page if no active user
        if not self.blof_user:
            return HttpResponseRedirect(users.create_login_url('/'))

        # return html of the main page
        return render_to_response(self.template_name, self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(BlofView, self).get_context_data(**kwargs)
        context['articles'] = models.ArticleModelForm().paginate()
        context['blof_user'] = self.blof_user.email()
        context['logout_url'] = users.create_logout_url('/')
        context['csrf_token'] = get_token(self.request)
        return context

class WebserviceView(TemplateView):
    """ handle webservice requests. returns html or json of validation errors"""
    http_method_names = ['post']
    errors = {}
    template_name = ''

    def post(self, request, *args, **kwargs):
        super(WebserviceView, self).get(self, **kwargs)
        context = None

        # using .dict() method to make mutable.
        form_data = request.POST.dict()

        # validating that 'action' requested is valid
        form = models.WebserviceForm(form_data)

        if not form.is_valid():
            self.errors = dumps(form.errors)
        else:
            
            # getting form to validate webservice function
            self.action = form_data['action']
            webservice_form_name = {'create': 'ArticleModelForm',
                                    'edit': 'EditArticleForm',
                                    'remove': 'ManageArticleForm',
                                    'feed': 'FeedForm'}[self.action]
            webservice_form = getattr(models, webservice_form_name)(form_data)

            if not webservice_form.is_valid():
                self.errors = webservice_form.errors
            else:
                # executing the webservice action
                self.cleaned_data = webservice_form.cleaned_data
                context = getattr(self, self.action)(webservice_form)

        if self.errors:
            # return json of validation errors. status 400 so client can react.
            return HttpResponseBadRequest(content=dumps(self.errors),
                                          content_type='application/json')
        elif context:
            # return html
            return render_to_response(self.template_name, context)
        else:
            # "nothing" to return.
            return HttpResponse()

    def create(self, webservice_form):
        """ created article """

        article_key = webservice_form.save().id
        article = models.Article.objects.get(id=article_key)

        self.template_name = 'article.html'
        return {'article': article, 'blof_user': article.user}

    def edit(self, webservice_form):
        """ edit existing article """

        article_key = self.cleaned_data['article_key']
        article = models.Article.objects.get(id=article_key)
        article.body = self.cleaned_data['body']
        article.save(is_edit=True)

        self.template_name = 'article.html'

        return {'article': article, 'blof_user': article.user}

    def remove(self, webservice_form):
        """ delete existing article """

        models.Article.objects.get(id=self.cleaned_data['article_key']).delete()

    def feed(self, webservice_form):
        """ gets articles. if `article_key` posted then will start there """

        article_key = self.cleaned_data['article_key']
        articles = models.ArticleModelForm().paginate(article_key)
        self.template_name = 'articles.html'

        return {'articles': articles }
<<<<<<< HEAD
=======
  
>>>>>>> 34ccc4cc1fe7adc513a697f00d5b2a0cb157e3c8
