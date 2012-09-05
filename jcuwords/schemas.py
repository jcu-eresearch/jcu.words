import colander
import deform

from pyramid_deform import CSRFSchema

def validate_keyword(node, value):
    values = value.strip().split()
    if len(values) > 1:
        raise colander.Invalid(node,
                               'Please use separate fields to input'
                               ' multiple words.')


class Keywords(colander.SequenceSchema):
    keyword = colander.SchemaNode(
        colander.String(),
        validator=validate_keyword,
        missing='',
    )


class AddKeywordsSchema(CSRFSchema, colander.MappingSchema):
    keywords = Keywords(
        title='Your words',
        validator=colander.Length(5),
        widget=deform.widget.SequenceWidget(
            min_len=5,
            max_len=5,
            add_subitem_text_template="Add another word")
    )
