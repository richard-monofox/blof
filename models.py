#!/usr/bin/env python

from django.core.exceptions import ValidationError
from django.db import models
import random
from django import forms
import datetime
from google.appengine.api import users
import re

# regex patterns used by Article.antagonise to add grammar mistakes

LEGAL_ACTIONS = ('create', 'edit', 'remove', 'feed')
IMPACTFUL_WORD = re.compile(r'\b(?P<word>\w+)!')
PUNCTUATION_IN_QUOTE = re.compile(r'(?P<word>\w+)(?P<punct>[\.,])[\"\']')
LAZY_PLURAL = re.compile(r'\b(?P<word>\w{4,})s\b')
LAZY_OWNED = re.compile(r'\b(?P<word>\w{4,})(?P<punct>\')s\b')
PUNCTUATION_FREE_WORD = re.compile(r'\b(?P<word>\w{2,}) ')

class ManageArticleForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ManageArticleForm, self).__init__(*args, **kwargs)

    article_key = forms.CharField()

    def clean_article_key(self):
        article_key = self.cleaned_data['article_key']

        model = Article.objects.get(id=article_key)

        if model.user != users.get_current_user().email():
            raise ValidationError('You do not have permission.')

        return article_key

class EditArticleForm(ManageArticleForm):
    def __init__(self, *args, **kwargs):
        super(EditArticleForm, self).__init__(*args, **kwargs)

    body = forms.CharField(max_length=500)


class FeedForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(FeedForm, self).__init__(*args, **kwargs)

    article_key = forms.CharField(required=False)

class WebserviceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(WebserviceForm, self).__init__(*args, **kwargs)

    action = forms.ChoiceField(choices=[(i, i) for i in LEGAL_ACTIONS])

class Article(models.Model):
    body = models.CharField(max_length=500)
    date = models.DateTimeField()
    user = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        """ saves article and handles edits """

        # dont update date if was an edit as this will addect ordering
        if not kwargs.pop('is_edit', False):
            self.date = datetime.datetime.utcnow()

        super(Article, self).save(*args, **kwargs)

    def date_iso(self):
        """ returns date in ISO format expected by client side javascript """
        return self.date.isoformat().split('.')[0]

    def antagonised(self, antagany=0.05):
        """ adds grammat mistakes to body """

        text = self.body

        # randomly adding incorrect punctuation
        candidates_for_mistakes = list(set(PUNCTUATION_FREE_WORD.findall(text)))

        for mistake in xrange(int(text.count(' ') * antagany)):
            word = random.choice(candidates_for_mistakes)
            text = text.replace('%s ' % word,
                                '%s%s ' % (word, random.choice(';,')))

        # richards --> richard's. using html encoded so LAZY_OWNED not affect
        text = LAZY_PLURAL.sub(r"\1&apos;s", text)

        # richard's --> richards 
        text = LAZY_OWNED.sub(r'\1s', text)

        # richard! --> "richard!"
        text = IMPACTFUL_WORD.sub(r'"\1!"', text)

        # "richard." --> "richard".
        text = PUNCTUATION_IN_QUOTE.sub(r'\1".', text)

        return text

class ArticleModelForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['body', 'id']

    def paginate(self, article_key=None):
        """ paginate over articles. Allows infinite scroll/lazy loading. """
        # django Paginator doesnt react to deleting occurs, hence using 'homebrew' method

        params = {'id__lt': article_key} if article_key else {}

        return self.Meta.model.objects.filter(**params).order_by('-date')[:5]

    def save(self, *args, **kwargs):
        # adding user to the record.
        model = super(ArticleModelForm, self).save(*args, **kwargs)
        model.user = users.get_current_user().email()
        model.save()
        return model
