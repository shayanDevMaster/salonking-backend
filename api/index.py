from flask import Flask, request, jsonify
from firebase_admin import credentials, db, initialize_app
import json
import random
from datetime import datetime, timedelta
import pytz
import re
import os

# Initialize Flask app
app = Flask(__name__)

# Load Firebase credentials from environment variable
firebase_credentials = os.environ.get('FIREBASE_CREDENTIALS')
if not firebase_credentials:
    raise ValueError("FIREBASE_CREDENTIALS environment variable not set")

cred = credentials.Certificate(json.loads(firebase_credentials))

initialize_app(cred, {
    'databaseURL': 'https://salon-booking-7a936-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# Enable CORS for specific origins (allow local development and your deployed frontend)
@app.after_request
def apply_cors(response):
    # response.headers['Access-Control-Allow-Origin'] = 'http://127.0.0.1:5501'  # Allow local development
    response.headers['Access-Control-Allow-Origin'] = '*'  # Allow local development
    # response.headers['Access-Control-Allow-Origin'] = 'https://shayanalone.github.io'  # Allow local development
    # response.headers['Access-Control-Allow-Origin'] = 'http://www.salonking.shop'
    # For production, replace with your frontend URL (e.g., 'https://your-frontend.vercel.app')
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# ///////////////////////////////////////////



class FeeHistory:
    def __init__(self, record_Id , class_number , dueDate, payDate, purpose, amount, status):
        self.record_Id = record_Id # as string
        self.class_number = class_number # as string
        self.dueDate = dueDate # as string
        self.payDate = payDate # as string
        self.purpose = purpose  # as string
        self.amount = amount # as int
        self.status = status # as string

    def to_dict(self):
        return {
            "record_Id": self.record_Id,
            "class_number": self.class_number,
            "dueDate": self.dueDate,
            "payDate": self.payDate,
            "purpose": self.purpose,
            "amount": self.amount,
            "status": self.status
        }
class CustomeFeeRecords:
    def __init__(self, record_Id , class_number , dueDate, payDate, purpose, amount, status):
        self.record_Id = record_Id # as string
        self.class_number = class_number # as string
        self.dueDate = dueDate # as string
        self.payDate = payDate # as string
        self.purpose = purpose  # as string
        self.amount = amount # as int
        self.status = status # as string

    def to_dict(self):
        return {
            "record_Id": self.record_Id,
            "class_number": self.class_number,
            "dueDate": self.dueDate,
            "payDate": self.payDate,
            "purpose": self.purpose,
            "amount": self.amount,
            "status": self.status
        }


class Student:
    def __init__(self, class_number, roll_number, name , password , parentName, address, contactNumber, feesHistory):
        self.class_number = class_number
        self.roll_number = roll_number
        self.name = name
        self.password = password
        self.parentName = parentName
        self.address = address
        self.contactNumber = contactNumber
        self.FeesHistory = feesHistory

    def to_dict(self):
        return {
            "class": self.class_number,
            "rollNumber": self.roll_number,
            "name": self.name,
            "parentName": self.parentName,
            "address": self.address,
            "contactNumber": self.contactNumber,
            "FeesHistory": [fee.to_dict() for fee in self.FeesHistory]
        }


class DetailedMonthlyIncome:
    def __init__(self , month, totalStudent, feesCollection_pkr, pendingFees_pkr, collectionRate):
        self.month = month
        self.totalStudent = totalStudent
        self.feesCollection_pkr = feesCollection_pkr
        self.pendingFees_pkr = pendingFees_pkr
        self.collectionRate = collectionRate

    def to_dict(self):
        return {
            "month": self.month,
            "totalStudent": self.totalStudent,
            "feesCollection_pkr": self.feesCollection_pkr,
            "pendingFees_pkr": self.pendingFees_pkr,
            "collectionRate": self.collectionRate
        }

class PaymentProceess_RESULT:
    def __init__(self, paidFees_Record, TotalPayAmmounrt):
        self.TotalPayAmmounrt = TotalPayAmmounrt
        self.paidFees_Record = paidFees_Record

    def to_dict(self):
        return {
            "TotalPayAmmounrt": self.TotalPayAmmounrt,
            "paidFees_Record": [fee.to_dict() for fee in self.paidFees_Record]
        }

@app.route("/payAdmin_StudentPay", methods=["POST", "OPTIONS"])
def return_StudentPay_Complete():
    if request.method == "OPTIONS":
        return jsonify({}), 204

    return jsonify({
        "status": "success",
    })
    
@app.route("/payAdmin_StudentPay", methods=["POST", "OPTIONS"])
def payAdmin_StudentPay():
    if request.method == "OPTIONS":
        return jsonify({}), 204
    
    try:
        data = request.get_json()
        selected_fees = data.get("selectedFees", [])

        total_amount = 0
        paid_fees_record = []

        for fee in selected_fees:
            amount = int(fee.get("amount", 0))
            purpose = fee.get("purpose", "")
            due_date = fee.get("dueDate", "")
            fee_id = fee.get("record_Id", "")
            class_number = fee.get("class_number", "")

            total_amount += amount

            paid_fees_record.append({
                "amount": amount,
                "purpose": purpose,
                "dueDate": due_date,
                "payDate": due_date,  # or you can use current date
                "record_Id": fee_id,
                "class_number": class_number,
                "status": "Paid"
            })

        return jsonify({
            "status": "success",
            "data": {
                "pay_date" : datetime.now().strftime('%d-%m-%Y'),
                "TotalPayAmmounrt": total_amount,
                "paidFees_Record": paid_fees_record
            }
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500
@app.route("/payStudentPay", methods=["POST", "OPTIONS"])
def payStudentPay():
    if request.method == "OPTIONS":
        return jsonify({}), 204

    try:
        data = request.get_json()
        selected_fees = data.get("selectedFees", [])

        total_amount = 0
        paid_fees_record = []

        for fee in selected_fees:
            amount = int(fee.get("amount", 0))
            purpose = fee.get("purpose", "")
            due_date = fee.get("dueDate", "")
            fee_id = fee.get("record_Id", "")
            class_number = fee.get("class_number", "")

            total_amount += amount

            paid_fees_record.append({
                "amount": amount,
                "purpose": purpose,
                "dueDate": due_date,
                "payDate": due_date,  # or you can use current date
                "record_Id": fee_id,
                "class_number": class_number,
                "status": "Paid"
            })

        return jsonify({
            "status": "success",
            "data": {
                "pay_date" : datetime.now().strftime('%d-%m-%Y'),
                "TotalPayAmmounrt": total_amount,
                "paidFees_Record": paid_fees_record
            }
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500
@app.route("/editStudentData", methods=["POST", "OPTIONS"])
def editStudentData():
    if request.method == "OPTIONS":
        return jsonify({}), 204

    return jsonify({
        "status": "success",
    })
@app.route("/addNewStudent", methods=["POST", "OPTIONS"])
def addNewStudent():
    if request.method == "OPTIONS":
        return jsonify({}), 204

    return jsonify({
        "status": "success",
    })
@app.route("/getAdminAccess", methods=["POST", "OPTIONS"])
def getAdminAccess():
    if request.method == "OPTIONS":
        return jsonify({}), 204

    return jsonify({
        "status": "success",
    })

@app.route("/get_DetailedMonthlyIncome", methods=["POST", "OPTIONS"])
def get_DetailedMonthlyIncome():
    if request.method == "OPTIONS":
        return jsonify({}), 204

    totalStudent_list = [1001, 10021, 13001, 10014, 10501]
    collectionRate_list = [100, 90, 12, 32, 32]
    pendingFees_pkr_list = [1200, 3100, 4500, 1000, 900]
    feesCollection_pkr_list = [8000, 9000, 4000, 2000, 2500]
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November"]

    detailedMonthlyIncome = []

    for _ in range(random.randint(7, 30)):
        income = DetailedMonthlyIncome(
            month=random.choice(months),
            totalStudent=random.choice(totalStudent_list),
            feesCollection_pkr=random.choice(feesCollection_pkr_list),
            pendingFees_pkr=random.choice(pendingFees_pkr_list),
            collectionRate=random.choice(collectionRate_list)
        )

        detailedMonthlyIncome.append(income.to_dict())

    return jsonify({
        "status": "success",
        "data": detailedMonthlyIncome
    })
@app.route("/get_CustomeFees", methods=["POST", "OPTIONS"])
def get_CustomeFees():
    if request.method == "OPTIONS":
        return jsonify({}), 204

    purposes = ["Jan Fee", "Feb Fee", "Mar Fee", "Apr Fee", "May Fee", "Jun Fee", "Jul Fee", "Aug Fee", "Sep Fee", "Oct Fee", "Nov Fee", "Dec Fee"]
    customeFeeRecords = []
    for i in range(random.randint(7, 30)):
        due_date = (datetime.today() - timedelta(days=random.randint(30 , 100))).strftime("%Y-%m-%d")
        pay_date = (datetime.today() - timedelta(days=random.randint(20 , 50))).strftime("%Y-%m-%d") if random.choice([True, False]) else None
        fee = CustomeFeeRecords(
            record_Id=str(random.randint(100, 1000)),
            class_number=str(random.rangeint(1, 10)),
            dueDate=due_date,
            purpose=random.choice(purposes),
            amount=random.choice([1500, 2000, 2500]),
        )
        customeFeeRecords.append(fee.to_dict())

    return jsonify({
        "status": "success",
        "data": customeFeeRecords
    })


@app.route("/get_AllStudentData", methods=["POST", "OPTIONS"])
def get_AllStudentData():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Preflight

    # Random mock data sources
    names = ["Aliyaan Shahid", "Ahmed Raza", "Fatima Noor", "Sara Ahmed"]
    parents = ["Shahid Khan", "Raza Ali", "Umer Farooq", "Kashif Mehmood"]
    addresses = ["Lahore", "Karachi", "Islamabad", "Faisalabad"]
    contacts = ["03001234567", "03111234567", "03211234567", "03331234567"]
    purposes = ["Jan Fee", "Feb Fee", "Mar Fee", "Apr Fee", "May Fee", "Jun Fee", "Jul Fee", "Aug Fee", "Sep Fee", "Oct Fee", "Nov Fee", "Dec Fee"]
    pass_word = "qww"
    students = []
    for s in range(random.randint(200, 300)):

        # Random fee history for each student
        feesHistory = []
        for i in range(random.randint(10, 30)):
            due_date = (datetime.today() - timedelta(days=random.randint(30, 90))).strftime("%Y-%m-%d")
            pay_date = (datetime.today() - timedelta(days=random.randint(5, 29))).strftime("%Y-%m-%d") if random.choice([True, False]) else None
            fee = FeeHistory(
                record_Id=str(random.randint(100, 1000)),
                class_number=str(random.randint(1, 11)),
                dueDate=due_date,
                payDate=pay_date,
                purpose=random.choice(purposes),
                amount=random.choice([1500, 2000, 2500]),
                status="Paid" if pay_date else "Unpaid"
            )
            feesHistory.append(fee)

        # Random student data
        student = Student(
            class_number=str(random.randint(6, 10)),
            roll_number=str(random.randint(1, 50)),
            name=random.choice(names),
            password=pass_word,
            parentName=random.choice(parents),
            address=random.choice(addresses),
            contactNumber=random.choice(contacts),
            feesHistory=feesHistory
        )

        students.append(student.to_dict())

    return jsonify({
        "status": "success",
        "data": students
    })


@app.route("/get_LoginStudentData", methods=["POST", "OPTIONS"])
def get_LoginStudentData():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content

    data = request.get_json()
    
    Class = data.get("class")
    roll = data.get("rollNumber")
    password = data.get("password")

    # Random mock data
    names = ["Aliyaan Shahid", "Ahmed Raza", "Fatima Noor", "Sara Ahmed"]
    parents = ["Shahid Khan", "Raza Ali", "Umer Farooq", "Kashif Mehmood"]
    addresses = ["Lahore", "Karachi", "Islamabad", "Faisalabad"]
    contacts = ["03001234567", "03111234567", "03211234567", "03331234567"]
    purposes = ["Jan Fee", "Feb Fee", "Mar Fee", "Apr Fee", "May Fee", "Jun Fee", "Jul Fee", "Aug Fee", "Sep Fee", "Oct Fee", "Nov Fee", "Dec Fee"]
    status_list = ["Paid", "Unpaid"]
    pass_word = "1234567"
    
    # Generate random fee history (2–3 records)
    feesHistory = []
    if(roll == "0"):
        for i in range(random.randint(7, 30)):
            due_date = (datetime.today() - timedelta(days=random.randint(30 , 100))).strftime("%Y-%m-%d")
            pay_date = (datetime.today() - timedelta(days=random.randint(20 , 50))).strftime("%Y-%m-%d") if random.choice([True, False]) else None
            fee = FeeHistory(
                record_Id=str(random.randint(100, 1000)),
                class_number=str(random.choice([5])),
                dueDate=due_date,
                payDate=pay_date,
                purpose=random.choice(purposes),
                amount=random.choice([1500, 2000, 2500]),
                status="Paid" if pay_date else "Unpaid"
            )
            feesHistory.append(fee)
    elif(roll == "1"):
        for i in range(random.randint(7, 30)):
            due_date = (datetime.today() - timedelta(days=random.randint(300, 400))).strftime("%Y-%m-%d")
            pay_date = (datetime.today() - timedelta(days=random.randint(290, 390))).strftime("%Y-%m-%d") if random.choice([True, False]) else None
            fee = FeeHistory(
                record_Id=str(random.randint(100, 1000)),
                class_number=str(random.choice([6,6,6,4,4,6,6,6])),
                dueDate=due_date,
                payDate=pay_date,
                purpose=random.choice(purposes),
                amount=random.choice([1500, 2000, 2500]),
                status="Paid" if pay_date else "Unpaid"
            )
            feesHistory.append(fee)
    else:
        for i in range(random.randint(7, 30)):
            due_date = (datetime.today() - timedelta(days=random.randint(10, 400))).strftime("%Y-%m-%d")
            pay_date = (datetime.today() - timedelta(days=random.randint(5, 300))).strftime("%Y-%m-%d") if random.choice([True, False]) else None
            fee = FeeHistory(
                record_Id=str(random.randint(100, 1000)),
                class_number=str(random.choice([1,1,1,1,2,2,2,2,2,4,4,4,4,5,5,5,5,5,6,6,6,6])),
                dueDate=due_date,
                payDate=pay_date,
                purpose=random.choice(purposes),
                amount=random.choice([1500, 2000, 2500]),
                status="Paid" if pay_date else "Unpaid"
            )
            feesHistory.append(fee)
    # Create random student object
    student = Student(
        class_number=Class,
        roll_number=roll,
        name=random.choice(names),
        password=pass_word,
        parentName=random.choice(parents),
        address=random.choice(addresses),
        contactNumber=random.choice(contacts),
        feesHistory=feesHistory
    )

    return jsonify({
        "status": "success",
        "data": student.to_dict()
    })



@app.route("/getAdmin_LoginStudentData", methods=["POST", "OPTIONS"])
def getAdmin_LoginStudentData():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content

    data = request.get_json()
    
    Class = data.get("class")
    roll = data.get("rollNumber")
    password = data.get("password")

    # Random mock data
    names = ["Aliyaan Shahid", "Ahmed Raza", "Fatima Noor", "Sara Ahmed"]
    parents = ["Shahid Khan", "Raza Ali", "Umer Farooq", "Kashif Mehmood"]
    addresses = ["Lahore", "Karachi", "Islamabad", "Faisalabad"]
    contacts = ["03001234567", "03111234567", "03211234567", "03331234567"]
    purposes = ["Jan Fee", "Feb Fee", "Mar Fee", "Apr Fee", "May Fee", "Jun Fee", "Jul Fee", "Aug Fee", "Sep Fee", "Oct Fee", "Nov Fee", "Dec Fee"]
    status_list = ["Paid", "Unpaid"]
    pass_word = "1234567"
    
    # Generate random fee history (2–3 records)
    feesHistory = []
    for i in range(random.randint(7, 30)):
        due_date = (datetime.today() - timedelta(days=random.randint(250, 500))).strftime("%Y-%m-%d")
        pay_date = (datetime.today() - timedelta(days=random.randint(250, 500))).strftime("%Y-%m-%d") if random.choice([True, False]) else None
        fee = FeeHistory(
            record_Id=str(random.randint(100, 1000)),
            class_number=str(random.choice([1,1,1,1,2,2,2,2,2,4,4,4,4,5,5,5,5,5,6,6,6,6])),
            dueDate=due_date,
            payDate=pay_date,
            purpose=random.choice(purposes),
            amount=random.choice([1500, 2000, 2500]),
            status="Paid" if pay_date else "Unpaid"
        )
        feesHistory.append(fee)

    # Create random student object
    student = Student(
        class_number=Class,
        roll_number=roll,
        name=random.choice(names),
        password=pass_word,
        parentName=random.choice(parents),
        address=random.choice(addresses),
        contactNumber=random.choice(contacts),
        feesHistory=feesHistory
    )

    return jsonify({
        "status": "success",
        "data": student.to_dict()
    })




















































#//////////////////////////////////////////////////////

def is_valid_pakistani_phone_number(phone):
    phone = re.sub(r'\s|-', '', phone).strip()
    pak_phone_regex = r'^(0|\+92)[3][0-9]{9}$'
    valid_mobile_codes = [
        '300', '301', '302', '303', '304', '305', '306', '307', '308', '309',
        '310', '311', '312', '313', '314', '315', '316', '317', '318', '319',
        '320', '321', '322', '323', '324', '325', '326', '327', '328', '329',
        '330', '331', '332', '333', '334', '335', '336', '337', '338', '339',
        '340', '341', '342', '343', '344', '345', '346', '347', '348', '349',
        '360', '361', '362', '363', '364', '365', '366', '367', '368', '369'
    ]
    if not re.match(pak_phone_regex, phone):
        return False
    mobile_code = phone[3:6] if phone.startswith('+92') else phone[1:4]
    return mobile_code in valid_mobile_codes

@app.route("/getAllSalon", methods=["POST", "OPTIONS"])
def getAllSalon():
    ref = db.reference("salons")
    result = ref.get() or []
    # Create res_bookings with all fields except 'code' and 'id'
    # res_salons = [
    #     {key: value for key, value in salon.items() if key not in ["password"]}
    #     for salon in result
    # ]
    # Convert to list if result is a dictionary
    salons = list(result.values()) if isinstance(result, dict) else result
    # Filter out DeActive salons and exclude password field
    res_salons = [
        {key: value for key, value in salon.items() if key not in ["password"]}
        for salon in salons
        if isinstance(salon, dict) and salon.get("status") == "Active"
    ]
    return jsonify({"status": "success", "data": res_salons})
@app.route("/get_your_salon", methods=["POST", "OPTIONS"])
def get_your_salon():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content

    data = request.get_json()
    salon_index = data.get("salonIndex")
    salon_name = data.get("salonName")
    salon_password = data.get("salonPassword")

    # Validate required fields
    if not salon_name:
        return jsonify({
            "status": "failed",
            "salon_index": -1,
            "salon": None
        })
    if not salon_password:
        return jsonify({
            "status": "failed",
            "salon_index": -1,
            "salon": None
        })
    if salon_index == -1:
        return jsonify({
            "status": "failed",
            "salon_index": -1,
            "salon": None
        })

    try:
        # Step 1: Try to get salon by salon_index if provided
        if salon_index is not None:
            try:
                salon_index = int(salon_index)  # Ensure salon_index is an integer
                salon_ref = db.reference(f"salons/{salon_index}")
                salon = salon_ref.get()
                if salon and salon.get("salonName") == salon_name and salon.get("password") == salon_password:
                    if(salon.get("status") == "Active"):
                        return jsonify({
                            "status": "success",
                            "salon_index": salon_index,
                            "salon": salon
                        })
                    else:
                        return jsonify({
                            "status": "failed",
                            "salon_index": -1,
                            "salon": None
                        })
            except (ValueError, TypeError):
                # Invalid salon_index format, proceed to search by salonName
                pass

        # Step 2: Search all salons for matching salonName and password
        ref = db.reference("salons")
        salons = ref.get() or []  # Ensure result is a list

        salon_index = next((i for i, s in enumerate(salons) if s['salonName'] == salon_name and s['password'] == salon_password), -1)

        if salon_index >= 0:
            # Salon found
            salon = salons[salon_index]
            return jsonify({
                "status": "success",
                "salon_index": salon_index,
                "salon": salon
            })
        else:
            # Salon not found
            return jsonify({
                "status": "failed",
                "salon_index": -1,
                "salon": None
            })

    except Exception as e:
        return jsonify({
            "status": "failed",
            "error": str(e),
            "salon_index": -1,
            "salon": None
        }), 500


    except Exception as e:
        return jsonify({"status": "failed" , "error": str(e) , 
                        "salon_index": -1,
                        "salon": None})
    
@app.route("/save_your_salon_setting", methods=["POST", "OPTIONS"])
def save_your_salon_setting():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content
    data = request.get_json()
    
    # /////////// Checking Authorization /////////////
    salon_index = data.get("salonIndex")
    salonName = data.get("old_salonName")
    salon_password = data.get("old_salonPassword")

    # Validate required fields
    if not salonName:
        return jsonify({
            "status": "failed",
            "data": None
        })
    if not salon_password:
        return jsonify({
            "status": "failed",
            "data": None
        })
    if salon_index == -1:
        return jsonify({
            "status": "failed",
            "data": None
        })

    # Step 1: Try to get salon by salon_index if provided
    if salon_index is not None:
        try:
            salon_index = int(salon_index)  # Ensure salon_index is an integer
            salon_ref = db.reference(f"salons/{salon_index}")
            salon = salon_ref.get()
            i = 1
            if salon and salon.get("salonName") == salonName and salon.get("password") == salon_password:
                i = 0
            else:
                return jsonify({
                    "status": "failed",
                    "data": None
                })
        except (ValueError, TypeError):
            # Invalid salon_index format, proceed to search by salonName
            return jsonify({
                    "status": "failed",
                    "data": None
                })
            pass
    # ////////////////////////////////////////////
    
    
    try:
        # 
        salon_index = int(salon_index)  # Ensure salon_index is an integer
        salon_ref = db.reference(f"salons/{salon_index}")
        salon = salon_ref.get()
        if salon and salon.get("salonName") == salonName and salon.get("password") == salon_password and salon.get("status") == "Active":
            newSalon = {
                "salonId" : salon.get("salonId"),
                "salonName" : data.get("salonName"),
                "ownerName" : data.get("ownerName"),
                "ownerNumber" : data.get("ownerNumber"),
                "password" : data.get("password"),
                "location" : data.get("location"),
                "isOverTime" : data.get("isOverTime"),
                "openTime" : data.get("openTime"),
                "closeTime" : data.get("closeTime"),
                "SeatCount" : data.get("SeatCount"),
                "breaks" : data.get("breaks"),
                "WholeServiceDiscounting" : data.get("WholeServiceDiscounting"),
                "services" : data.get("services"),
                "ownerImage" : data.get("ownerImage"),
                "salonImages" : data.get("salonImages"),
                "status": "Active"
            }
            ref = db.reference("salons/" + str(salon_index))
            ref.set(newSalon)

            return jsonify({
                "status": "success",
                "salon": newSalon
            })
        else:
            return jsonify({
                "status": "Your Salon is Delete or Not found",
                "salon": None
            })

    except Exception as e:
        return jsonify({"status": str(e) , "salon": None})

@app.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content
    data = request.get_json()
    salonName = data.get("salonName")
    salonPassword = data.get("salonPassword")
    if not salonName:
        return jsonify({"status": "Failed: Unkown Problem"}), 400
    if not salonPassword:
        return jsonify({"status": "Failed: Unkown Problem"}), 400
    try:
        ref = db.reference("salons")
        result = ref.get() or {}
        # ///////
        salon_index = next((i for i, s in enumerate(result) if s['salonName'] == salonName and s['password'] == salonPassword), -1)

        if salon_index >= 0:
            # logged
            return jsonify({"status": "success" , "salon_index": salon_index})
        else:
            # not found
            return jsonify({"status": "failed" , "salon_index": -1})

    except Exception as e:
        return jsonify({"status": "failed" , "error": str(e) , "salon_index": -1})

@app.route("/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content
    data = request.get_json()
    salonName = data.get("salonName")
    if not salonName:
        return jsonify({"error": "Missing salonName"}), 400
    try:
        # ///////
        if not data or "permissionCode" not in data:
            return jsonify({
                "status": "Missing permission code",
                "salon_index": -1,
                "salon": None
            }), 400

        # Retrieve permission code from Firebase
        # try:
        #     per_code = db.reference("Permission Code").get()
        #     if per_code is None:
        #         return jsonify({
        #             "status": "Permission code not configured in the system",
        #             "salon_index": -1,
        #             "salon": None
        #         }), 500
        # except Exception as e:
        #     return jsonify({
        #         "status": "Failed to retrieve permission code: " + str(e),
        #         "salon_index": -1,
        #         "salon": None
        #     }), 500

        # # Validate and compare permission codes
        # provided_code = data.get("permissionCode")
        # if not isinstance(provided_code, (str, int)) or not str(provided_code).strip():
        #     return jsonify({
        #         "status": "Invalid permission code format",
        #         "salon_index": -1,
        #         "salon": None
        #     }), 400

        # # Ensure both values are strings for comparison
        # if str(per_code).strip() != str(provided_code).strip():
        #     return jsonify({
        #         "status": "Incorrect permission code",
        #         "salon_index": -1,
        #         "salon": None
        #     }), 403
        # ///////
        ref = db.reference("salons")
        salons = ref.get() or {}
        # ///////
        salon_index = next((i for i, s in enumerate(salons) if s['salonName'] == salonName), -1)

        if salon_index == -1:
            # this salon not exists
            salon = {
                "salonId" : + str(random.randint(10000 , 50000)),
                "salonName" : data.get("salonName"),
                "ownerName" : data.get("ownerName"),
                "ownerNumber" : data.get("ownerNumber"),
                "password" : data.get("password"),
                "location" : data.get("location"),
                "isOverTime" : data.get("isOverTime"),
                "openTime" : data.get("openTime"),
                "closeTime" : data.get("closeTime"),
                "SeatCount" : data.get("SeatCount"),
                "breaks" : data.get("breaks"),
                "WholeServiceDiscounting" : data.get("WholeServiceDiscounting"),
                "services" : data.get("services"),
                "ownerImage" : data.get("ownerImage"),
                "salonImages" : data.get("salonImages"),
                "status": "Active"
            }
            # Get and increment next_salons_index
            index_ref = db.reference("next_salons_index")
            next_index = index_ref.get() or 0  # Default to 0 if not set

            # Append salon to Firebase list at next_index
            ref.child(str(next_index)).set(salon)

            # Increment next_salons_index for the next salon
            index_ref.set(next_index + 1)

            return jsonify({
                "status": "success",
                "salon_index": next_index,
                "salon": salon
            })
        else:
            return jsonify({"status": "Already exist this Salon Name" , "salon_index": -1 , "salon": None})
            

    except Exception as e:
        return jsonify({"status": "Failed: "+ str(e) , "salon_index": -1 , "salon": None})
    

@app.route("/getUserBookings", methods=["POST", "OPTIONS"])
def getUserBookings():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content
    data = request.get_json()
    deviceId = data.get("deviceId")
    if not deviceId:
        return jsonify({"error": "Missing deviceId"}), 400
    try:
        ref = db.reference("bookings")
        result = ref.get() or {}
        # ///////
        # Filter bookings where status is 'pending' and deviceId matches
        filtered_bookings = [
            booking for booking in (result.values() if isinstance(result, dict) else result)
            if isinstance(booking, dict) and booking.get("status") == "pending" and booking.get("deviceId") == deviceId
        ]

        return jsonify({"status": "success", "data": filtered_bookings})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/getSalonBookings", methods=["POST", "OPTIONS"])
def getSalonBookings():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content
    data = request.get_json()
    # /////////// Checking Authorization /////////////
    salon_index = data.get("salonIndex")
    salonName = data.get("salonName")
    salon_password = data.get("salonPassword")
    salonId = data.get("salonId")

    # Validate required fields
    if not salonId:
        return jsonify({
            "status": "failed",
            "data": None
        })
    # Validate required fields
    if not salonName:
        return jsonify({
            "status": "failed",
            "data": None
        })
    if not salon_password:
        return jsonify({
            "status": "failed",
            "data": None
        })
    if salon_index == -1:
        return jsonify({
            "status": "failed",
            "data": None
        })

    # Step 1: Try to get salon by salon_index if provided
    if salon_index is not None:
        try:
            salon_index = int(salon_index)  # Ensure salon_index is an integer
            salon_ref = db.reference(f"salons/{salon_index}")
            salon = salon_ref.get()
            if salon and salon.get("salonName") == salonName and salon.get("password") == salon_password:
                salon_index = 0
            else:
                return jsonify({
                    "status": "failed",
                    "data": None
                })
        except (ValueError, TypeError):
            # Invalid salon_index format, proceed to search by salonName
            return jsonify({
                    "status": "failed",
                    "data": None
                })
            pass
    # ////////////////////////////////////////////

    try:
        ref = db.reference("bookings")
        result = ref.get() or {}
        # ///////
        # Filter bookings where status is 'pending' and deviceId matches
        filtered_bookings = [
            booking for booking in (result.values() if isinstance(result, dict) else result)
            if isinstance(booking, dict) and booking.get("salonId") == salonId
        ]

        return jsonify({"status": "success", "data": filtered_bookings})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/getOnlyTime_SalonBookings", methods=["POST", "OPTIONS"])
def getOnlyTime_SalonBookings():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content
    data = request.get_json()
    
    salonId = data.get("salonId")
    if not salonId:
        return jsonify({"error": "Missing salonId"}), 400
    try:
        ref = db.reference("bookings")
        result = ref.get() or {}
        

        # Get today's date in the format "2025-06-12"
        today_date = datetime.now(pytz.timezone("Asia/Karachi")).strftime("%Y-%m-%d")
        tomorrow_date = (datetime.now(pytz.timezone("Asia/Karachi")) + timedelta(days=1)).strftime("%Y-%m-%d")

        # Filter bookings where status is 'pending', deviceId matches, and date is today or tomorrow
        filtered_bookings = [
            booking for booking in (result.values() if isinstance(result, dict) else result)
            if isinstance(booking, dict) and booking.get("salonId") == salonId and booking.get("status") == "pending" 
            and (booking.get("date") == today_date or booking.get("date") == tomorrow_date)
        ]
        # Create res_bookings with only time and time_take fields
        res_bookings = [
            {
                "time": booking.get("time", ""),
                "time_take": booking.get("time_take", 0)
            }
            for booking in filtered_bookings
        ]
        return jsonify({"status": "success", "data": res_bookings})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Booking Canceling:
@app.route("/user_cancel_booking", methods=["POST", "OPTIONS"])
def user_cancel_booking():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content
    data = request.get_json()
    deviceId = data.get("deviceId")
    booking_code = data.get("code")
    if not deviceId:
        return jsonify({"error": "Missing deviceId"}), 400
    try:
        ref = db.reference("bookings")
        result = ref.get() or []

        booking_index = next((i for i, s in enumerate(result) if s['deviceId'] == deviceId and s['status'] == "pending" and s['code'] == booking_code), -1)
        if(booking_index >= 0):
            ref = db.reference("bookings/" + str(booking_index) + "/status")
            ref.set("user canceled")

            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "Booking not found or already canceled."})
    except Exception as e:
        return jsonify({"status": "Failed: " + str(e)}), 500

# Baaad mai dekhta hu
@app.route("/user_cancel_allBooking", methods=["POST", "OPTIONS"])
def user_cancel_allBooking():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content
    data = request.get_json()
    deviceId = data.get("deviceId")
    if not deviceId:
        return jsonify({"error": "Missing deviceId"}), 400
    try:
        ref = db.reference("bookings")
        result = ref.get() or []

        b = 0
        c = 0
        for index, booking in enumerate(result):
            if booking.get("deviceId") == deviceId:
                ref = db.reference("bookings/" + str(b) + "/status")
                ref.set("user canceled")
                c += 1
            b += 1
        # 
        if(c > 0):
            return jsonify({"status": "success" , "count": c})
        else:
            return jsonify({"status": "Booking not found or already canceled." , "count": c})
    except Exception as e:
        return jsonify({"status": "Failed: " + str(e) , "count": 0}), 500


@app.route("/dash_cancel_booking", methods=["POST", "OPTIONS"])
def dash_cancel_booking():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content
    data = request.get_json()
    # /////////// Checking Authorization /////////////
    salon_index = data.get("salonIndex")
    salonName = data.get("salonName")
    salon_password = data.get("salonPassword")
    
    booking_code = data.get("code")
    salonId = data.get("salonId")

    # Validate required fields
    if not salonId:
        return jsonify({
            "status": "failed",
            "data": None
        })

    # Validate required fields
    if not salonName:
        return jsonify({
            "status": "failed",
            "data": None
        })
    if not salon_password:
        return jsonify({
            "status": "failed",
            "data": None
        })
    if salon_index == -1:
        return jsonify({
            "status": "failed",
            "data": None
        })

    # Step 1: Try to get salon by salon_index if provided
    if salon_index is not None:
        try:
            salon_index = int(salon_index)  # Ensure salon_index is an integer
            salon_ref = db.reference(f"salons/{salon_index}")
            salon = salon_ref.get()
            if salon and salon.get("salonName") == salonName and salon.get("password") == salon_password:
                salon_index = 0
            else:
                return jsonify({
                    "status": "failed",
                    "data": None
                })
        except (ValueError, TypeError):
            # Invalid salon_index format, proceed to search by salonName
            return jsonify({
                    "status": "failed",
                    "data": None
                })
            pass
    
    if not salonName:
        return jsonify({"error": "Missing salonName"}), 400
    try:
        ref = db.reference("bookings")
        result = ref.get() or []

        booking_index = next((i for i, s in enumerate(result) if s['salonId'] == salonId and s['status'] == "pending" and s['code'] == booking_code), -1)
        if(booking_index >= 0):
            ref = db.reference("bookings/" + str(booking_index) + "/status")
            ref.set("dash canceled")

            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "Booking not found or already canceled."})
    except Exception as e:
        return jsonify({"status": "Failed: " + str(e)}), 500
    
@app.route("/dash_cancel_allBooking", methods=["POST", "OPTIONS"])
def dash_cancel_allBooking():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content
    data = request.get_json()
    # /////////// Checking Authorization /////////////
    salon_index = data.get("salonIndex")
    salonName = data.get("salonName")
    salon_password = data.get("salonPassword")

    salonId = data.get("salonId")

    # Validate required fields
    if not salonId:
        return jsonify({
            "status": "failed",
            "data": None
        })
    # Validate required fields
    if not salonName:
        return jsonify({
            "status": "failed",
            "data": None
        })
    if not salon_password:
        return jsonify({
            "status": "failed",
            "data": None
        })
    if salon_index == -1:
        return jsonify({
            "status": "failed",
            "data": None
        })

    # Step 1: Try to get salon by salon_index if provided
    if salon_index is not None:
        try:
            salon_index = int(salon_index)  # Ensure salon_index is an integer
            salon_ref = db.reference(f"salons/{salon_index}")
            salon = salon_ref.get()
            if salon and salon.get("salonName") == salonName and salon.get("password") == salon_password:
                salon_index = 0
            else:
                return jsonify({
                    "status": "failed",
                    "data": None
                })
        except (ValueError, TypeError):
            # Invalid salon_index format, proceed to search by salonName
            return jsonify({
                    "status": "failed",
                    "data": None
                })
            pass
    # ////////////////////////////////////////////

    try:
        ref = db.reference("bookings")
        result = ref.get() or []

        b = 0
        c = 0
        for index, booking in enumerate(result):
            if booking.get("salonId") == salonId and booking.get("status") == "pending":
                ref = db.reference("bookings/" + str(b) + "/status")
                ref.set("dash canceled")
                c += 1
            b += 1
        # 
        if(c > 0):
            return jsonify({"status": "success" , "count": c})
        else:
            return jsonify({"status": "Booking not found or already canceled." , "count": c})
    except Exception as e:
        return jsonify({"status": "Failed: " + str(e) , "count": 0}), 500
    
# Compeleting Booking:
    
@app.route("/dash_complete_booking", methods=["POST", "OPTIONS"])
def dash_complete_booking():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content
    data = request.get_json()
    # /////////// Checking Authorization /////////////
    salon_index = data.get("salonIndex")
    salonName = data.get("salonName")
    salon_password = data.get("salonPassword")
    salonId = data.get("salonId")

    # Validate required fields
    if not salonId:
        return jsonify({
            "status": "failed",
            "data": None
        })
    if not salonName:
        return jsonify({
            "status": "failed",
            "data": None
        })
    if not salon_password:
        return jsonify({
            "status": "failed",
            "data": None
        })
    if salon_index == -1:
        return jsonify({
            "status": "failed",
            "data": None
        })

    # Step 1: Try to get salon by salon_index if provided
    if salon_index is not None:
        try:
            salon_index = int(salon_index)  # Ensure salon_index is an integer
            salon_ref = db.reference(f"salons/{salon_index}")
            salon = salon_ref.get()
            if salon and salon.get("salonName") == salonName and salon.get("password") == salon_password:
                salon_index = 0
            else:
                return jsonify({
                    "status": "failed",
                    "data": None
                })
        except (ValueError, TypeError):
            # Invalid salon_index format, proceed to search by salonName
            return jsonify({
                    "status": "failed",
                    "data": None
                })
            pass
    # ////////////////////////////////////////////
    booking_code = data.get("code")

    try:
        ref = db.reference("bookings")
        result = ref.get() or []

        booking_index = next((i for i, s in enumerate(result) if s['salonId'] == salonId and s['status'] == "pending" and s['code'] == booking_code), -1)
        if(booking_index >= 0):
            ref = db.reference("bookings/" + str(booking_index) + "/status")
            ref.set("completed")

            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "Booking not found or already canceled."})
    except Exception as e:
        return jsonify({"status": "Failed: " + str(e)}), 500
    
@app.route("/dash_complete_allBooking", methods=["POST", "OPTIONS"])
def dash_complete_allBooking():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content
    data = request.get_json()
    # /////////// Checking Authorization /////////////
    salon_index = data.get("salonIndex")
    salonName = data.get("salonName")
    salon_password = data.get("salonPassword")

    salonId = data.get("salonId")

    # Validate required fields
    if not salonId:
        return jsonify({
            "status": "failed",
            "data": None
        })
    # Validate required fields
    if not salonName:
        return jsonify({
            "status": "failed",
            "data": None
        })
    if not salon_password:
        return jsonify({
            "status": "failed",
            "data": None
        })
    if salon_index == -1:
        return jsonify({
            "status": "failed",
            "data": None
        })

    # Step 1: Try to get salon by salon_index if provided
    if salon_index is not None:
        try:
            salon_index = int(salon_index)  # Ensure salon_index is an integer
            salon_ref = db.reference(f"salons/{salon_index}")
            salon = salon_ref.get()
            if salon and salon.get("salonName") == salonName and salon.get("password") == salon_password:
                salon_index = 0
            else:
                return jsonify({
                    "status": "failed",
                    "data": None
                })
        except (ValueError, TypeError):
            # Invalid salon_index format, proceed to search by salonName
            return jsonify({
                    "status": "failed",
                    "data": None
                })
            pass
    # ////////////////////////////////////////////

    try:
        ref = db.reference("bookings")
        result = ref.get() or []

        b = 0
        c = 0
        for index, booking in enumerate(result):
            if booking.get("salonId") == salonId and booking.get("status") == "pending":
                ref = db.reference("bookings/" + str(b) + "/status")
                ref.set("completed")
                c += 1
            b += 1
        # 
        if(c > 0):
            return jsonify({"status": "success" , "count": c})
        else:
            return jsonify({"status": "Booking not found or already canceled." , "count": c})
    except Exception as e:
        return jsonify({"status": "Failed: " + str(e) , "count": 0}), 500

# Before All time Bookings:
def time_to_minutes(time_str):
    # Split "10:00 PM" -> ["10:00", "PM"]
    time_part, period = time_str.split(' ')
    hours, minutes = map(int, time_part.split(':'))

    if period == 'PM' and hours != 12:
        hours += 12
    if period == 'AM' and hours == 12:
        hours = 0

    return hours * 60 + minutes

# Example values

@app.route("/dash_complete_allBeforeBooking", methods=["POST", "OPTIONS"])
def dash_complete_allBeforeBooking():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content
    data = request.get_json()
    # /////////// Checking Authorization /////////////
    salon_index = data.get("salonIndex")
    salonName = data.get("salonName")
    salon_password = data.get("salonPassword")

    salonId = data.get("salonId")

    # Validate required fields
    if not salonId:
        return jsonify({
            "status": "failed",
            "data": None
        })
    # Validate required fields
    if not salonName:
        return jsonify({
            "status": "failed",
            "data": None
        })
    if not salon_password:
        return jsonify({
            "status": "failed",
            "data": None
        })
    if salon_index == -1:
        return jsonify({
            "status": "failed",
            "data": None
        })

    # Step 1: Try to get salon by salon_index if provided
    if salon_index is not None:
        try:
            salon_index = int(salon_index)  # Ensure salon_index is an integer
            salon_ref = db.reference(f"salons/{salon_index}")
            salon = salon_ref.get()
            if salon and salon.get("salonName") == salonName and salon.get("password") == salon_password:
                salon_index = 0
            else:
                return jsonify({
                    "status": "failed",
                    "data": None
                })
        except (ValueError, TypeError):
            # Invalid salon_index format, proceed to search by salonName
            return jsonify({
                    "status": "failed",
                    "data": None
                })
            pass
    # ////////////////////////////////////////////

    try:
        ref = db.reference("bookings")
        result = ref.get() or []

        b = 0
        c = 0
        for index, booking in enumerate(result):
            if booking.get("salonId") == salonId and booking.get("status") == "pending":
                tomorrow_date = (datetime.now(pytz.timezone("Asia/Karachi")) + timedelta(days=1)).strftime("%Y-%m-%d")

                if booking.get("date") != tomorrow_date:
                    time = booking.get("time")
                    time_take = booking.get("time_take")
                    clean_time = time[:time.index('s')]

                    # Current time in minutes since midnight
                    now = datetime.now( pytz.timezone("Asia/Karachi") )
                    current_minutes = now.hour * 60 + now.minute

                    # Get today's date in the format "2025-06-05"
                    today_date = datetime.now(pytz.timezone("Asia/Karachi")).strftime("%Y-%m-%d")

                    # Comparison
                    if time_to_minutes(clean_time) + time_take < current_minutes or booking.get("date") != today_date:
                        ref = db.reference("bookings/" + str(b) + "/status")
                        ref.set("completed")
                        c += 1
            b += 1
        # 
        if(c > 0):
            return jsonify({"status": "success" , "count": c})
        else:
            return jsonify({"status": "Booking not found or already canceled." , "count": c})
    except Exception as e:
        return jsonify({"status": "Failed: " + str(e) , "count": 0}), 500

@app.route("/dash_cancel_allBeforeBooking", methods=["POST", "OPTIONS"])
def dash_cancel_allBeforeBooking():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content
    data = request.get_json()
    # /////////// Checking Authorization /////////////
    salon_index = data.get("salonIndex")
    salonName = data.get("salonName")
    salon_password = data.get("salonPassword")

    salonId = data.get("salonId")

    # Validate required fields
    if not salonId:
        return jsonify({
            "status": "failed",
            "data": None
        })
    # Validate required fields
    if not salonName:
        return jsonify({
            "status": "failed",
            "data": None
        })
    if not salon_password:
        return jsonify({
            "status": "failed",
            "data": None
        })
    if salon_index == -1:
        return jsonify({
            "status": "failed",
            "data": None
        })

    # Step 1: Try to get salon by salon_index if provided
    if salon_index is not None:
        try:
            salon_index = int(salon_index)  # Ensure salon_index is an integer
            salon_ref = db.reference(f"salons/{salon_index}")
            salon = salon_ref.get()
            if salon and salon.get("salonName") == salonName and salon.get("password") == salon_password:
                salon_index = 0
            else:
                return jsonify({
                    "status": "failed",
                    "data": None
                })
        except (ValueError, TypeError):
            # Invalid salon_index format, proceed to search by salonName
            return jsonify({
                    "status": "failed",
                    "data": None
                })
            pass
    # ////////////////////////////////////////////

    try:
        ref = db.reference("bookings")
        result = ref.get() or []

        b = 0
        c = 0
        for index, booking in enumerate(result):
            if booking.get("salonId") == salonId and booking.get("status") == "pending":
                
                tomorrow_date = (datetime.now(pytz.timezone("Asia/Karachi")) + timedelta(days=1)).strftime("%Y-%m-%d")

                if booking.get("date") != tomorrow_date:
                    time = booking.get("time")
                    time_take = booking.get("time_take")
                    clean_time = time[:time.index('s')]

                    # Current time in minutes since midnight
                    now = datetime.now( pytz.timezone("Asia/Karachi") )
                    current_minutes = now.hour * 60 + now.minute

                    # Get today's date in the format "2025-06-05"
                    today_date = datetime.now( pytz.timezone("Asia/Karachi") ).strftime("%Y-%m-%d")

                    # Comparison
                    if time_to_minutes(clean_time) + time_take < current_minutes  or booking.get("date") != today_date:
                        ref = db.reference("bookings/" + str(b) + "/status")
                        ref.set("dash canceled")
                        c += 1
            b += 1
        # 
        if(c > 0):
            return jsonify({"status": "success" , "count": c})
        else:
            return jsonify({"status": "Booking not found or already canceled." , "count": c})
    except Exception as e:
        return jsonify({"status": "Failed: " + str(e) , "count": 0}), 500


# Bookings System

@app.route("/bookAppointment", methods=["POST", "OPTIONS"])
def bookAppointment():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content
    data = request.get_json()
    try:
        
        customer_number = data.get("customerNumber")
        if(str(customer_number) != "0000"):
            if not customer_number or not is_valid_pakistani_phone_number(customer_number):
                return jsonify({"status": "failed", "message": "Invalid or missing customer phone number"}), 400
        
        bookings_ref = db.reference("bookings")

        # Get today's date in the format "2025-06-05"
        _time = data.get("time")

        date = datetime.now(pytz.timezone("Asia/Karachi")).strftime("%Y-%m-%d")
        # ye correct way hai ?
        if data.get("nextDayDate") == "1":
            date = (datetime.now(pytz.timezone("Asia/Karachi")) + timedelta(days=1)).strftime("%Y-%m-%d")

        # this salon not exists
        booking = {
            "salonId": data.get("salonId"),
            # "salonName": data.get("salonName"),
            # "ownerName": data.get("ownerName"),
            # "location": data.get("location"),
            "deviceId": data.get("deviceId"),
            "service": data.get("service"),
            "price": data.get("price"),
            "time": _time,
            "time_take": data.get("time_take"),
            "customerImage": data.get("customerImage"),
            "customerName": data.get("customerName"),
            "customerNumber": data.get("customerNumber"),
            "code": "BOOK:"+ str( random.randint(100 , 999) ),
            "date": date,
            "status": "pending",
        }
        # Get and increment next_salons_index
        index_ref = db.reference("next_boookings_index")
        next_index = index_ref.get() or 0  # Default to 0 if not set

        # Append booking to Firebase list at next_index
        bookings_ref.child(str(next_index)).set(booking)

        # Increment next_salons_index for the next booking
        index_ref.set(next_index + 1)

        return jsonify({
            "status": "success",
            "booking": booking
        })

    except Exception as e:
        return jsonify({"status": "Failed: " + str(e) , "booking": None})
@app.route("/getDefaultImages", methods=["POST", "OPTIONS"])
def getDefaultImages():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content
    try:
        ref = db.reference("defaultSalonImages")
        result = ref.get()
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ///////////////////////////////////////////
@app.route("/get", methods=["POST", "OPTIONS"])
def get():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content
    data = request.get_json()
    path = data.get("path")
    if not path:
        return jsonify({"error": "Missing path"}), 400
    try:
        ref = db.reference(path)
        result = ref.get()
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/set", methods=["POST", "OPTIONS"])
def set_data():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content
    data = request.get_json()
    path = data.get("path")
    value = data.get("value")
    if not path or value is None:
        return jsonify({"error": "Missing path or value"}), 400
    try:
        ref = db.reference(path)
        ref.set(value)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ///////////////////////////////////////////
@app.route("/update", methods=["POST", "OPTIONS"])
def update_data():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content
    data = request.get_json()
    path = data.get("path")
    value = data.get("value")
    if not path or not isinstance(value, dict):
        return jsonify({"error": "Missing path or value"}), 400
    try:
        ref = db.reference(path)
        ref.update(value)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/delete", methods=["POST", "OPTIONS"])
def delete_data():
    if request.method == "OPTIONS":
        return jsonify({}), 204  # Respond to preflight with 204 No Content
    data = request.get_json()
    path = data.get("path")
    if not path:
        return jsonify({"error": "Missing path"}), 400
    try:
        ref = db.reference(path)
        ref.delete()
        return jsonify({"status": "deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
