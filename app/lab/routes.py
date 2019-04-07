import bleach
import pytz
import tzlocal
from flask import redirect, render_template, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from . import lab
from .forms import ProcedureForm, PatientForm, ClinicForm, OrderForm, MorphForm, CBDForm,\
    ProviderForm, DiffForm, UpdateClinicForm
from .. import db, database
from ..models import LabProcedure, Patient, Clinic, Order, CellImage, Morphology, BloodMorphology,\
    PathReview, Event, Sample, Provider, Smear
from ..utils import Privilege, privilege_required, admin_required, save_image, wbc_classification,\
    wbc_trial, smear_path_review, ResultOption, OrderEventType, wbc_exclusion, diff_pickle

# add procedure


@lab.route('/procedures/add', methods=['GET', 'POST'])
@login_required
@privilege_required(Privilege.MODERATE)
def add_procedure():
    """
    Route to display form to add a
    Standard Operating Procedure for Lab
    """
    form = ProcedureForm()
    if form.validate_on_submit():
        procedure = LabProcedure(title=form.title.data,
                                 content=form.procedure_content.data,
                                 author=current_user._get_current_object())
        database.create(procedure)
        flash('Added procedure', 'success')
        return redirect(url_for('lab.all_procedures'))
    return render_template('lab/procedures/add_procedure.html', form=form)


@lab.route('/procedures')
@login_required
@privilege_required(Privilege.VIEW)
def all_procedures():
    """
    Route to display list of all SOP
    """
    procedures = LabProcedure.query.order_by(LabProcedure.timestamp.desc()).all()
    return render_template('lab/procedures/procedures.html', procedures=procedures)


@lab.route('/procedures/<int:id>')
@login_required
@privilege_required(Privilege.VIEW)
def procedure(id):
    """
    Route to display single SOP
    """
    procedure = LabProcedure.query.get_or_404(id)
    return render_template('lab/procedures/procedure.html', procedure=procedure)


