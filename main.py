import logging
import os

import json
import glob
from functools import wraps

from fastapi import FastAPI, Request
from starlette.types import Scope
from starlette.responses import Response
from weasyprint import HTML

from jinja2 import Environment, FileSystemLoader


logging.basicConfig(level='DEBUG', format='%(asctime)s %(levelname)s %(name)s:%(pathname)s:%(lineno)s %(message)s')


app = FastAPI()

languages = {}
# Find all translation files
language_list = glob.glob("languages/*.json")
# Loop the language files and file the dictionary with key and values
for lang in language_list:
    filename = os.path.basename(lang)
    # Use the file name as the key,
    lang_code, ext = os.path.splitext(filename)

    # Open the file
    with open(lang, 'r', encoding='utf8') as file:
        # Open the data as json and fill the translation dictionary
        languages[lang_code] = json.load(file)


def environment():
    """
    Set up the jinja2 with File Loader.
    """
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_dir, 'templates')

    j2_env = Environment(
        loader=FileSystemLoader(template_dir),
        trim_blocks=True,
    )

    return j2_env


class PDFResponse(Response):
    """
    Response class to automatically add the media type for PDF file to the http response
    """
    media_type = "application/pdf"


def add_i18n_translations(func):
    """
    Decorator to add i18n translations information into the requests before the API gets the request
    :param func:
    :return:
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs['request']
        # Make sure there is request context
        assert request
        logging.debug(f"request.headers: {request.headers}")

        # Get the locale from the headers
        locale = request.headers.get('accept-language')
        # Make sure the requested local actually exists in language keys, otherwise default to english
        if locale not in languages.keys():
            logging.debug(f'Requested locale: {locale}, not available, defaulting to en')
            locale = 'en'
        # Add translation data into the request
        kwargs['request'].i18n = languages[locale]

        return await func(*args, **kwargs)

    return wrapper


class I18nRequest(Request):
    """
    Class to make requests include a translations field
    """
    def __init__(self, scope: Scope):
        super().__init__(scope)
        self.i18n = None


@app.get('/generate-pdf')
@add_i18n_translations
async def generate_pdf(request: I18nRequest):
    """
    A FastAPI endpoint that will create a translatable PDF file
    :param request:
    :return:
    """
    # Grab the template
    template = environment().get_template('pdf_template.html')
    # Initialize the context
    context = {}
    # Update context with translations data
    context.update(request.i18n)
    # Assert the system generated translations
    assert context is not None
    # TODO MAKE SURE NO KEYS IN CONTEXT MATCH THE TRANSLATIONS IN THE LANGUAGE JSON FILES
    data_dict = {
        'data_point_1': 'Testing 123',
        'data_point_2': 'Testing 456',
        'data_point_3': 'Testing 789',
        # 'title': "We don't want to overwrite this key because it is a translation"
    }

    # Assert we are not trying to update a translation
    key_collision = set(data_dict.keys()).intersection(context.keys())
    assert len(key_collision) == 0

    context.update(data_dict)

    logging.debug(f'context: {context}')
    # Pass the context data to the template, this includes translation context keys
    html = template.render(context)
    # Create the PDF, this may need to change to a streaming response
    pdf_content = HTML(string=html).write_pdf()
    return PDFResponse(content=pdf_content)
