# import needed packages
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

#creates an instance of the Flask class
app = Flask(__name__)

# Configure the database path
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://meenu:tesla@localhost:3306/world'

#binds instance to a specific Flask application
db = SQLAlchemy(app)

# Two classes, Doctor and Review that holds information about each
class Doctor(db.Model):
    __tablename__ = 'doctor'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(500))
    #backref shows that there is link between the reviews and the doctors
    reviews = db.relationship('Review', backref='doctor', lazy='dynamic')


class Review(db.Model):
    __tablename__ = 'review'
    id = db.Column('id', db.Integer, primary_key=True)
    #foreign key connects doctor id to id in doctor class
    doctor_id = db.Column('doctor_id', db.Integer, db.ForeignKey('doctor.id'))
    description = db.Column('description', db.String(500))

# This fucntion gets all information about the doctors and creates new doctors
@app.route('/doctors', methods=['GET', 'POST'])
def doctor():
    #gets information about all the doctors
    if request.method == 'GET':

        doc_query=Doctor.query.all()
        output_list=[]
        rev=[]
        reviewlist=Review.query.all()
        # go through and get all the reviews
        for i in range(0,len(doc_query)):
            for j in range(0,len(reviewlist)):
                if doc_query[i].id==reviewlist[j].doctor_id:
                    rev.append({'id': reviewlist[j].id, 'doctor_id': reviewlist[j].doctor_id,'description': reviewlist[j].description})
            if len(rev)>0:
                output_list.append({'name': doc_query[i].name, 'id': doc_query[i].id, 'reviews': rev})
                rev=[]
            else:
                #if there are no reviews
                output_list.append({'name': doc_query[i].name, 'id': doc_query[i].id})

        return jsonify(output_list)
      
    #Create a doctor
    elif request.method == 'POST':
        request_data = request.get_json()
        doc=Doctor(name=request_data['doctor']['name']) 
        # Add the session and commit it to the database
        db.session.add(doc)
        db.session.commit()
        # if successfully added, a message will show up
        return jsonify({'Successfully created doctor':doc.name})
#This function list the specific review and deletes a doctor
@app.route('/doctors/<id>', methods=['GET', 'DELETE'])
def doctor_id(id):
    
    # List a specific doctor along with their reviews
    if request.method == 'GET':
        rev_list=[]
        output_list=[]
        doctor = Doctor.query.get(id)
        review=Review.query.filter_by(doctor_id=id).all()
        if len(review)>0:
            #gets all the reviews
            for i in range(0,len(review)):
                rev_list.append({'id':review[i].id,'doctor_id':review[i].doctor_id, 'description':review[i].description})
            
            output_list.append({'name':doctor.name,'id':doctor.id,'reviews':rev_list})
        elif doctor:
            #if no reviews exist
            output_list.append({'name':doctor.name,'id':doctor.id})
        return jsonify(output_list)
        
    #deletes a specific doctor
    elif request.method=='DELETE':
        doctor=Doctor.query.get(id)
        db.session.delete(doctor)
        db.session.commit()
        # when successfully deleted, a message shows up
        return jsonify('Successfully deleted doctor')
# This function adds a review to a doctor
@app.route('/doctors/<id>/reviews', methods=['POST'])
def review(id):
    des=request.get_json()   
    #checks for the format 
    if ('review' in des)and('description' in des['review']):
        #finds the proper id and adds review
        review=Review(doctor_id=id,description=des['review']['description'])
        db.session.add(review)
        db.session.commit()
        #when it is added successfully, a message shows up
        return jsonify('Added:',des['review']['description'])
    #if it is not able to be added
    return jsonify('Error!')
#This function deletes a specific review 
@app.route('/doctors/<d_id>/reviews/<r_id>', methods=['DELETE'])
def review_id(d_id,r_id): 
    if request.method=='DELETE':
        review=Review.query.filter_by(doctor_id=d_id,id=r_id).first()
        if review:
            db.session.delete(review)
            db.session.commit()
            #when deleted successfully, a message shows up
            return jsonify('deleted review successfully')
        #if it was unable to be deletd
        return jsonify('error deleting review')
        
#Main method
if __name__ == "__main__":
    app.run(debug=True)