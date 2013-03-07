def force_tuple(value):
    if isinstance(value, basestring):
        return (value,)
    return tuple(value)

def invert_order_by(s):
    if s.startswith('-'):
        return s[1:]
    return '-%s' % s

def invert_order_by_tuple(t):
    return tuple(invert_order_by(s) for s in t)

def parse_order_by(s):
    if s.startswith('-'):
        return s[1:], True
    return s, False

def unparse_order_by(field, desc):
    return '%s%s' % ('-' if desc else '', field)
