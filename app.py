import logging
import random
import time
import webbrowser
import mechanicalsoup
from getpass import getpass
import argparse
from itertools import count
import sys
import requests
import webview
from pyvirtualdisplay import Display
from flask import Flask, render_template, request, session, url_for, make_response
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities, ActionChains
from selenium.webdriver.android.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from werkzeug.utils import redirect
import pymysql.cursors
from PyWebRunner import WebRunner
import getpass
from flask_cors import CORS, cross_origin

app = Flask(__name__)
app.secret_key = 'your secret key'

db = pymysql.connect("localhost", "root", "root", "flask_auth")
cursor = db.cursor()

# driver = webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub',desired_capabilities={'browserName': 'internet explorer', 'javascriptEnabled': True})

driver = webdriver.Firefox()
wait = WebDriverWait(driver, 2)
actionChains = ActionChains(driver)
# driver.get('http://127.0.0.1:5000/login')
# webbrowser.open('')
# driver.execute_script("window.open('');")
# action = ActionChains(driver)


CORS(app,
     allow_headers=(
         'x-requested-with',
         'content-type',
         'accept',
         'origin',
         'authorization',
         'x-csrftoken',
         'withcredentials',
         'cache-control',
         'cookie',
         'session-id',
     ),
     supports_credentials=True)
username = ''
logging.basicConfig(level=logging.INFO)

@app.route('/login', methods=['GET', 'POST'])
def login():
    global username
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        email = request.form['username']
        password = request.form['password']
        username = request.form['username']

        cursor.execute('SELECT * FROM Users WHERE password = %s AND email = %s ', (password, email))
        Users = cursor.fetchone()
        cursor.execute('SELECT * FROM admin WHERE username = %s AND password = %s ', (username, password))
        admin = cursor.fetchone()
        cursor.execute('SELECT * FROM newuser WHERE username = %s AND password = %s ', (username, password))
        newuser = cursor.fetchone()
        cursor.execute('SELECT * FROM newusers2 WHERE username = %s AND password = %s ', (username, password))
        newuser2 = cursor.fetchone()

        if Users:
            session['loggedin'] = True
            return redirect('/main')
        elif admin:
            session['loggedin'] = True
            return redirect('/admin')
        elif newuser:
            session['loggedin'] = True
            return redirect('/user1')
        elif newuser2:
            session['loggedin'] = True
            return redirect('/user2')
        else:
            msg = 'Incorrect username/password!'

    return render_template('index.html', msg=msg)


print(username)