@lab.route('/procedures/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@privilege_required(Privilege.MODERATE)
def edit_procedure(id):
    """
    Route to edit a single procedure
    """
    procedure = LabProcedure.query.get_or_404(id)
    form = ProcedureForm()
    if form.validate_on_submit():
        procedure.title = form.title.data
        procedure.content = form.procedure_content.data
        database.update(procedure)
        flash('Procedure has been updated!', 'success')
        return redirect(url_for('lab.procedure', id=procedure.id))
    form.title.data = procedure.title
    form.procedure_content.data = procedure.content
    return render_template('lab/procedures/edit_procedure.html', procedure=procedure, form=form)


@lab.route('/clinics/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_clinic():
    """
    Route to a new clinic location
    """
    form = ClinicForm()
    if form.validate_on_submit():
        clinic = Clinic(clinic_code_name=form.code_name.data,
                        clinic_full_name=form.name.data,
                        added_by=current_user.id)
        database.create(clinic)
        flash('Clinic has been added', 'success')
        return redirect(url_for('main.index'))
    return render_template('lab/clinics/add_clinic.html', form=form)


@lab.route('/clinics')
@login_required
@privilege_required(Privilege.VIEW)
def all_clinics():
    """
    Route to display all clinics
    """
    clinics = Clinic.query.all()
    return render_template('lab/clinics/clinics.html', clinics=clinics)


@lab.route('/clinics/<int:id>')
@login_required
@privilege_required(Privilege.VIEW)
def clinic(id):
    """
    Route to display single clinic detail information
    """
    clinic = Clinic.query.get_or_404(id)
    # Better way to do following #
    patients = db.session.query(Patient).join(Order, Clinic).filter(Clinic.id == clinic.id).distinct(Patient.id).all()
    return render_template('lab/clinics/clinic.html', clinic=clinic, patients=patients)


@lab.route('/clinics/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_clinic(id):
    """
    Route to edit a clinic data
    """

    clinic = Clinic.query.get_or_404(id)
    form = UpdateClinicForm(clinic=clinic)
    if form.validate_on_submit():
        clinic.clinic_code_name = form.code_name.data
        clinic.clinic_full_name = form.name.data
        database.update(clinic)
        flash('clinic has been updated!', 'success')
        return redirect(url_for('lab.clinic', id=clinic.id))
    form.name.data = clinic.clinic_full_name
    form.code_name.data = clinic.clinic_code_name
    return render_template('lab/clinics/edit_clinic.html', clinic=clinic, form=form)


@lab.route('/providers/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_provider():
    """
    Route to add new provider
    """
    form = ProviderForm()
    if form.validate_on_submit():
        provider = Provider(pro_first_name=form.f_name.data,
                            pro_last_name=form.l_name.data,
                            pro_middle_name=form.m_name.data,
                            degree=form.degree.data,
                            added_by=current_user.id)
        database.create(provider)
        flash('Provider has been added', 'success')
        return redirect(url_for('lab.all_providers'))
    return render_template('lab/providers/add_provider.html', form=form)


@lab.route('/providers')
@login_required
@privilege_required(Privilege.VIEW)
def all_providers():
    """
    Route to display all providers
    """
    providers = Provider.query.all()
    return render_template('lab/providers/providers.html', providers=providers)


@lab.route('/providers/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@privilege_required(Privilege.CREATE)
def edit_provider(id):
    """
    Route to edit provider information
    """
    provider = Provider.query.get_or_404(id)
    form = ProviderForm()
    if form.validate_on_submit():
        provider.pro_first_name = form.f_name.data,
        provider.pro_last_name = form.l_name.data,
        provider.pro_middle_name = form.m_name.data,
        provider.degree = form.degree.data
        database.update(provider)
        flash('Provider data has been updated!', 'success')
        return redirect(url_for('lab.all_providers'))
    elif request.method == 'GET':
        form.f_name.data = provider.pro_first_name
        form.l_name.data = provider.pro_last_name
        form.m_name.data = provider.pro_middle_name
        form.degree.data = provider.degree.name
    return render_template('lab/providers/add_provider.html', provider=provider, form=form)


@lab.route('/patients/add', methods=['GET', 'POST'])
@login_required
@privilege_required(Privilege.CREATE)
def add_patient():
    """
    Route to add a new patient
    """
    form = PatientForm()
    if form.validate_on_submit():
        patient = Patient(pat_first_name=form.f_name.data,
                          pat_last_name=form.l_name.data,
                          pat_middle_name=form.m_name.data,
                          birth_date=form.dob.data,
                          gender=form.gender.data,
                          registered_by=current_user.id)
        database.create(patient)
        flash('Patient has been added', 'success')
        return redirect(url_for('lab.patient', id=patient.id))
    return render_template('lab/patients/add_patient.html', form=form)


@lab.route('/patients/<int:id>', methods=['GET', 'POST'])
@login_required
@privilege_required(Privilege.VIEW)
def patient(id):
    """
    Route to display single patient information
    """
    patient = Patient.query.get_or_404(id)
    age = patient.age()
    return render_template('lab/patients/patient.html', patient=patient,
                           age=age)


@lab.route('/patients')
@login_required
@privilege_required(Privilege.VIEW)
def all_patients():
    """
    Route to dispaly all patients
    Patients data will be pulled using
    ajax as a json object
    """
    return render_template('lab/patients/patients.html')


@lab.route('/patients/json')
@login_required
@privilege_required(Privilege.VIEW)
def json_patients():
    """
    Route to retrive patient data as JSON
    """
    patients = Patient.query.all()
    json_patients = jsonify({'data': [patient.to_json() for patient in patients]})
    return json_patients


@lab.route('/patients/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@privilege_required(Privilege.CREATE)
def edit_patient(id):
    """
    Route to edit patient demographic data
    """
    patient = Patient.query.get_or_404(id)
    form = PatientForm()
    if form.validate_on_submit():
        patient.pat_first_name = form.f_name.data,
        patient.pat_middle_name = form.m_name.data,
        patient.pat_last_name = form.l_name.data,
        patient.birth_date = form.dob.data,
        patient.gender = form.gender.data
        database.update(patient)
        flash('Patient data has been updated!', 'success')
        return redirect(url_for('lab.patient', id=patient.id))
    elif request.method == 'GET':
        form.f_name.data = patient.pat_first_name
        form.m_name.data = patient.pat_middle_name
        form.l_name.data = patient.pat_last_name
        form.dob.data = patient.birth_date
        form.gender.data = patient.gender.name
    return render_template('lab/patients/edit_patient.html', patient=patient, form=form)


@lab.route('/patients/<int:id>/add_order', methods=['GET', 'POST'])
@login_required
@privilege_required(Privilege.CREATE)
def add_order(id):
    """
    Route to add new order to a patient
    """
    patient = Patient.query.get_or_404(id)
    form = OrderForm()
    if form.validate_on_submit():
        order = Order(donor=patient,
                      order_loc_id=form.location.data,
                      order_provider=form.provider.data,
                      order_fluid_type=form.order_fluid_type.data,
                      order_name=form.order_name.data,
                      order_comment=form.order_comment.data)
        database.flush()
        database.create((Event(order_id=order.id, user_id=current_user.id, event_detail=OrderEventType.CREATED)))
        flash('Sample has been add', 'success')
        return redirect(url_for('lab.patient', id=patient.id))
    return render_template('lab/orders/add_order.html', patient=patient, form=form)


@lab.route('/orders/all')
@login_required
@privilege_required(Privilege.VIEW)
def all_orders():
    """
    Route to display all patient orders in db
    Data will be pulled as JSON by AJAX
    """
    return render_template('lab/orders/orders.html', find_order='all')


@lab.route('/orders/pending')
@login_required
@privilege_required(Privilege.VIEW)
def pending_orders():
    """
    Route to display all patient pending orders in db
    ie- order is added to db but sample is yet to be added
    Data will be pulled as JSON by AJAX
    """
    return render_template('lab/orders/orders.html', find_order='pending')


@lab.route('/orders/json/<string:status>')
@login_required
@privilege_required(Privilege.VIEW)
def json_orders(status):
    """
    Route to retrive orders data as JSON object
    """
    if status == 'pending':
        orders = Order.query.filter(Order.samples == None)
    else:
        orders = Order.query.all()
    json_orders = jsonify({'data': [order.to_json() for order in orders]})
    return json_orders


@lab.route('/orders/<int:id>/add_sample', methods=['GET', 'POST'])
@login_required
@privilege_required(Privilege.CREATE)
def add_sample(id):
    """
    Route to add a sample to the order created before
    TODO - add rollback()
    """
    order = Order.query.get_or_404(id)
    if order.samples.count() != 0:
        flash('Sample already exitst for this order', 'info')
        return redirect(url_for('lab.sample', id=order.samples[0].id))
    form = CBDForm()
    if form.validate_on_submit():
        sample = Sample(wbc=form.wbc.data,
                        rbc=form.rbc.data,
                        hct=form.hct.data,
                        hgb=form.hgb.data,
                        plt=form.plt.data,
                        order_id=order.id)
        database.create(sample)
        smear = Smear(instrument_type=form.instrument.data,
                      sample_id=sample.id)
        e1 = Event(order_id=order.id, user_id=current_user.id, event_detail=OrderEventType.RECEIVED_SAMPLE)
        database.create_all([e1, smear])
        if form.images.data:
            pay_load = []
            for image in request.files.getlist('images'):
                wbc_file = save_image(image)
                pay_load.append(CellImage(smear_id=smear.id, img=wbc_file))
            pay_load.append(Event(order_id=order.id, user_id=current_user.id, event_detail=OrderEventType.RECEIVED_SMEAR))
            database.create_all(pay_load)
        return redirect(url_for('lab.sample', id=sample.id))
    return render_template('lab/samples/add_sample.html', form=form, order=order)


@lab.route('/samples/<int:id>')
@login_required
@privilege_required(Privilege.VIEW)
def sample(id):
    """
    Route to display single sample
    """
    sample = Sample.query.get_or_404(id)
    donor = sample.order.donor
    e = sample.order.events.all()
    # e2 = e[0].event_ts
    local = tzlocal.get_localzone()
    events = {each.event_detail.name: {'ts': pytz.utc.localize(each.event_ts, is_dst=None).astimezone(local), 'tech': each.user_id} for each in e}
    return render_template('lab/samples/sample.html', sample=sample, donor=donor, events=events)


@lab.route('/smears/<int:id>')
@login_required
@privilege_required(Privilege.CREATE)
def smear_images(id):
    """
    Route to display all images uploaded for each smear
    This is used mostly as a verification that images were indeed
    uploaded to db.
    """
    smear = Smear.query.get_or_404(id)
    return render_template('lab/samples/images.html', smear=smear, donor=smear.parent_sample.order.donor,
                           sample=smear.parent_sample)


@lab.route('/smears/<int:id>/diff', methods=['GET', 'POST'])
@login_required
@privilege_required(Privilege.UPDATE)
def sample_diff(id):
    """
    Route to perform the differential on blood cells
    """
    smear = Smear.query.get_or_404(id)
    sample = smear.parent_sample
    classification = wbc_classification()
    morph = Morphology.query.order_by(Morphology.morph_name.asc()).all()
    wbc = [w for w in morph if w.cell_type.name == 'WBC']
    checked = [each.morphs.id for each in smear.morphologies]
    include = [classification[i] for i in range(len(classification)) if i not in wbc_exclusion()]
    pathrv_status = smear.parent_sample.path_reviews.first() if sample.pathrv else False
    form = DiffForm()
    if form.validate_on_submit():
        if sample.status:
            flash('Sample was already validated', 'danger')
        else:
            cell_tuple = smear.images.with_entities(CellImage.nucleated_cell_class,
                                                    db.func.count(CellImage.id)).group_by(CellImage.nucleated_cell_class).all()
            morph_list = [each.morphs.morph_name for each in smear.morphologies]
            get_diff_pickle = diff_pickle(sample.wbc, cell_tuple)
            get_diff_pickle['morph'] = morph_list
            # update sample db
            sample.diff_report = get_diff_pickle
            sample.status = True
            e = Event(order_id=sample.order.id, user_id=current_user.id, event_detail=OrderEventType.SMEAR_ANALYZED)
            if smear_path_review() in morph_list:
                path_event = Event(order_id=sample.order.id, user_id=current_user.id, event_detail=OrderEventType.PATHRV)
                sample.pathrv = True
                database.create_all([sample, e, path_event])
            else:
                database.create_all([sample, e])
            flash('Diff is completed.' 'success')
        return redirect(url_for('lab.sample', id=sample.id))
    return render_template('lab/samples/diff.html', smear=smear, include=include,
                           classification=classification, wbc=wbc, checked=checked,
                           trial=wbc_trial(), donor=smear.parent_sample.order.donor, sample=sample,
                           review=smear_path_review(), pathrv=pathrv_status, form=form)


@lab.route('/samples/diff_value', methods=['GET'])
@login_required
@privilege_required(Privilege.UPDATE)
def sample_temp_diff():
    """
    Route to change blood cell classification
    """
    cell_id = request.args.get("id")
    cell_class = request.args.get("box")
    class_list = wbc_classification()
    i = class_list.index(cell_class)
    if cell_class in class_list:
        img = CellImage.query.filter_by(id=cell_id).first()
        img.nucleated_cell_class = class_list.index(cell_class)
        database.commit()
        return str(i)
    return None


@lab.route('/samples/morph_value', methods=['GET'])
@login_required
@privilege_required(Privilege.UPDATE)
def sample_temp_morph():
    """
    Route to add/update/delete morphology
    """
    m = int(request.args.get("m"))
    s = int(request.args.get("s"))
    r = request.args.get("r")
    # TODO following will be uncommented after adding Red Blood Cell
    # c = request.args.get("c")
    # degree = request.args.get("degree")
    smear = Smear.query.get(s)
    morph = Morphology.query.get(m)
    if smear and morph:
        if morph.id not in [each.morphs.id for each in smear.morphologies]:
            smear.morphologies.append(BloodMorphology(morphs=morph, degree=None))
            database.update(smear)
            if morph.morph_name == smear_path_review():
                review4 = bleach.clean(r, strip=True)
                database.create(PathReview(sample_id=smear.parent_sample.id, review_for=review4))
            return 'success'
        else:
            d = BloodMorphology.query.filter_by(smear_id=smear.id, morph_id=morph.id).first()
            smear.morphologies.remove(d)
            # db.session.add(smear)
            database.update(smear)
            if morph.morph_name == smear_path_review():
                PathReview.query.filter_by(sample_id=smear.parent_sample.id).delete()
                database.commit()
        return 'already exists'
    return 'fail'


@lab.route('/samples/review_value', methods=['GET'])
@login_required
@privilege_required(Privilege.UPDATE)
def sample_temp_review():
    """
    Route to add pathology review to the sample
    """
    r = request.args.get("r")
    s = int(request.args.get("s"))
    pathrv = PathReview.query.filter_by(sample_id=s).first()
    if pathrv and not pathrv.status:
        pathrv.review = bleach.clean(r, strip=True)
        pathrv.status = True
        database.update(pathrv)
        database.create(Event(order_id=pathrv.smear.order.id, user_id=current_user.id, event_detail=OrderEventType.PATH_REVIEWED))
        return url_for('lab.sample', id=pathrv.sample_id)
    return 'fail'


@lab.route('/samples/json/<string:status>')
@login_required
@privilege_required(Privilege.VIEW)
def json_samples(status):
    """
    Route to extract sample data as JSON
    """

    if status == 'pending':
        samples = Sample.query.filter(Sample.status.is_(False))
    else:
        samples = Sample.query.all()
    json_samples = jsonify({'data': [sample.to_json() for sample in samples]})
    return json_samples


@lab.route('/samples/all')
@login_required
@privilege_required(Privilege.VIEW)
def all_samples():
    """
    Route to display all samples that were logged
    """
    return render_template('lab/samples/samples.html', find_sample='all')


@lab.route('/samples/pending')
@login_required
@privilege_required(Privilege.VIEW)
def pending_samples():
    """
    Route to display pending samples
    """
    return render_template('lab/samples/samples.html', find_sample='pending')


@lab.route('/json/pending')
@login_required
@privilege_required(Privilege.VIEW)
def pending():
    """
    Route to calcuate pending sample number
    return JSON object
    """
    s = Sample.get_pending_data()
    p = PathReview.get_pending_data()
    return jsonify([{'name': 'pending', 'data': [s, p]}])


@lab.route('/samples/reviews/json/<string:status>')
@login_required
@privilege_required(Privilege.UPDATE)
def json_reviews(status):
    """
    Route to extract sample pathrv data as JSON
    """
    if status == 'pending':
        paths = PathReview.query.filter(PathReview.status.is_(False))
    else:
        paths = PathReview.query.all()
    json_samples = jsonify({'data': [sample.smear.to_json() for sample in paths]})
    return json_samples


@lab.route('/reviews/all')
@login_required
@privilege_required(Privilege.UPDATE)
def all_reviews():
    """
    Route to display all samples that were logged
    """
    return render_template('lab/samples/reviews.html', find_review='all')


@lab.route('/reviews/pending')
@login_required
@privilege_required(Privilege.UPDATE)
def pending_reviews():
    """
    Route to display pending samples
    """
    return render_template('lab/samples/reviews.html', find_review='pending')


@lab.route('/orders/events/json/<int:id>')
@login_required
@privilege_required(Privilege.ADMIN)
def order_events(id):
    """
    Route to calcuate pending sample number
    return JSON object
    """
    o = Order.query.get_or_404(id)
    return jsonify({o.id: o.order_events_json()})


@lab.route('/morphology/add', methods=['GET', 'POST'])
@login_required
@privilege_required(Privilege.MODERATE)
def add_morphology():
    """
    Route to add new morphology
    """
    form = MorphForm()
    if form.validate_on_submit():
        morph = Morphology(cell_type=form.cell_type.data,
                           morph_name=form.morphology.data,
                           options={'option-' + str(k): ResultOption(k).name for k in form.options.data},
                           author=current_user._get_current_object())
        database.create(morph)
        flash('Added morph', 'success')
        return redirect(url_for('lab.add_morphology'))
    return render_template('lab/morphs/add_morphology.html', form=form)


@lab.route('/morphologies')
@login_required
@privilege_required(Privilege.VIEW)
def all_morphologies():
    """
    Route to dispaly all morphologies
    """
    morphologies = Morphology.query.order_by(Morphology.cell_type.desc()).all()
    return render_template('lab/morphs/morphs.html', morphologies=morphologies)
