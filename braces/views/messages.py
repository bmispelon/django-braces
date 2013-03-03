from django.utils.functional import curry
from django.contrib.messages import api as messages_api


class _MessageWrapper(object):
    """Wrap the django.contrib.messages.api module to automatically pass a given
    request object as the first parameter of function calls.
    
    """
    def __init__(self, request):
        self.request = request
    
    def __getattr__(self, attr):
        """Retrieve the function in the messages api and curry it with the
        instance's request.
        
        """
        fn = getattr(messages_api, attr)
        return curry(fn, self.request)


class MessageMixin(object):
    """Add a `messages` attribute on the view instance that wraps
    `django.contrib .messages`, automatically passing the current request object.
    
    """
    def dispatch(self, request, *args, **kwargs):
        self.messages = _MessageWrapper(request)
        return super(MessageMixin, self).dispatch(request, *args, **kwargs)


class FormMessageMixin(MessageMixin):
    """Add contrib.messages support in views that use FormMixin."""
    form_valid_message = ""
    form_invalid_message = ""
    
    def form_valid(self, form):
        response = super(FormMessageMixin, self).form_valid(form)
        if self.form_valid_message:
            self.messages.success(self.form_valid_message)
        return response
    
    def form_invalid(self, form):
        response = super(FormMessageMixin, self).form_invalid(form)
        if self.form_invalid_message:
            self.messages.error(self.form_invalid_message)
        return response


class DeleteMessageMixin(MessageMixin):
    """Provide message support to generic.DeleteView."""
    delete_message = ""
    
    def delete(self, request, *args, **kwargs):
        response = super(DeleteMessageMixin, self).delete(request, *args, **kwargs)
        if self.delete_message:
            self.messages.success(self.delete_message)
        return response
