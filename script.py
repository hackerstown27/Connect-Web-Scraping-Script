import os
import pymongo
import requests
import time
from random import randint
from selenium import webdriver
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def gen_pass():
    password = ""
    for _ in range(8):
        password += str(randint(0, 9))
    return password


def web_auto(roll_no):
    roll_no = str(int(roll_no))
    browser = webdriver.Firefox()
    browser.get('https://erp.aktu.ac.in/')
    username = browser.find_element_by_id('txtUserId')
    password = browser.find_element_by_id("txtPassword")
    username.send_keys(roll_no)
    password.send_keys("AK"+roll_no[2:9]+"TU")

    while(True):
        time.sleep(2)
        if browser.title == "DashBoard (छात्र पोर्टल)":
            break

    browser.get("https://erp.aktu.ac.in/WebPages/StudentPortal/frmEditProfile.aspx")
    data = browser.find_element_by_id("ContentPlaceHolder1_dtlsViewStudentInformation").text
    data = data.split("\n")
    data.pop(1)
    fields = ["Name", "FatherName", "MotherName", "Gender", "DOB", "BloodGroup", "AddSession", 
    "AddSem", "Status", "Institute", "Course", "Branch", "Semester", "MobileNo", "Email", "Address", 
    "City_District", "State", "Country", "Pincode"]

    user_details = {}
    i = 0
    for row in data:
        index = row.index(")")
        user_details[fields[i]] = row[index+2:]
        i += 1

    user_details["AKTURollNo"] = browser.find_element_by_id("ContentPlaceHolder1_lblRollNo").text[11:]

    return user_details



client = pymongo.MongoClient(f"mongodb+srv://admin:{os.environ.get('DB_PASS')}@cluster0-aiymc.mongodb.net/hookup?retryWrites=true&w=majority")
db = client["hookup"]
accreqs = db["accreqs"]
userinfos = db["userinfos"]
result = list(accreqs.find({}))
for req in result:
    user_details = web_auto(req["rollNo"])
    userinfos.insert_one(user_details)
    url = 'http://localhost:3001/'
    password = gen_pass()
    myobj = {"username": user_details["Email"], "password": password}
    x = requests.post(url, data = myobj)
    message = Mail(
        from_email='Connect.GLBajaj@gmail.com',
        to_emails=user_details["Email"],
        subject='Connect - Thank You For Joing Us',
        html_content=f'Thank You For Joining Us,<br><br>We Hope You Will Have Great Experience On Our Platform<br><br>Your Account Has Been Verified And Credentials Are Given Below:<br><br><strong>UserName: {user_details["Email"]}<br>Password: {password}</strong><br><br>Thank You,<br><br>From Connect Team'
    )
    try:
        sg = SendGridAPIClient(api_key=os.environ.get('SEND_GRID_API'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)
    accreqs.delete_many({"rollNo": req["rollNo"]})
