from flask import Flask, render_template, request, redirect, url_for, flash
from wtforms import Form, validators, StringField, DateField
from flask_mysqldb import MySQL
import datetime


app = Flask(__name__)
app.secret_key = 'many random bytes'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Deepti123!'
app.config['MYSQL_DB'] = 'crudapplication'

import requests

mysql = MySQL(app)
@app.route('/',methods=['GET','POST'])
def Index():
    if request.method=='GET':
        cur = mysql.connection.cursor()
        cur.execute("select bookId from transaction "  )
        data2=cur.fetchall()
        print(data2,"aaaaaaaaaaaa")
        data=requests.get("https://frappe.io/api/method/frappe-library")
        bookData=data.json()
        print(bookData["message"])
        if data.status_code==200:
            booklist=[]
            for i in  bookData["message"]:
                print(i,"bbbbbbbbbb")
                if i["bookID"] in list(data2):
                    continue
                else:
                    booklist.append(i)
            return render_template('index2.html', members=booklist )

            
    elif request.method=='POST':
         search =request.form['Search']
         print(search,"DDDDD")
         data=requests.get("https://frappe.io/api/method/frappe-library?title="+ search + "&authors=" + search )
         bookData=data.json()
         return render_template('index2.html',members=bookData["message"])

@app.route('/insert', methods = ['POST'])
def insert():

    if request.method == "POST":
        print(request.form)
        name = request.form['name']
        email = request.form['email']
        contact = request.form['phone']
        bookId = request.form['bookId']
        bookName = request.form['bookName']
        now=datetime.datetime.now() 
        issueDate = now.isoformat()
        returnDate=request.form['returnDate']
        cur = mysql.connection.cursor()
        cur.execute("select * from members where email='"+ email+ "' or phone="+ contact+";"  )
        print("select * from members where email='"+ email+ "'")
        data=cur.fetchall()
        print(data,"asdfgh")
        if data:
            cur.execute("""
               UPDATE members
               SET num_of_books=%s
               WHERE email=%s
            """, ( (data[0][4])+1,email))
            cur.execute("INSERT INTO transaction (name, contact, email,bookId,bookName,issueDate,returnDate,status,amount) VALUES (%s, %s, %s, %s,%s,%s,%s,%s,%s)", (name, contact, email,bookId,bookName,issueDate,returnDate,1,10))
            mysql.connection.commit()
            flash("Book Issued Successfully")
            return redirect(url_for('Index'))
        else:
            flash("user not found")
            return redirect(url_for('Index'))

