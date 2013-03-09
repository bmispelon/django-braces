from collections import OrderedDict

from django.core.exceptions import ImproperlyConfigured

from braces.utils import force_tuple, invert_order_by_tuple

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
    """
    Orders the queryset using self.ordering.
    The ordering attribute can either be a string or a tuple/list:
    
        * 'name'
        * '-name'
        * ('last_name', 'first_name')
        * ('name', '-age')
    Note that giving an empty tuple will reset the ordering of the queyset.
    """
    ordering = None

    def get_ordering(self):
        if self.ordering is None:
            raise ImproperlyConfigured("%(cls)s is missing an ordering "
                "attribute." % {"cls": self.__class__.name})
        return force_tuple(self.ordering)

    def get_queryset(self):
        queryset = super(OrderingMixin, self).get_queryset()
        ordering = self.get_ordering()
        queryset = queryset.order_by(*ordering)
        return queryset


class SortableMixin(OrderingMixin):
    """
    A mixin that will order a queryset based on a parameter supplied in the
    URL.
    To use it, just supply a list of accepted_orderings where each item can be
    one of the following:
    
    * 'name':
        ?sort=name results in order_by('name')
        ?sort=-name           order_by('-name')
    * ('external', 'name'):
        ?sort=external results in order_by('name')
        ?sort=-external           order_by('-name')
    * ('namedesc', '-name'):
        ?sort=namedesc results in order_by('-name')
        ?sort=-namedesc           order_by('name')
    * ('name', ('last_name', 'first_name')):
        ?sort=name results in order_by('last_name', 'first_name')
        ?sort=-name           order_by('-last_name', '-first_name')
    * ('foo', ('name', '-age')):
        ?sort=foo results in order_by('name', '-age')
        ?sort=-foo           order_by('-name', 'age')
    """
    accepted_orderings = []
    default_ordering = None
    sort_parameter = 'sort'
    
    def get_default_order_by(self):
        """
        If self.default_ordering is not provided, return the first item
        of self.accepted_orderings.
        """
        if self.default_ordering is not None:
            return force_tuple(self.default_ordering)
        return self.orderings_dict.items()[0][1]
    
    @property
    def orderings_dict(self):
        """
        An OrderedDict normalized version of self.accepted_orderings where the
        keys are the accepted sorting keys and the values are tuples which can
        be passed unpacked to queryset.order_by()
        """
        if not self.accepted_orderings:
            raise ImproperlyConfigured("%(cls)s is missing an "
                "accepted_orderings attribute." % {'cls': self.__class__.name})
        orderings = OrderedDict()
        for t in self.accepted_orderings:
            if isinstance(t, basestring):
                orderings[t] = force_tuple(t)
            elif len(t) == 1:
                orderings[t[0]] = force_tuple(t[0])
            elif len(t) == 2:
                orderings[t[0]] = force_tuple(t[1])
            else:
                raise ImproperlyConfigured("%(cls)s has an invalid "
                    "accepted_orderings attribute." % {
                        'cls': self.__class__.name
                    })
        return orderings
    
    def get_ordering(self):
        requested = self.request.REQUEST.get(self.sort_parameter)
        default = self.get_default_order_by()
        
        if not requested:
            return default
        key, inverted = parse_order_by(requested)
        order_by = self.orderings_dict.get(key)
        if order_by is None: # Invalid key requested
            return default
        if inverted:
            order_by = invert_order_by_tuple(order_by)
        return order_by
