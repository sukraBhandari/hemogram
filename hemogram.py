import os
# from flask_migrate import Migrate
from app import create_app, db
from app.models import User, Role, Privilege, LabProcedure, Patient, Clinic,\
    Order, Event, Sample, Smear, CellImage, Comment, PathReview, Morphology,\
    BloodMorphology, Provider
app = create_app(os.environ.get('LAB_CONFIG'))
# migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Privilege=Privilege,
                LabProcedure=LabProcedure, Patient=Patient, Clinic=Clinic,
                Order=Order, Event=Event, Sample=Sample, Smear=Smear,
                CellImage=CellImage, Comment=Comment, PathReview=PathReview,
                Morphology=Morphology, BloodMorphology=BloodMorphology,
                Provider=Provider)


@app.context_processor
def util_processor():
    """
    Make get_samples function available to templages using context_processor
    """
    def get_pending_samples():
        return Sample.get_pending_data()

    def get_pending_reviews():
        return PathReview.get_pending_data()
    return dict(sample_pending_data=get_pending_samples, review_pending_data=get_pending_reviews)


@app.cli.command()
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=3).run(tests)