@app.route('/update',methods=['POST','GET'])
def update():

    if request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE members
               SET name=%s, email=%s, phone=%s
               WHERE id=%s
            """, (name, email, phone, id_data))
        mysql.connection.commit()
        flash("Data Updated Successfully")
        return redirect(url_for('Index'))



@app.route('/issuer',methods=['GET'])
def Issuer():
    if request.method=="GET":
        cur = mysql.connection.cursor()
        cur.execute("select * from transaction")
        X=cur.fetchall()
        print(X,"1111111111")
        cur.close()
        return render_template('bookissuers.html', Issuer=X )
    

@app.route('/member',methods=['GET'])
def Issue():
    if request.method=="GET":
        cur = mysql.connection.cursor()
        cur.execute("select * from members")
        y=cur.fetchall()
        print(y)
        cur.close()
    return render_template('transaction.html', Issue=y)
    
# View Details of Member by ID
@app.route('/member/<string:id>')
def viewMember(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM members WHERE id=%s", [id])
    member = cur.fetchone()
    if result > 0:
        return render_template('view_member_details.html', member=member)
    else:
        msg = 'This Member Does Not Exist'
        return render_template('view_member_details.html', warning=msg)


class AddMember(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.length(min=6, max=50)])
    phone = StringField('Phone', [validators.Length(min=1, max=50)])  # Add this line



# Add Member
@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    form = AddMember(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        phone=form.phone.data
        cur = mysql.connection.cursor()
        cur.execute("select * from members where email='"+ email+ "' or phone="+ phone+";"  )
        print("select * from members where email='"+ email+ "'")
        data=cur.fetchall()
        print(data,"asdfgh")
        if data:
            flash("user already exist")
            return redirect(url_for('Index'))
        cur.execute("INSERT INTO members(name, email, phone, Debt) VALUES (%s, %s, %s, %s)", (name, email, phone, 0))
        mysql.connection.commit()
        cur.close()
        flash("New Member Added", "success")
        return redirect(url_for('add_member'))
    return render_template('add_member.html', form=form)


# Edit Member by ID


@app.route('/edit_member/<string:id>', methods=['GET', 'POST'])
def edit_member(id):
    print("ID:", id)
    form = AddMember(request.form)

    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM members WHERE id=%s", (id,))
        data1 = cur.fetchall()
        return render_template('edit_member.html', form=form, member=data1)

    if request.method == 'POST' and form.validate():
        # Extract form data
        new_name = form.name.data
        # Add other form fields as needed

        cur = mysql.connection.cursor()
        cur.execute("UPDATE members SET name=%s WHERE id=%s", (new_name, id))
        mysql.connection.commit()
        cur.close()
        flash("Member Updated", "success")
        return redirect(url_for('Index'))

    return render_template('edit_member.html', form=form, member=data1)



@app.route('/delete/<string:id>',methods=['GET','POST'])
def delete_member(id):
    print(id)
    cur = mysql.connection.cursor()
    cur.execute(f"DELETE FROM members WHERE id={id}")
    mysql.connection.commit()
    flash("Member Has Been Deleted Successfully")
    return redirect(url_for('Index'))

# editbook

class AddBook(Form):
    id = StringField('Book ID', [validators.Length(min=1, max=11)])
    bookId = StringField('id', [validators.Length(min=2, max=255)])
    bookName = StringField('Title', [validators.Length(min=2, max=255)])
    issueDate = DateField('Publication Date', [validators.InputRequired()])
    returnDate= DateField('return date', [validators.InputRequired()])
    email = StringField('Email', [validators.length(min=6, max=50)])

# Assuming other fields like 'author', 'average_rating', 'isbn', 'isbn13', 'language_code', 'num_pages', 'ratings_count', 'text_reviews_count', 'publisher', 'total_quantity' are also part of the AddBook form class
# Add Book
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    form = AddBook(request.form)
    if request.method == 'POST' and form.validate():
        bookId = form.bookId.data
        issueDate = form.issueDate.data
        returnDate = form.returnDate.data
        email = form.email.data

        cur = mysql.connection.cursor()
        cur.execute("select * from transaction where bookId=%s or email=%s;", (bookId, email))
        data = cur.fetchall()

        if data:
            flash("Book or User already found")
            return redirect(url_for('Index'))

        cur.execute("INSERT INTO transaction(bookId, issueDate, returnDate, email) VALUES (%s, %s, %s, %s)", (bookId, issueDate, returnDate, email))
        mysql.connection.commit()
        cur.close()
        flash("New Book Added", "success")
        return redirect(url_for('add_book'))
    return render_template('add_book.html', form=form)


from werkzeug.exceptions import abort

from werkzeug.exceptions import NotFound

@app.route('/delete_book/<string:book_name>', methods=['GET', 'POST'])
def delete_book(book_name):
    print("Book Name:", book_name)

    cur = mysql.connection.cursor()
    query = "DELETE FROM transaction WHERE id = %s"
    
    try:
        cur.execute(query, (book_name,))
        mysql.connection.commit()
        flash("BooK  Has Been Deleted Successfully", "success")
    except NotFound:
        flash("Book Not Found", "error")
    finally:
        cur.close()

    return redirect(url_for('Index'))


if __name__ == "__main__":
    app.run(debug=True)
