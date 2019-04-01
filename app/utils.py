import os
import secrets
import random
import string
from enum import Enum
from dateutil.relativedelta import *
from datetime import date
from flask import current_app, render_template, abort
from flask_login import current_user
from app import mail
from PIL import Image
from functools import wraps
from flask_mail import Message
from threading import Thread


# runs thread in the background
def send_async_email(app, message):
    """
    make application instance accessible for email server to access
    configuration values
    """
    with app.app_context():
        mail.send(message)


def send_email(to, subject, template, **kwargs):
    """
    function to send email with predefined templates
    email is background thread
    """
    app = current_app._get_current_object()
    message = Message(app.config['MAIL_SUBJECT'] + ' ' + subject,
                      sender=app.config['MAIL_SENDER'],
                      recipients=[to])
    message.body = render_template(template + '.txt', **kwargs)
    message.html = render_template(template + '.html', **kwargs)
    return Thread(target=send_async_email, args=[app, message]).start()


class Gender(Enum):
    """
    Enum type gender for patient sex
    Can add more options if needed
    """
    MALE = 'male'
    FEMALE = 'female'


class FluidType(Enum):
    """
    Type of Fluids accepted for cell counts
    Can add more options if needed
    """
    WHOLE_BLOOD = "whole blood"


class OrderName(Enum):
    """
    Type of Test accepted
    Can add more options if needed
    """
    CBD = 'cbd'


class CellType(Enum):
    """
    Type of cells in blood
    Used in Morphology
    """
    WBC = 'wbc'
    RBC = 'rbc'
    PLATELET = 'platelet'


class ResultOption(Enum):
    """
    Red Blood Cells abnormalities may be graded
    on three scales
    """
    SLIGHT = 'slight'
    MODERATE = 'moderate'
    MARKED = 'marked'


class ProviderDegree(Enum):
    """
    Provider Degree Title
    """
    MD = 'MD'
    MBBS = 'MBBS'
    PA = 'PA'
    NP = 'NP'


class InstrumentType(Enum):
    """
    Instrument used in capturing
    cells images from slide
    """
    CELLAVISION = 'cellavision'


class OrderEventType(Enum):
    """
    Enum to capture different events
    while order is being processed
    """
    CREATED = 'Order Created'
    RECEIVED_SAMPLE = 'Sample Received'
    RECEIVED_SMEAR = 'Smear Received'
    SMEAR_ANALYZED = 'Smear Analyzed'
    PATHRV = 'Path Review Ordered'
    PATH_REVIEWED = 'Path Review Completed'
    CORRECTED = 'Report Corrected'
    DISCARD = 'Smear Discarded'


class Classifier(Enum):
    """
    Different type of cells present
    on a blood slide
    """
    UNIDENTIFIED = 'unidentified'
    NEUTROPHIL = 'neutrophils'
    BASOPHIL = 'basophils'
    EOSINOPHIL = 'eosinophils'
    LYMPHOCYTE = 'lymphocytes'
    MONOCYTE = 'monocytes'
    IMMATURE_GRANULOCYTES = 'immature granulocytes'
    BLAST = 'blasts'
    UNCLASSIFIED = 'unclassified'
    NRBC = 'nrbcs'
    SMUDGE_CELLS = 'sumdge cells'


class Privilege:
    """
    Define set of Privileges user can hold
    """
    VIEW = 1
    CREATE = 2
    UPDATE = 4
    DELETE = 8
    MODERATE = 16
    OVERWRITE = 32
    ADMIN = 64


def define_roles():
    """
    Predefined roles with specific Privilege
    If roles dict needs update, Role.preset_roles needs to called
    """
    roles = {
        'Basic': [Privilege.VIEW],
        'Assistant': [Privilege.VIEW, Privilege.CREATE],
        'Technologist': [Privilege.VIEW, Privilege.UPDATE],
        'Lead': [Privilege.VIEW, Privilege.CREATE, Privilege.UPDATE,
                 Privilege.DELETE, Privilege.MODERATE, Privilege.OVERWRITE],
        'Pathologist': [Privilege.VIEW, Privilege.UPDATE],
        'Admin': [Privilege.VIEW, Privilege.CREATE, Privilege.UPDATE,
                  Privilege.DELETE, Privilege.MODERATE, Privilege.ADMIN]

    }
    return roles


