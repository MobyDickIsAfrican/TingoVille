from django import template
from ecommerce.models import Product

register = template.Library()


@register.filter(name = 'dj_product_name')
def dj_product_name(id):
    Item = Product.objects.get(id = id)
    return Item.Name

@register.filter(name = 'dj_product_image')
def dj_product_image(id):
    Item = Product.objects.get(id = id)
    return Item.image

@register.filter(name = 'dj_product_price')
def dj_product_price(id):
    Item = Product.objects.get(id = id)
    return Item.Price

def parse_tokens(parser, bits):
    """
    Parse a tag bits (split tokens) and return a list on kwargs (from bits of the  fu=bar) and a list of arguments.
    """

    kwargs = {}
    args = []
    for bit in bits[1:]:
        try:
            try:
                pair = bit.split('=')
                kwargs[str(pair[0])] = parser.compile_filter(pair[1])
            except IndexError:
                args.append(parser.compile_filter(bit))
        except TypeError:
            raise template.TemplateSyntaxError('Bad argument "%s" for tag "%s"' % (bit, bits[0]))

    return args, kwargs

class ZipLongestNode(template.Node):
    """
    Zip multiple lists into one using the longest to determine the size

    Usage: {% zip_longest list1 list2 <list3...> as items %}
    """
    def __init__(self, *args, **kwargs):
        self.lists = args
        self.varname = kwargs['varname']

    def render(self, context):
        lists = [e.resolve(context) for e in self.lists]

        if self.varname is not None:
            context[self.varname] = [i for i in map(lambda *a: a, *lists)]
        return ''
@register.tag
def zip_longest(parser, token):
    bits = token.contents.split()
    varname = None
    if bits[-2] == 'as':
        varname = bits[-1]
        del bits[-2:]
    else:
        # raise exception
        pass
    args, kwargs = parse_tokens(parser, bits)

    if varname:
        kwargs['varname'] = varname

    return ZipLongestNode(*args, **kwargs)