@app.route('/login/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        name = request.form['username']
        password = request.form['password']
        email = request.form['email']
        try:
            cursor.execute('INSERT INTO Users VALUES ( %s, %s, %s)', (name, password, email))
            db.commit()
        finally:
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'

    return render_template('register.html', msg=msg)


@app.route('/Branch', methods=['GET', 'POST'])
def Branch():
    global B_id
    cursor.execute("SELECT * FROM Branch")
    data = cursor.fetchall()
    if request.method == 'POST' and 'Branch_Name' in request.form and 'Branch_Desc' in request.form and 'KVM_ip' in request.form and 'Camera_ip' in request.form:

        B_Name = request.form['Branch_Name']
        KVM_ip = request.form['KVM_ip']
        Camera_ip = request.form['Camera_ip']
        B_Description = request.form['Branch_Desc']

        try:
            cursor.execute('INSERT INTO Branch SET B_Name=%s,B_Description=%s,KVM_ip=%s,Camera_ip=%s',
                           (B_Name, B_Description, KVM_ip, Camera_ip))
            db.commit()
        except Exception as er:
            print(er)
    elif request.method == 'POST' and 'id' in request.form:
        usr = request.form['id']
        cursor.execute('SELECT * FROM Branch WHERE B_Name = %s  ', (usr))
        id = cursor.fetchall()
        for row in id:
            B_id = row[0]
    elif request.method == 'POST' and 'Branch_Name1' in request.form:
        B_Name = request.form['Branch_Name1']
        KVM_ip = request.form['KVM_ip1']
        Camera_ip = request.form['Camera_ip1']
        B_Description = request.form['Branch_Desc1']

        try:
            cursor.execute('UPDATE  Branch SET B_Name=%s,B_Description=%s,KVM_ip=%s,Camera_ip=%s WHERE id=%s',
                           (B_Name, B_Description, KVM_ip, Camera_ip, B_id))
            db.commit()
        except Exception as er:
            print(er)

    else:
        pass

    return render_template('branches.html', data=data)
def evaluate_js(window):
    time.sleep(15)
    result = window.evaluate_js(
        r"""
          var req = https.request({ 
      host: '106.51.98.92', 
      port: 443,
      path: '/',
      method: 'GET',
      rejectUnauthorized: false,
      requestCert: true,
      agent: false
    },
        """
    )


@app.route('/main', methods=['GET', 'POST'])
def main():

    Users = ''
    global user_id
    cursor.execute("SELECT * FROM newuser")
    data = cursor.fetchall()
    cursor.execute("SELECT * FROM newusers2")
    data2 = cursor.fetchall()
    cursor.execute("SELECT * FROM branches")
    branch = cursor.fetchall()
    cursor.execute("SELECT * FROM Branch")
    Checkbox = cursor.fetchall()
    if request.method == 'POST' and 'user' in request.form:
        username = request.form['user']
        email = request.form['email1']
        password = request.form['psw']
        check = request.form.getlist('check')
        KVM_usr = request.form['KVM_u']
        KVM_pass = request.form['KVM_p']
        Camera_usr = request.form['Camera_u']
        Camera_pass = request.form['Camera_p']
        Address = request.form['Address']
        Branchs = ','.join(check)
        try:
            cursor.execute(
                'INSERT  INTO newuser SET username=%s,password=%s,email=%s,Branchs=%s,KVM_usr=%s,KVM_pass=%s,Camera_usr=%s,Camera_pass=%s,Address=%s ',
                (username, password, email, Branchs, KVM_usr, KVM_pass, Camera_usr, Camera_pass, Address))
            db.commit()
        except Exception as er:
            print(er)
        finally:
            pass
    elif request.method == 'POST' and 'id' in request.form:
        usr = request.form['id']
        cursor.execute('SELECT * FROM newuser WHERE username = %s  ', (usr))
        id = cursor.fetchall()
        for row in id:
            user_id = row[0]
    elif request.method == 'POST' and 'user2' in request.form:
        username = request.form['user2']
        email = request.form['email']
        password = request.form['psw2']
        check = request.form.getlist('check')
        KVM_usr = request.form['KVM_u2']
        KVM_pass = request.form['KVM_p2']
        Camera_usr = request.form['Camera_u2']
        Camera_pass = request.form['Camera_p2']
        Address = request.form['Address2']
        Branchs = ','.join(check)
        try:
            cursor.execute(
                'UPDATE  newuser SET username=%s,password=%s,email=%s,Branchs=%s,KVM_usr=%s,KVM_pass=%s,Camera_usr=%s,Camera_pass=%s,Address=%s   WHERE id = %s  ',
                (username, password, email, Branchs, KVM_usr, KVM_pass, Camera_usr,
                 Camera_pass, Address, user_id))
            db.commit()
        except Exception as er:
            print(er)
        finally:
            pass

    return render_template('main.html', data=data, branch=branch, data2=data2, Users=Users, Checkbox=Checkbox)


@app.route('/view_branch', methods=['GET', 'POST'])
def view_branch():
    ButtonPressed = 0
    branchs = ''
    branch1 = ''
    branch2 = ''
    cursor.execute("SELECT * FROM newuser WHERE username = %s", (username))
    pwd = cursor.fetchall()
    for row in pwd:
        KVM_usr = row[5]
        KVM_pwd = row[6]
        camera_usr = row[7]
        camera_pwd = row[8]
    cursor.execute("SELECT * FROM Branch")
    branch = cursor.fetchall()
    for row in branch:
        if request.method == 'POST' and 'action' in request.form:
            try:
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, row[1])))
                wait.until(EC.presence_of_element_located((By.NAME, 'username'))).send_keys('administrator')
                # wait.until(EC.presence_of_element_located((By.NAME, 'password'))).send_keys("pass1234")
                elem = driver.find_element_by_name('password')
                elem.send_keys('aarthi')
                wait.until(EC.presence_of_element_located((By.NAME, 'login'))).click()
                elem = wait.until(EC.presence_of_element_located((By.ID, 'LIMG01')))
                actionChains.move_to_element(elem).double_click()
                driver.switch_to.default_content()
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, row[0])))
                wait.until(EC.presence_of_element_located((By.NAME, 'email'))).send_keys('support@betamonks.com')
                wait.until(EC.presence_of_element_located((By.NAME, 'password'))).send_keys('pass12!@')
                wait.until(EC.presence_of_element_located((By.NAME, 'login'))).click()
            except:
                pass
            finally:
                driver.switch_to.default_content()

        else:
            print('no')

    return render_template('view_branch.html', branchs=branchs, branch=branch, ButtonPressed=ButtonPressed,
                           branch1=branch1, branch2=branch2, username=username)


