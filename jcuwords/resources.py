from fanstatic import Library
from fanstatic import Resource


library = Library('jcu.words', 'static')
future_fonts = Resource(library, 'dle7wjq-d.css')
css_resource = Resource(library, 'main.css', depends=(future_fonts,))
