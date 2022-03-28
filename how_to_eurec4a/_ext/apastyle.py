from pybtex.style.formatting.unsrt import Style as UnsrtStyle
from pybtex.style.labels.alpha import LabelStyle as AlphaLabelStyle
from pybtex.plugin import register_plugin


class ApaLabelStyle(AlphaLabelStyle):
    def format_label(self, entry):
        return "APA"


class ApaStyle(UnsrtStyle):
    default_label_style = 'apa'

def setup(app):
    register_plugin('pybtex.style.labels', 'apa', ApaLabelStyle)
    register_plugin('pybtex.style.formatting', 'apastyle', ApaStyle)
