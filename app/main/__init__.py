from flask import Blueprint
from ..utils import Privilege
main = Blueprint('main', __name__)

from . import routes


@main.app_context_processor
def inject_privilege():
    return dict(Privilege=Privilege, type=type, int=int)
