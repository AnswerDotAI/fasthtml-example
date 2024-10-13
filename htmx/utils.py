from fasthtml.common import *
from uuid import uuid4
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
        return Script(f'proc_htmx("[{self.data()}]", el => {{ {self.expand(code)} }})')

class Component(FT):
    def __str__(self): return f"document.getElementById('{self.id}')"

fh_cfg['ft_cls' ]=Component
fh_cfg['auto_id' ]=True

