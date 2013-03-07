from django.core.exceptions import ImproperlyConfigured

from braces.utils import force_tuple, invert_order_by

class SelectRelatedMixin(object):
    """
    Mixin allows you to provide a tuple or list of related models to
    perform a select_related on.
    """
    select_related = None  # Default related fields to none

    def get_queryset(self):
        if self.select_related is None:  # If no fields were provided,
                                         # raise a configuration error
            raise ImproperlyConfigured("%(cls)s is missing the "
                "select_related property. This must be a tuple or list." % {
                    "cls": self.__class__.__name__})

        if not isinstance(self.select_related, (tuple, list)):
            # If the select_related argument is *not* a tuple or list,
            # raise a configuration error.
            raise ImproperlyConfigured("%(cls)s's select_related property "
                "must be a tuple or list." % {"cls": self.__class__.__name__})

        # Get the current queryset of the view
        queryset = super(SelectRelatedMixin, self).get_queryset()

        return queryset.select_related(*self.select_related)


class PrefetchRelatedMixin(object):
    """
    Mixin allows you to provide a tuple or list of related models to
    perform a prefetch_related on.
    """
    prefetch_related = None  # Default prefetch fields to none

    def get_queryset(self):
        if self.prefetch_related is None:  # If no fields were provided,
                                           # raise a configuration error
            raise ImproperlyConfigured("%(cls)s is missing the "
                "prefetch_related property. This must be a tuple or list." % {
                    "cls": self.__class__.__name__})

        if not isinstance(self.prefetch_related, (tuple, list)):
            # If the select_related argument is *not* a tuple or list,
            # raise a configuration error.
            raise ImproperlyConfigured("%(cls)s's prefetch_related property "
                "must be a tuple or list." % {"cls": self.__class__.__name__})

        # Get the current queryset of the view
        queryset = super(PrefetchRelatedMixin, self).get_queryset()

        return queryset.prefetch_related(*self.prefetch_related)


class UserQuerysetMixin(object):
    """
    Filter the queryset to include only instances attached to the current user.
    This mixin assumes that the user is not anonymous so it should be used
    in conjunction with LoginRequiredMixin.
    """
    user_field_name = 'user'
    
    def get_queryset(self):
        queryset = super(UserQuerysetMixin, self).get_queryset()
        queryset = queryset.filter(**{self.user_field_name: self.request.user})
        return queryset


class OrderingMixin(object):
    """Orders the queryset using self.ordering."""
    ordering = None

    def get_ordering(self):
        if isinstance(self.ordering, basestring):
            raise ImproperlyConfigured("%(cls)s's ordering should be a tuple, "
                " not a string." % {"cls": self.__class__.name})
        return self.ordering

    def get_queryset(self):
        queryset = super(OrderingMixin, self).get_queryset()
        ordering = self.get_ordering()
        if ordering:
            queryset = queryset.order_by(*ordering)
        return queryset


class SortableMixin(OrderingMixin):
    """
    TODO
    """
    sortables = []
    sort_parameter = 'sort'
    sort_context = 'current_sort'
    
    @property
    def ordering(self):
        requested = self.request.REQUEST.get(self.sort_parameter)
        default = force_tuple(self.get_default_sort())
        
        if not requested:
            return default
        key, desc = parse_order_by(requested)
        if not order_by:
            return force_tuple(default)
        
        order_by = self.get_order_by_for_key(key)
        if desc:
            order_by = invert_order_by_tuple(order_by)
        return order_by
    
    def get_context_data(self, **kwargs):
        """Add the current sort to the context."""
        context = super(SortableMixin, self).get_context_data(**kwargs)
        context[self.sort_context] = self.ordering
        return context
    
    def get_order_by_for_key(self, key):
        for external, internal in self.sortables:
            if key == external:
                return force_tuple(internal)
        return None
    
    def get_default_sort(self):
        """The default sort is the first element of self.sortables"""
        return self.sortables[0]
