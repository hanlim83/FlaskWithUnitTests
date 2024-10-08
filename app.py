from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__, static_folder='static', static_url_path='/')

if __name__ == '__main__':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://' + \
                                            'root:root' + \
                                            '@localhost:3306/is212_example'
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_size': 100,
                                               'pool_recycle': 280}
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

CORS(app)


class Person(db.Model):
    __tablename__ = 'person'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    title = db.Column(db.String(10))

    def to_dict(self):
        """
        'to_dict' converts the object into a dictionary,
        in which the keys correspond to database columns
        """
        columns = self.__mapper__.column_attrs.keys()
        result = {}
        for column in columns:
            result[column] = getattr(self, column)
        return result


class Doctor(Person):
    __tablename__ = 'doctor'

    id = db.Column(db.Integer, db.ForeignKey('person.id'), primary_key=True)
    reg_num = db.Column(db.String(15))
    hourly_rate = db.Column(db.Integer)

    def calculate_charges(self, num_mins):
        """
        Uses the doctor's hourly rate to determine how much
        a 'num_mins' length appointment should be charged.
        NB: an appointment shorter than 10 mins is charged
        as if it were 10 mins long.
        """
        if num_mins < 10:
            result = self.hourly_rate / 6
        else:
            result = self.hourly_rate * (num_mins / 60)
        return result


class Patient(Person):
    __tablename__ = 'patient'

    id = db.Column(db.Integer, db.ForeignKey('person.id'), primary_key=True)
    contact_num = db.Column(db.String(15))
    ewallet_balance = db.Column(db.Integer, default=0)

    def ewallet_topup(self, amount):
        """
        Tops up a patient's e-wallet account.
        'amount' must be positive.
        """
        if amount >= 0:
            self.ewallet_balance += amount
        else:
            raise Exception("Negative topups not allowed.")

    def ewallet_withdraw(self, amount):
        """
        Withdraws an 'amount' from the patient's e-wallet if
        there is sufficient balance.
        """
        if self.ewallet_balance >= amount:
            self.ewallet_balance -= amount
        else:
            raise Exception("Unable to withdraw: insufficient balance.")


class Consultation(db.Model):
    __tablename__ = 'consultation'

    id = db.Column(db.Integer, primary_key=True)
    diagnosis = db.Column(db.String(100))
    prescription = db.Column(db.String(30))
    charge = db.Column(db.Integer)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))

    def to_dict(self):
        """
        'to_dict' converts the object into a dictionary,
        in which the keys correspond to database columns
        """
        columns = self.__mapper__.column_attrs.keys()
        result = {}
        for column in columns:
            result[column] = getattr(self, column)
        return result


with app.app_context():
    db.create_all()


@app.route("/persons/<int:person_id>")
def person_by_id(person_id):
    person = db.session.execute(
                db.select(Person).
                filter_by(id=person_id)
             ).scalar_one_or_none()
    if person:
        return jsonify({
            "data": person.to_dict()
        }), 200
    else:
        return jsonify({
            "message": "Person not found."
        }), 404


@app.route("/doctors")
def doctors():
    search_name = request.args.get('name')
    if search_name:
        doctor_list = db.session.execute(
                         db.select(Doctor).
                         where(Doctor.name.contains(search_name))
                      ).scalars()
    else:
        doctor_list = db.session.execute(db.select(Doctor)).scalars()
    return jsonify(
        {
            "data": [doctor.to_dict() for doctor in doctor_list]
        }
    ), 200


@app.route("/doctors", methods=['POST'])
def create_doctor():
    data = request.get_json()
    if not all(key in data.keys() for
               key in ('name', 'title',
                       'reg_num', 'hourly_rate')):
        return jsonify({
            "message": "Incorrect JSON object provided."
        }), 500
    doctor = Doctor(**data)
    try:
        db.session.add(doctor)
        db.session.commit()
        return jsonify(doctor.to_dict()), 201
    except Exception:
        return jsonify({
            "message": "Unable to commit to database."
        }), 500


@app.route("/patients")
def patients():
    search_name = request.args.get('name')
    if search_name:
        patient_list = db.session.execute(
                         db.select(Patient).
                         where(Patient.name.contains(search_name))
                      ).scalars()
    else:
        patient_list = db.session.execute(db.select(Patient)).scalars()
    return jsonify(
        {
            "data": [patient.to_dict() for patient in patient_list]
        }
    ), 200


@app.route("/patients", methods=['POST'])
def create_patient():
    data = request.get_json()
    if not all(key in data.keys() for
               key in ('name', 'title',
                       'contact_num', 'ewallet_balance')):
        return jsonify({
            "message": "Incorrect JSON object provided."
        }), 500
    patient = Patient(**data)
    try:
        db.session.add(patient)
        db.session.commit()
        return jsonify(patient.to_dict()), 201
    except Exception:
        return jsonify({
            "message": "Unable to commit to database."
        }), 500


@app.route("/consultations")
def consultations():
    consultation_list = db.session.execute(db.select(Consultation)).scalars()
    return jsonify(
        {
            "data": [consultation.to_dict()
                     for consultation in consultation_list]
        }
    ), 200


@app.route("/consultations", methods=['POST'])
def create_consultation():
    data = request.get_json()
    if not all(key in data.keys() for
               key in ('doctor_id', 'patient_id',
                       'diagnosis', 'prescription', 'length')):
        return jsonify({
            "message": "Incorrect JSON object provided."
        }), 500

    # (1): Validate doctor
    try:
        doctor = db.session.execute(
                    db.select(Doctor).
                    filter_by(id=data['doctor_id'])
                 ).scalar_one()
    except Exception:
        return jsonify({
            "message": "Doctor not valid."
        }), 500

    # (2): Compute charges
    charge = doctor.calculate_charges(data['length'])

    # (3): Validate patient
    try:
        patient = db.session.execute(
                     db.select(Patient).
                     filter_by(id=data['patient_id'])
                 ).scalar_one()
    except Exception:
        return jsonify({
            "message": "Patient not valid."
        }), 500

    # (4): Subtract charges from patient's e-wallet
    try:
        patient.ewallet_withdraw(charge)
    except Exception:
        return jsonify({
            "message": "Patient does not have enough e-wallet funds."
        }), 500

    # (4): Create consultation record
    consultation = Consultation(
        diagnosis=data['diagnosis'], prescription=data['prescription'],
        doctor_id=data['doctor_id'], patient_id=data['patient_id'],
        charge=charge
    )

    # (5): Commit to DB
    try:
        db.session.add(consultation)
        db.session.commit()
        return jsonify(consultation.to_dict()), 201
    except Exception:
        return jsonify({
            "message": "Unable to commit to database."
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
