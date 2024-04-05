from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///car_services.sqlite'
db = SQLAlchemy(app)
app.app_context().push()
# تولید کد رهگیری با طول ۸ رقم
def generate_tracking_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


# جداول شامل سرویس و وسیله نقلیه و قرار ملاقات 

class Service(db.Model):
 id = db.Column(db.Integer, primary_key=True)
 name = db.Column(db.String(100), nullable=False)
 description = db.Column(db.Text, nullable=True)

class Vehicle(db.Model):
 id = db.Column(db.Integer, primary_key=True)
 model = db.Column(db.String(70), nullable=False)
 year = db.Column(db.Integer, nullable=False)

class Appointment(db.Model):
 id = db.Column(db.Integer, primary_key=True)
 service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
 vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
 appointment_date = db.Column(db.String(100), nullable=False)
 warranty_code = db.Column(db.String(100), nullable=False)
 service_description = db.Column(db.String(100), nullable=False)
 full_name = db.Column(db.String(100), nullable=False)
 phone_number = db.Column(db.String(100), nullable=False)
 tracking_code = db.Column(db.String(100), nullable=False)
 status = db.Column(db.String(100), default="Pending") #Approved Denied
 
 service = db.relationship('Service', backref=db.backref('appointments', lazy=True))
 vehicle = db.relationship('Vehicle', backref=db.backref('appointments', lazy=True))

# class Tracking(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
#     service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
#     service_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     notes = db.Column(db.Text)

#     vehicle = db.relationship('Vehicle', backref=db.backref('service_history', lazy=True))
#     service = db.relationship('Service', backref=db.backref('service_history', lazy=True))


# Create the database tables

def create_tables():
    db.create_all()


create_tables()

# اطلاعات رزرو (نمونه)
reservations = [
    {'tracking_code': 'ABC123', 'full_name': 'علی احمدی', 'phone_number': '09123456789', 'brand': 'پژو', 'model': '۲۰۶', 'year': '۱۳۹۹', 'warranty_code': '123456', 'service_description': 'تعویض روغن و فیلتر هوا'}
]

# صفحه اصلی
@app.route('/')
def index():
 return render_template('index.html')
# صفحه‌ی خدمات
@app.route('/services')
def services():
 services = Service.query.all()
 return render_template('services.html', services=services)

@app.route('/service/create', methods=['POST'])
def service_create():
    name = request.form.get('name')
    description = request.form.get('description')
    service = Service(name=name, description=description)
    db.session.add(service)
    db.session.commit()
    
    return redirect(url_for('services'))
# صفحه‌ی وسایل نقلیه
@app.route('/vehicles')
def vehicles():
 vehicles = Vehicle.query.all()
 return render_template('vehicles.html', vehicles=vehicles)

@app.route('/vehicle/create', methods=['POST'])
def vehicle_create():
    model = request.form.get('model')
    year = request.form.get('year')
    vehicle = Vehicle(model=model, year=year)
    db.session.add(vehicle)
    db.session.commit()
    
    return redirect(url_for('vehicles'))
    
# صفحه‌ی قرار ملاقات‌ها
@app.route('/appointments', methods=['GET', 'POST'])
def appointments():
    if request.method == 'POST':
        service_id = request.form['service_id']
        vehicle_id = request.form['vehicle_id']
        appointment_date = request.form['appointment_date']
        warranty_code = request.form['warranty_code']
        service_description = request.form['service_description']
        full_name = request.form['full_name']  # نام و نام خانوادگی
        phone_number = request.form['phone_number']  # شماره تماس
        
        # انجام پردازش‌های مربوط به رزرو خدمات
        
        
         # تولید کد رهگیری
        tracking_code = generate_tracking_code()
        
        appointment = Appointment(service_id=service_id, vehicle_id=vehicle_id, appointment_date=appointment_date, warranty_code=warranty_code, service_description=service_description, full_name=full_name, phone_number=phone_number, tracking_code=tracking_code)
        db.session.add(appointment)
        db.session.commit()

        # انتقال کاربر به صفحه تایید رزرو
        return render_template('confirmation.html', tracking_code=tracking_code)

    services = Service.query.all()
    vehicles = Vehicle.query.all()
    return render_template('appointments.html', services=services, vehicles=vehicles)


@app.route('/confirmation/<tracking_code>')
def confirmation(tracking_code):
    appointment = Appointment.query.filter_by(tracking_code=tracking_code).first()
    appointment.status = "Approved"
    
    db.session.commit()
    
    return redirect(url_for("admin_view"))

@app.route('/denied/<tracking_code>')
def denied(tracking_code):
    appointment = Appointment.query.filter_by(tracking_code=tracking_code).first()
    appointment.status = "Denied"
    
    db.session.commit()
    
    return redirect(url_for("admin_view"))


@app.route('/tracking', methods=['GET', 'POST'])
def tracking():
    if request.method == 'POST':
        tracking_code = request.form['tracking_code']
        reservation = Appointment.query.filter_by(tracking_code=tracking_code).first()
        if reservation is None:
            error = "this tracking code was not true"
            return render_template('tracking.html', error=error)
        return render_template('tracking.html', reservation=reservation)
    
    return render_template('tracking.html')

@app.route('/admin')
def admin_view():
   
   appointments = Appointment.query.all()
   return render_template('admin.html', appointments=appointments)


if __name__ == '__main__':
 db.create_all()
 app.run(debug=True)