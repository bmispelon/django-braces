from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

class CsrfExemptMixin(object):
    """
    Exempts the view from CSRF requirements.

    NOTE:
        This should be the left-most mixin of a view.
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CsrfExemptMixin, self).dispatch(*args, **kwargs)


class UserFormKwargsMixin(object):
    """
    CBV mixin which puts the user from the request into the form kwargs.
    Note: Using this mixin requires you to pop the `user` kwarg
    out of the dict in the super of your form's `__init__`.
    """
    def get_form_kwargs(self):
        kwargs = super(UserFormKwargsMixin, self).get_form_kwargs()
        # Update the existing form kwargs dict with the request's user.
        kwargs.update({"user": self.request.user})
        return kwargs


class SuccessURLRedirectListMixin(object):
    """
    Simple CBV mixin which sets the success url to the list view of
    a given app. Set success_list_url as a class attribute of your
    CBV and don't worry about overloading the get_success_url.

    This is only to be used for redirecting to a list page. If you need
    to reverse the url with kwargs, this is not the mixin to use.
    """
    success_list_url = None  # Default the success url to none

    def get_success_url(self):
        # Return the reversed success url.
        if self.success_list_url is None:
            raise ImproperlyConfigured("%(cls)s is missing a succes_list_url "
                "name to reverse and redirect to. Define "
                "%(cls)s.success_list_url or override "
                "%(cls)s.get_success_url()"
                "." % {"cls": self.__class__.__name__})
        return reverse(self.success_list_url)


class NextMixin(object): # TODO: name
    """
    A mixin for generic CBV that defines get_success_url to take into account
    a parameter in the request.
    If that parameter is not present, or is empty, fall back to a default URL.
    """
    default_success_url = None
    success_url_param = 'next'
    success_url_context = 'next'
    allow_external_redirect = False

    def get_default_success_url(self):
        """Return the fallback URL for when the request contains no redirect
        parameter.
        """
        if not self.default_success_url:
            raise ImproperlyConfigured("%(cls)s is missing a fallback success "
                "URL. Define %(cls)s.default_success_url or override "
                "%(cls)s.get_default_success_url()"
                "." % {"cls": self.__class__.__name__})
        return self.default_success_url

    def get_success_url(self):
        """Look for a redirect URL in the request parameters (GET or POST)."""
        if self.success_url: # TODO: document this behaviour
            return super(NextMixin, self).get_success_url()
        next = self.request.REQUEST.get(self.success_url_param)
        fallback = self.get_default_success_url()
        if next and self.is_valid_redirect(next):
            return next
        return fallback

    def is_valid_redirect(self, url):
        return True # TODO

    def redirect(self):
        """A utility method that returns a 302 HTTP response."""
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        """Add the computed next URL to the context."""
        context = super(NextMixin, self).get_context_data(**kwargs)
        context[self.success_url_context] = self.get_success_url()
        return context