def save_image(picture, output_size=(350, 350), folder='slide_images'):
    """
    function to store images on the server
    Blood cells images have default image sixe
    """
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(picture.filename)
    file_name = random_hex + file_ext
    picture_path = os.path.join(current_app.root_path,
                                'static/images/' + folder,
                                file_name)
    pic = Image.open(picture)
    pic.thumbnail(output_size)
    pic.save(picture_path)
    return file_name


def privilege_required(privilege):
    """
    decorator function to check if users
    have certain privilege to access data
    Raise abort error if no privilege
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(privilege):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """
    decorator functions to check admin privilege
    """
    return privilege_required(Privilege.ADMIN)(f)


def calculate_delta(dob):
    """
    Calculate time difference between now and birthdate
    """
    return relativedelta(date.today(), dob)


def calculate_age(dob):
    """
    functon to calculate patient age
    """
    age = calculate_delta(dob)
    if age.years >= 1:
        return "{}Y".format(age.years)
    elif age.months >= 1:
        return "{}M and {}D".format(age.months, age.days)
    return "{}D".format(age.days)


def wbc_classification():
    """
    Type of Nucleated Blood cells seen in
    a smear
    """
    wbc_class = ['unidentified', 'neutrophils', 'lymphocytes', 'monocytes', 'basophils',
                 'eosinophils', 'immature_granulocytes', 'blasts', 'unclassified',
                 'nrbcs', 'smudge_cells']
    return wbc_class


def wbc_exclusion():
    """
    function that returns list of indexes of White Blood Cell(WBC) not
    included in the calcuation of WBC differential
    """
    return [0, 9, 10]


def wbc_trial():
    """
    function that return dictinary of WBC
    dict is used by javascript
    to display images and create WBC differential report
    dynamically in the client side while classification
    is in progress
    """
    # list = Display_drag_n_drop, always_display_on_report, display_if_present
    wbc_dict = {'unidentified': [1, 0, 0], 'neutrophils': [1, 1, 1],
                'lymphocytes': [1, 1, 1], 'monocytes': [1, 1, 1],
                'basophils': [1, 1, 1], 'eosinophils': [1, 1, 1],
                'immature_granulocytes': [1, 0, 1], 'blasts': [1, 0, 1],
                'unclassified': [1, 0, 1], 'nrbcs': [1, 0, 1],
                'smudge_cells': [1, 0, 0]}
    return wbc_dict


def diff_pickle(wbc, diff):
    """
    function to generate WBC differential results as dictonary
    param: wbc
    param: diff - list of tuples in following order (cell_index, cell_count)

    """
    exclude = wbc_exclusion()
    cell_d = wbc_classification()
    always_report = list(range(1, 6))
    total = 0
    nrbcs = False
    # calculate total number of WBC count
    # which excludes NRBCs, SMUDGE CELLS

    for cell_index, count in diff:
        if cell_index not in exclude:
            total += count
        if cell_d.index('nrbcs') == cell_index:
            nrbcs = True
            nrbcs_count = count
    # Five classes of WBC (neutrophils, lymphocytes, monocytes, eosinophils, basophils)
    # are always reported in lab result, even if the count is 0
    # list of all cell present in diff
    cells_already_present = [i[0] for i in diff]
    # add cells to diff if cell not present in 'always_report'
    diff.extend([(i, 0) for i in always_report if i not in cells_already_present])

    # create dict to hold diff report
    d = {}
    """
    # TODO - NO WBC PRESENT
    # Possible case - Patient has no WBC
    # OR Instrument did not capture WBC images
    """
    if total > 0:
        cell = {}
        factor = round((100 / total), 3)
        for cell_index, count in diff:
            if cell_index not in exclude:
                rel = round(count * factor)
                ab = (wbc * rel / 100)
                cell[cell_d[cell_index]] = {'seq': cell_index, 'relative': round(rel, 1), 'absolute': round(ab, 2)}
        # In Lab report result, cell order has to be maintained
        # sort cells based on sequence.
        d['wbc'] = sorted(cell.items(), key=lambda item: item[1]['seq'])
        if nrbcs:
            rel = round(nrbcs_count * factor)
            ab = (wbc * rel / 100)
            d['nrbcs'] = {'relative': round(rel, 1), 'absolute': round(ab, 2)}

    return {'diff': d, 'total': total}


def smear_path_review():
    """
    helper function when data is modified
    in PathReview data model
    """
    return 'Smear to be reviewed by Pathologist'


def get_ref_range(dob, gender):
    """
    helper function to generate lab result reference range
    for patient based on their birth_date and gender
    TODO
    """
    pass


def random_string(length=6):
    """
    helper function to generate random string
    """
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(length))
