import sqlite3
import flask
from datetime import *

app = flask.Flask(__name__)

@app.route('/')
def home():
    return flask.render_template('index.html')

@app.route('/member_form')
def member_form():
     return flask.render_template('Add member.html')

@app.route('/member_added', methods=['POST'])
def member_added():
    Data = sqlite3.connect('hairdresser.db')
    name = flask.request.form['SU_Name']
    contact =flask.request.form['Contact']
    email = flask.request.form['Email']
    gender = flask.request.form['Gender']
    address = flask.request.form['Address']
    Data.execute('insert into Member (Name,Contact,Email,Gender,Address) values(?,?,?,?,?);',(name,contact,email,gender,address))
    Data.commit()
    Data.close()
    return flask.render_template('index.html')
@app.route('/Services')
def Services():
    return flask.render_template('service.html')
@app.route('/invoice', methods=['POST'])    
def invoice():
    name = flask.request.form['Name']
    member = flask.request.form['Member']
    Services=  flask.request.form.getlist('service')
    Data = sqlite3.connect('hairdresser.db')
    table = Data.execute('select * from Service')
    invoice =[]
    total_price = 0.0
    discount=0.0
    invoiceid = Data.execute('select InvoiceID from "Transaction"').fetchall()
    invoiceid = invoiceid[-1][0] +1
    for s in table:
        for i in Services:
            if i in s:
                invoice.append(s)   
                Data.execute('insert into TransactionDetail (type,InvoiceID) values(?,?)',(i,invoiceid))   
    for i in invoice:
        total_price += i[1]
    member_lst = Data.execute('select ID from Member').fetchall()
    for m in member_lst:
        if int(member) in m:
            discount = total_price*0.1
            total_price= total_price *0.9 
    Data.execute('insert into "Transaction" (Name,Member_id,Date,"Total Price") values(?,?,?,?)',(name,member,date.today(),total_price))
    Data.commit()
    return flask.render_template('invoice.html',invoice=invoice,name=name,member=member,total_price=total_price,discount=discount,date =date.today(),id =invoiceid )

@app.route('/confirm_invoice')    
def confirm_invoice():
    return flask.render_template('index.html')

@app.route('/deconfirm_invoice')    
def deconfirm_invoice():
    Data = sqlite3.connect('hairdresser.db')
    Data.rollback()
    return flask.render_template('service.html')

@app.route('/history',methods=['GET'])    
def history():
    Data = sqlite3.connect('hairdresser.db')
    c = flask.request.values.get('choice')
    today = date.today()
    if None == c or 'Day'==c :
        back = date.today()
        table = Data.execute("select * from 'Transaction' where Date >= ? and Date <= ?",(back,today)).fetchall()
    elif 'Week' in c:
        back = date.today() - timedelta(days= 7)
        table = Data.execute('select * from "Transaction" where Date >= ? and Date <= ?',(back,today)).fetchall()

    else:
        back = date.today() - timedelta(days= 30)
        table = Data.execute('select * from "Transaction" where Date >= ? and Date <=? ',(back,today)).fetchall()
    
    return flask.render_template('History.html',history= table)

@app.route('/edit')    
def edit():
    return flask.render_template('edit.html')
@app.route('/editted',methods = ['POST'])
def editted():
    Data = sqlite3.connect('hairdresser.db')
    edits =[]
    edits.append(flask.request.values.get('MemberID'))
    edits.append(flask.request.values.get('SU_Name'))
    edits.append(flask.request.values.get('Contact'))
    edits.append(flask.request.values.get('Gender'))
    edits.append(flask.request.values.get('Address'))
    edits.append(flask.request.values.get('Email'))
    NONETYPE = flask.request.values.get('FAKE')
    original = Data.execute('select * from Member where ID = ?',(int(edits[0]),)).fetchall()
    for i in range(len(edits)):
        if edits[i] == NONETYPE or edits[i]==None:
            edits[i] = original[0][i]
    Data.execute('update Member set Name =?,Contact=?,Gender=?,Address=?,Email=? where ID= ?',(edits[1],edits[2],edits[3],edits[4],edits[5],edits[0]))
    Data.commit()
    return flask.render_template('index.html')

@app.route('/revenue')    
def revenue():
    Data = sqlite3.connect('hairdresser.db')
    table = Data.execute("select `Total Price`,Date from 'Transaction'").fetchall()
    Month = ''
    Month_lst=[]
    Monthly = 0.0
    for row in table:
        if row ==(None,None):
            pass
        else:
            if Month != str(row[1])[:7]:
                Month_lst.append([Month,Monthly])
                Month = str(row[1])[:7]
                Monthly += float(row[0])
            else:
                Monthly +=float(row[0])
    Month_lst.append([Month,Monthly])
    return flask.render_template('revenue.html',table=Month_lst[1:])


if __name__ == '__main__': 
    app.run(port = 4569, debug = True) 
    
app.run(debug=True)

