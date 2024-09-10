from fasthtml import common as fh
from uuid import uuid4
from base64 import b85encode
from string import Formatter

def extract_names(s): return [o for _,o,_,_ in Formatter().parse(s) if o is not None]

class RsJs:
    def __init__(self, nm): self.nm = nm
    def ref(self, k): return f'$("[{self.data(k)}]", el)'

    def expand(self, s):
        d = {o:self.ref(o) for o in extract_names(s)}
        return s.format(**d)

    def data(self, nm=''):
        if not nm: return f'data-{self.nm}'
        return f'data-{self.nm}-{nm}'

    def __getattr__(self, k): return {self.data(k): True}
    @property
    def d(self): return {self.data(): True}

    def __call__(self, code):
        s = f'proc_htmx("[{self.data()}]", el => {{ {self.expand(code)} }})'
        return fh.Script(s)


def unqid():
    res = b85encode(uuid4().bytes)
    return res.decode().replace('"', '').replace("'", '')

class Component(fh.FT):
    def __str__(self): return f"document.getElementById('{self.id}')"

def component(*args, **kw):
    if id not in kw: kw['id'] = unqid()
    return fh.ft_hx(*args, **kw, ft_cls=Component)

Output = fh.partial(component, 'output')
Button = fh.partial(component, 'button')

