from . import db
from sqlalchemy import exc


def commit():
    """
    Helper to commit the db session
    """
    db.session.commit()


def create(model):
    """
    Helper to attempt to create a new instance of an object
    """
    try:
        db.session.add(model)
        commit()
    except exc.IntegrityError as e:
        db.session.rollback()


def create_all(models):
    """
    Helper function to create instances of objects
    """
    try:
        db.session.add_all(models)
        commit()
    except exc.IntegrityError as e:
        db.session.rollback()


def update(model):
    """
    Helper to update a model
    """
    commit()
    db.session.refresh(model)


def flush():
    """
    Helper to attempt flush or roll back if exception
    """
    try:
        db.session.flush()
    except exc.IntegrityError as e:
        db.session.rollback()


def delete(model):
    """
    Helper to attempt to delete a model
    """
    if model:
        try:
            db.session.delete(model)
            db.session.commit()
        except exc.IntegrityError as e:
            db.session.rollback()
