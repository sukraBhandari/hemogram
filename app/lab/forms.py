from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, ValidationError,\
    FloatField, IntegerField, SelectMultipleField, HiddenField
from flask_wtf.file import FileField, FileAllowed
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length
from flask_pagedown.fields import PageDownField
from ..models import Clinic, Provider
from ..utils import Gender, CellType, ResultOption, FluidType, OrderName, ProviderDegree,\
    InstrumentType


class ProcedureForm(FlaskForm):
    """
    Form to add new standard operating provcedure
    for the lab
    """
    title = StringField('Title', validators=[DataRequired(), Length(0, 128)])
    procedure_content = PageDownField("Content goes here", validators=[DataRequired()])
    submit = SubmitField('Submit')


class MorphForm(FlaskForm):
    """
    Form to add Cells Morphology
    """
    cell_type = SelectField("Blood Cell Type", validators=[DataRequired()])
    morphology = StringField('Enter cell morphology', validators=[DataRequired()])
    options = SelectMultipleField("Morphology Options")
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(MorphForm, self).__init__(*args, **kwargs)
        self.cell_type.choices = [('', 'Select')]
        [self.cell_type.choices.append((each.name, each.value)) for each in CellType]
        self.options.choices = [('', 'Select')]
        [self.options.choices.append((each.value, each.name)) for each in ResultOption]


class ProviderForm(FlaskForm):
    """
    Form to add new Provider/Doctor/Nurses
    """
    f_name = StringField('First Name', validators=[DataRequired(), Length(1, 64)])
    m_name = StringField('Middle Name', validators=[DataRequired(), Length(1, 64)])
    l_name = StringField('Last Name', validators=[DataRequired(), Length(1, 64)])
    degree = SelectField('Provider Degree', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(ProviderForm, self).__init__(*args, **kwargs)
        self.degree.choices = [('', 'Select')]
        [self.degree.choices.append((choice.name, choice.value)) for choice in ProviderDegree]


class PatientForm(FlaskForm):
    """
    Form to add new Patient to database
    """
    f_name = StringField('First Name', validators=[DataRequired(), Length(1, 64)])
    m_name = StringField('Middle Name', validators=[DataRequired(), Length(1, 64)])
    l_name = StringField('Last Name', validators=[DataRequired(), Length(1, 64)])
    dob = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    gender = SelectField("Gender", validators=[DataRequired()])
    submit = SubmitField('Register')

    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)
        self.gender.choices = [('', 'Select')]
        [self.gender.choices.append((choice.name, choice.value.capitalize())) for choice in Gender]


class ClinicForm(FlaskForm):
    """
    Form to add new Test ordering location
    """
    code_name = StringField('Clinic Code Name', validators=[DataRequired(), Length(1, 5)])
    name = StringField('Clinica Full Name', validators=[DataRequired(), Length(1, 128)])
    submit = SubmitField('Add Clinic')

    def validate_code_name(self, code_name):
        if code_name.data:
            name = Clinic.query.filter_by(clinic_code_name=code_name.data).first()
            if name:
                raise ValidationError('That clinc code is taken')


class UpdateClinicForm(FlaskForm):
    """
    Form to add new Test ordering location
    """
    code_name = StringField('Clinic Code Name', validators=[DataRequired(), Length(1, 5)])
    name = StringField('Clinica Full Name', validators=[DataRequired(), Length(1, 128)])
    submit = SubmitField('Update Clinic')

    def __init__(self, clinic, *args, **kwargs):
        super(UpdateClinicForm, self).__init__(*args, **kwargs)
        self.clinic = clinic

    def validate_code_name(self, field):
        if field.data != self.clinic.clinic_code_name and Clinic.query.filter_by(clinic_code_name=field.data).first():
            raise ValidationError('Clinic code name is already taken.')


class OrderForm(FlaskForm):
    """
    Form to add new requisiton for a lab test
    """
    location = SelectField('Order Location', coerce=int)
    provider = SelectField('Proivder', coerce=int)
    order_fluid_type = SelectField('Fluid Type', validators=[DataRequired(), Length(1, 128)])
    order_name = SelectField('Order Name', validators=[DataRequired(), Length(1, 128)])
    order_comment = StringField('Comment')
    submit = SubmitField('Add Order')

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.location.choices = [(clinic.id, clinic.clinic_code_name) for clinic in Clinic.query.order_by(Clinic.clinic_code_name).all()]
        self.provider.choices = [(provider.id, provider.pro_first_name + ' ' + provider.pro_last_name)
                                 for provider in Provider.query.order_by(Provider.pro_last_name).all()]
        self.order_fluid_type.choices = [(fluid.name, fluid.value.capitalize()) for fluid in FluidType]
        self.order_name.choices = [(order.name, order.value.upper()) for order in OrderName]


class CBDForm(FlaskForm):
    """
    Form to add some lab data and images from the smear.
    """
    wbc = FloatField('WBC count', validators=[DataRequired()])
    rbc = FloatField('RBC count', validators=[DataRequired()])
    hct = IntegerField('Hematocrit', validators=[DataRequired()])
    hgb = FloatField('Hemoglobin', validators=[DataRequired()])
    plt = IntegerField('Platelet', validators=[DataRequired()])
    instrument = SelectField('Instrument', validators=[DataRequired(), Length(1, 128)])
    images = FileField('Images', validators=[FileAllowed(['jpg'])])
    submit = SubmitField('Add Sample')

    def __init__(self, *args, **kwargs):
        super(CBDForm, self).__init__(*args, **kwargs)
        self.instrument.choices = [(ins.name, ins.value.upper()) for ins in InstrumentType]


class DiffForm(FlaskForm):
    """
    Form to finalize the diff
    """
    diff_value = HiddenField('Diff Value')
    submit = SubmitField("Confirm")
