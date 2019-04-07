import os
import bleach
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin
from markdown import markdown
from . import db, login_manager
from .utils import Privilege, define_roles, calculate_age, Gender, FluidType,\
    OrderName, CellType, ProviderDegree, OrderEventType, InstrumentType


class User(UserMixin, db.Model):
    """
    Create a User table
    :title: user job title
    :user_since: user first registration date
    :last_visit: user last visit to the app
    :accound_confirmed: boolean to confirm that user account confirmation

    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, index=True)
    username = db.Column(db.String(64), unique=True)
    user_first_name = db.Column(db.String(64), nullable=False)
    user_last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    title = db.Column(db.String(64))
    profile_image = db.Column(db.String(20), nullable=False, default='default.jpg')
    user_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_visit = db.Column(db.DateTime(), default=datetime.utcnow)
    account_confirmed = db.Column(db.Boolean, default=False)

    # FK, establishes the relationship with 'roles' table
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    # 1 to many relationship
    procedures = db.relationship('LabProcedure', backref='author', lazy='dynamic')
    default_morphologies = db.relationship('Morphology', backref='author', lazy='dynamic')
    events = db.relationship('Event', backref='logger', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == os.environ.get('LAB_ADMIN'):
                self.role = Role.query.filter_by(name='Admin').first()
            else:
                self.role = Role.query.filter_by(default=True).first()

    def __repr__(self):
        return '<User Email %r>' % self.email

    @property
    def password(self):
        """
        Prevent password from being accessed
        """
        raise AttributeError('Password cannot be retreived directly')

    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Verify if hashed password matches the user's acutal password
        """
        return check_password_hash(self.password_hash, password)

    def check_account_confirmation(self):
        """
        User account status
        """
        return self.account_confirmed

    # token functions
    def get_new_user_token(self, expires=3600):
        """
        Generate an account confirmation token with time limit
        """
        key = Serializer(current_app.config['SECRET_KEY'], expires)
        return key.dumps({'confirm_id': self.id}).decode('utf-8')

    def verify_new_user_token(self, token):
        """
        Verification of token to confirm the legitimate email
        """
        key = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = key.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm_id') != self.id:
            return False
        # update the db with confirmed account value
        self.account_confirmed = True
        return True

    def get_password_reset_token(self, expires=1800):
        """
        Generate token with expiration, when password reset request is made
        """
        s = Serializer(current_app.config['SECRET_KEY'], expires)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_password_reset_token(token, new_password):
        """
        Verify the validity of token, if valid update the user password
        """
        key = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = key.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('user_id'))
        if user is None:
            return False
        else:
            user.password = new_password
            db.session.add(user)
            return True

    def can(self, perm):
        """
        Verify if user can perform cetrain functions
        """
        return self.role is not None and self.role.has_privilege(perm)

    def is_administrator(self):
        """
        Verify if the user has administration privilege
        """
        return self.can(Privilege.ADMIN)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Role(db.Model):
    """
    create a role table
    :name: predefined role name that is assigned to each used
    :default: boolean value to check if user has default role
    :privileges: each role has predefined previlege
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    privileges = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.privileges is None:
            self.privileges = 0

    @staticmethod
    def preset_roles():
        """
        Function to create and update roles
        """
        roles = define_roles()
        default_role = 'Basic'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_privileges()
            for perm in roles[r]:
                role.add_privilege(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_privilege(self, perm):
        """
        function to add privilege for user
        """
        if not self.has_privilege(perm):
            self.privileges += perm

    def remove_privilege(self, perm):
        """
        function to remove a privilege
        """
        if self.has_privilege(perm):
            self.privileges -= perm

    def reset_privileges(self):
        """
        function to reset privilege to 0
        """
        self.privileges = 0

    def has_privilege(self, perm):
        """
        function to check if user has certain privilege
        """
        return self.privileges & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name


class LabProcedure(db.Model):
    """
    Create a laboratory procedure AKA Standard Operation Procedures table
    :title: tilte of the procedure
    :content: content of the procedure
    :content_html: content in html format for MARKDOWN
    """
    __tablename__ = 'procedures'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)
    content_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    # FK, establish relationship with user table
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    @staticmethod
    def on_changed_content(target, value, oldvalue, initiator):
        """
        Function to invoke as the content of the procedure is updated/changed
        """
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i',
                        'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p', 'table',
                        'thead', 'tbody', 'tfoot']
        target.content_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, strip=True))


# listener of SQLAlchemy
db.event.listen(LabProcedure.content, 'set', LabProcedure.on_changed_content)


class Clinic(db.Model):
    """
    Create a clinic table
    :clinic_code_name: Special and unique code name for each clinic
    :clinic_full_name: Clinic full name
    :added_by: users id who enter the clinic to db
    :update_ts: timestamp of last update
    """
    __tablename__ = 'clinics'
    id = db.Column(db.Integer, primary_key=True, index=True)
    clinic_code_name = db.Column(db.String(5), unique=True)
    clinic_full_name = db.Column(db.String(128))
    added_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    update_ts = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='ordering_location', lazy='dynamic')

    def __repr__(self):
        return "Clinic Info: {}, {}".format(self.clinic_full_name, self.clinic_code_name)


class Provider(db.Model):
    """
    Create a table for Provider/Physician
    :degree: Provider degree title such MD/MBBS/PA
    :is_active: boolean to check if provider is still active
    """
    __tablename__ = 'providers'
    id = db.Column(db.Integer, primary_key=True)
    pro_first_name = db.Column(db.String(64), nullable=False)
    pro_last_name = db.Column(db.String(64), nullable=False)
    pro_middle_name = db.Column(db.String(64), nullable=False)
    added_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    update_ts = db.Column(db.DateTime(), default=datetime.utcnow)
    degree = db.Column(db.Enum(ProviderDegree, name="degree"))
    is_active = db.Column(db.Boolean, default=True)
    orders = db.relationship('Order', backref='ordering_provider', lazy='dynamic')

    def __repr__(self):
        return "Provider : {} {}".format(self.pro_first_name, self.pro_last_name)


class Patient(db.Model):
    """
    Create a table for Patient Demographic data
    """
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    pat_first_name = db.Column(db.String(64), nullable=False)
    pat_last_name = db.Column(db.String(64), nullable=False)
    pat_middle_name = db.Column(db.String(64), nullable=False)
    birth_date = db.Column(db.DateTime(), nullable=False)
    gender = db.Column(db.Enum(Gender, name="gender"))
    registered_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    update_ts = db.Column(db.DateTime(), default=datetime.utcnow, index=True)
    orders = db.relationship('Order', backref='donor', lazy='dynamic')

    def __repr__(self):
        return "Patient : {} {}".format(self.pat_first_name, self.pat_last_name)

    def get_patient_fullname(self):
        """
        function to get patient full name
        """
        return self.pat_first_name + " " + self.pat_middle_name + " " + self.pat_last_name

    def age(self):
        """
        function to get patient age from birth_date
        """
        return calculate_age(self.birth_date)

    def to_json(self):
        """
        Patient data in dictionary format to dump as JSON data
        Userful for DataTable
        """
        json_patient = {
            'id': self.id,
            'full_name': self.get_patient_fullname(),
            'dob': self.birth_date.strftime("%A %d. %B %Y"),
            'age': self.age(),
            'gender': self.gender.name,
            'registered': self.update_ts,
        }
        return json_patient


class Order(db.Model):
    """
    Create a table for Patient's Lab testing order
    :order_fluid_type: Enum data, specifies the type of Body Fluid for lab testing
    :order_name: name of the test for this order eg CBD, FLUID CELL COUNT
    :order_comment: addition comment for the order
    :order_loc_id: clinic location that originated the order
    :order_provider: Provider who ordered the test
    """
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_fluid_type = db.Column(db.Enum(FluidType, name="type"))
    order_name = db.Column(db.Enum(OrderName, name="req"))
    order_comment = db.Column(db.String())
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    order_loc_id = db.Column(db.Integer, db.ForeignKey('clinics.id'), nullable=False)
    order_provider = db.Column(db.Integer, db.ForeignKey("providers.id"), nullable=False)
    samples = db.relationship('Sample', backref='order', lazy='dynamic')
    events = db.relationship('Event', backref='order', lazy='dynamic')

    def __repr__(self):
        return "Order ID: {} for  {}".format(self.id, self.donor)

    def to_json(self):
        """
        Order data in dictionary format to dump as JSON data
        Userful for dataTable
        """
        patient = self.donor
        provider = self.ordering_provider
        e = self.events.all()
        events = {each.event_detail.name: each.event_ts for each in e}
        status = True if self.samples.count() == 1 else False
        if status:
            sample_id = self.samples[0].id
        json_order = {
            'id': self.id,
            'patient': patient.get_patient_fullname(),
            'sample_type': self.order_fluid_type.value,
            'order_name': self.order_name.name,
            'events': events,
            'order_loc': self.ordering_location.clinic_code_name,
            'order_prov': provider.pro_first_name + " " + provider.pro_last_name + ", " + provider.degree.value,
            'status': status,
            'sample_id': sample_id if status else None
        }
        return json_order

    def order_events_json(self):
        """
        Order Events data in dictionary format to dump as JSON data
        """
        e = self.events.all()
        events = {each.event_detail.name: [each.logger.id, each.logger.username, each.event_ts] for each in e}
        return events


class Event(db.Model):
    """
    Create table to log Events
    Each event associated with order is logged
    :order_id: Each event is associated with order
    :user_id : User who invoked the event
    :event_ts: timestamp of the event
    :event_detail: Detail of the event -eg Order Created, Sample received
    """
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    event_ts = db.Column(db.DateTime(), default=datetime.utcnow)
    event_detail = db.Column(db.Enum(OrderEventType, name="actions"))

    def __repr__(self):
        return "Event : {} for order ID {}".format(self.event_detail, self.order_id)


class Sample(db.Model):
    """
    Create a table for samples
    :wbc: White Blood cell count taken from instrument
    :rbc: Red Blood cell count taken from instrument
    :hgb: Hemoglobin count taken from instrument
    :hct: Hematocrit count taken from instrument
    :plt: Platelet count taken from instrument
    :status: boolean to capture if testing is complete or in progress
    :diff_report: After all images are analyzed, results are stored as Binary Text
    :pathrv: boolean to check if sample needs pathologists review
    """
    __tablename__ = 'samples'
    id = db.Column(db.Integer, primary_key=True)
    wbc = db.Column(db.Float, nullable=False)
    rbc = db.Column(db.Float, nullable=False)
    hgb = db.Column(db.Float, nullable=False)
    hct = db.Column(db.Integer, nullable=False)
    plt = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Boolean, default=False)
    diff_report = db.Column(db.PickleType)
    pathrv = db.Column(db.Boolean, default=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), unique=True, nullable=False)
    smears = db.relationship('Smear', backref='parent_sample', lazy='dynamic')
    path_reviews = db.relationship('PathReview', backref='smear', lazy='dynamic')
    comments = db.relationship('Comment', backref='sample', lazy='dynamic')

    def __repr__(self):
        return "Sample ID: {}".format(self.id)

    @staticmethod
    def get_pending_data():
        """
        Function to get current pending sample count
        """
        return Sample.query.filter_by(status=False).count()

    def to_json(self):
        """
        Function to convert patient data in dictionary
        """
        patient = self.order.donor
        provider = self.order.ordering_provider
        e = self.order.events.all()
        events = {each.event_detail.name: each.event_ts for each in e}
        json_sample = {
            'id': self.id,
            'patient': patient.get_patient_fullname(),
            'status': self.status,
            'provider': provider.pro_first_name + " " + provider.pro_last_name + ", " + provider.degree.value,
            'clinic': self.order.ordering_location.clinic_code_name,
            'events': events,
            'test': self.order.order_name.name
        }
        if self.pathrv:
            json_sample['path_status'] = self.path_reviews.scalar().status
        return json_sample


class Smear(db.Model):
    """
    Create a table Smear
    Each sample will have a blood smear
    :instrument_type: instrument that will scan the slide - eg CELLAVISION
    :sample_id: each smear belongs to a sample
    """
    __tablename__ = 'smears'
    id = db.Column(db.Integer, primary_key=True)
    instrument_type = db.Column(db.Enum(InstrumentType, name="instrument"))
    sample_id = db.Column(db.Integer, db.ForeignKey('samples.id'), nullable=False)
    images = db.relationship('CellImage', backref='smear', lazy='dynamic')
    morphologies = db.relationship(
        'BloodMorphology', cascade='all, delete-orphan', backref='blood_smears')

    def __repr__(self):
        return "Smear: {} {}".format(self.id, self.sample_id)


class CellImage(db.Model):
    """
    Create a table images,
    each row represent a single image of White Blood Cells
    :imag: image of a white blood cell
    :nucleated_cell_class: index number of Blood Cells, default = 0 = unidentified cell
    """
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.String(30), nullable=False)
    nucleated_cell_class = db.Column(db.Integer, default=0)

    smear_id = db.Column(db.Integer, db.ForeignKey('smears.id'), nullable=False)


class Comment(db.Model):
    """
    Create a table comments
    can add additional comment to the sample
    :sample_id: each  comment correspond to a sample id
    :comment: comment text
    :auther_id: user id who wrote the comment
    """
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    sample_id = db.Column(db.Integer, db.ForeignKey('samples.id'))
    comment = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return "Additonal: {} {}".format(self.smear_id, self.comment)


class PathReview(db.Model):
    """
    Create a table reviews
    Some sample will need pathologist review
    :sample_id: id of the sample that required pathologist review
    :status: boolean value to check if review is done or in progress
    :review_for: message by technologist regarding what needs to be reviewed for pathologiest
    :review: final comment by patholgist after analyzing sample
    """
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    sample_id = db.Column(db.Integer, db.ForeignKey('samples.id'))
    status = db.Column(db.Boolean, default=False)
    review_for = db.Column(db.Text)
    review = db.Column(db.Text)

    def __repr__(self):
        return "Pathologist Review: {} {}".format(self.sample_id, self.review)

    @staticmethod
    def get_pending_data():
        """
        Function to calculate current pending pathologist reviews
        """
        return PathReview.query.filter_by(status=False).count()


class Morphology(db.Model):
    """
    Create a table for morphs
    Different morphology that can be reported for Blood Cells
    :cell_type: Different type of Blood cells - White Blood, Red Blood, Platelet
    :morph_name: Morphological discription
    :options: ###TODO#### This implies to Red Blood Cells, currenlty not implemented
    :author_id: user who created each morphology
    :morph_ts: timestamp for morph
    """
    __tablename__ = 'morphs'
    id = db.Column(db.Integer, primary_key=True)
    cell_type = db.Column(db.Enum(CellType, name="cells"))
    morph_name = db.Column(db.Text, nullable=False)
    options = db.Column(db.PickleType)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    morph_ts = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return "Morphology(%r, %r)" % (self.cell_type, self.morph_name)


class BloodMorphology(db.Model):
    """
    Create a table blood_morphologies
    Association table between table morphs and smears with additional columns
    :smear_id: smear id, primary key,
    :morph_id: morph id, primary key
    :scale: captures magnitude of severity eg- 1+, 2+, 3+.. used for Red Blood Cells
    """
    __tablename__ = "blood_morphologies"
    smear_id = db.Column(db.Integer, db.ForeignKey("smears.id"), primary_key=True)
    morph_id = db.Column(db.Integer, db.ForeignKey("morphs.id"), primary_key=True)
    # TODO # change degree to scale
    degree = db.Column(db.String(16))
    morphs = db.relationship(Morphology, lazy="joined")