@app.route('/user1', methods=['GET', 'POST'])
def user1():
    ButtonPressed = 0
    KVM_usr = ''
    KVM_pwd = ''
    camera_usr = ''
    camera_pwd = ''
    ip = ''
    cursor.execute("SELECT * FROM newuser WHERE username = %s", (username))
    pwd = cursor.fetchall()
    for row in pwd:
        KVM_usr = row[5]
        KVM_pwd = row[6]
        camera_usr = row[7]
        camera_pwd = row[8]
    cursor.execute("SELECT Branchs FROM newuser WHERE username = %s", (username))
    branchs = cursor.fetchone()[0]
    split = branchs.split(',')
    list = []
    for row in split:
        cursor.execute("SELECT * FROM Branch WHERE B_Name = %s", (row))
        ip = cursor.fetchall()
        list.append(ip)
    for row in list:
        if request.method == 'POST' and 'action' in request.form:
            try:
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, row[0][1])))
                wait.until(EC.presence_of_element_located((By.NAME, 'username'))).send_keys(KVM_usr)
                # wait.until(EC.presence_of_element_located((By.NAME, 'password'))).send_keys("pass1234")
                elem = driver.find_element_by_name('password')
                elem.send_keys(KVM_pwd)
                wait.until(EC.presence_of_element_located((By.NAME, 'login'))).click()
                driver.switch_to.default_content()
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, row[0][0])))
                wait.until(EC.presence_of_element_located((By.NAME, 'email'))).send_keys(camera_usr)
                wait.until(EC.presence_of_element_located((By.NAME, 'password'))).send_keys(camera_pwd)
                wait.until(EC.presence_of_element_located((By.NAME, 'login'))).click()
            except:
                pass
            finally:
                driver.switch_to.default_content()

    return render_template('user1.html', branchs=branchs, ButtonPressed=ButtonPressed, ip=ip, list=list, split=split,
                           username=username)


@app.route('/user2', methods=['GET', 'POST'])
def user2():
    branchs = ''
    branch1 = ''
    branch2 = ''
    branch3 = ''
    branch4 = ''
    msg = ''
    cursor.execute("SELECT Branch1,Branch2,Branch3,Branch4 FROM newusers2 WHERE username = %s", (username))
    branch = cursor.fetchone()

    return render_template('user2.html', branch=branch, branch1=branch1, branch2=branch2, branch3=branch3,
                           branch4=branch4, username=username)


@app.route('/VADAPALANI')
def branch1():
    return redirect('https://106.51.98.92')


@app.route('/TAMBARAM')
@cross_origin()
def branch2():

    resp = make_response(redirect('http://106.51.98.92:88/'))  # here you could use make_response(render_template(...)) too
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    return resp


@app.route('/PORUR')
def branch3():
    return redirect('https://106.51.98.92')


@app.route('/ANNA_NAGAR')
def branch4():
    return redirect('http://128.199.224.128:8080/actionregister')


if __name__ == "__main__":
    app.run(port=80, debug=True,)


