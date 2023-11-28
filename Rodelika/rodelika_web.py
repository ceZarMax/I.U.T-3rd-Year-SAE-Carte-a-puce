#RODELIKA_WEB, logiciel de gestion de la BDD

import mysql.connector
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

cnx = mysql.connector.connect(user='root', password='root', host='localhost', database='purpledragon')

app = Flask(__name__)
	
def get_list_student():
    sql = "SELECT etudiant.* FROM etudiant"
    cursor = cnx.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    students = [{"etu_num": row[0], "etu_nom": row[1], "etu_prenom": row[2]} for row in rows]
    return students
		
def get_list_student_with_sold():
	formatted_list = []
	sql = "SELECT etudiant.etu_num, etudiant.etu_nom, etudiant.etu_prenom, SUM(compte.opr_montant) as sold FROM etudiant JOIN compte ON etudiant.etu_num = compte.etu_num GROUP BY etudiant.etu_num, etudiant.etu_nom, etudiant.etu_prenom"
	cursor = cnx.cursor()
	cursor.execute(sql)
	rows = cursor.fetchall()
	for result in rows:
		formatted_result = ' '.join(map(str, result))
		formatted_list.append(formatted_result)
	return formatted_list
    
def new_student():
	if request.method == 'POST':
		nom = request.form['nom']
		prenom = request.form['prenom']
		insert_student_query = "INSERT INTO etudiant (etu_num, etu_nom, etu_prenom) VALUES (NULL, %s, %s);"
		student_values = (nom, prenom)
		cursor = cnx.cursor()
		cursor.execute(insert_student_query, student_values)
		cnx.commit()
		student_id = cursor.lastrowid
		insert_bonus_query = "INSERT INTO compte (etu_num, opr_date, opr_montant, opr_libelle, type_operation) VALUES (%s, %s, %s, %s, %s);"
		current_datetime = datetime.now()
		date = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
		bonus_values = (student_id, date, 1.00, "Initialisation", "Bonus")
		cursor.execute(insert_bonus_query, bonus_values)
		cnx.commit()
		cursor.close()
		return redirect(url_for('success_student'))
	else:
		return render_template('new_student_form.html')
	
def add_bonus():
	if request.method == 'POST':
		num = request.form['num']
		com = request.form['commentaire']
		insert_bonus_query = "INSERT INTO compte (etu_num, opr_date, opr_montant, opr_libelle, type_operation) VALUES (%s, %s, %s, %s, %s);"
		current_datetime = datetime.now()
		date = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
		bonus_values = (num, date, 1.00, com, "Bonus")
		cursor = cnx.cursor()
		cursor.execute(insert_bonus_query, bonus_values)
		cnx.commit()
		cursor.close()
		return redirect(url_for('success_bonus'))
	else:
		return render_template('add_bonus_form.html')

@app.route('/')
def home():
    return render_template('rodelika_web.html')
    
@app.route('/menu', methods=['GET', 'POST'])
def main_menu():
    return render_template('menu.html')

@app.route('/menu/<option>', methods=['GET', 'POST'])
def menu(option):
	if option == "1":
		students = get_list_student()
		return render_template('list_students.html', students=students)
	elif option == "2":
		students = get_list_student_with_sold()
		return render_template('list_students_with_sold.html', students=students)
	elif option == "3":
		return new_student()
	elif option == "4":
		return add_bonus()
	elif option == "5":
		return render_template('exit.html')
		
@app.route('/success_student')
def success_student():
    message = "Student added successfully."
    return render_template('success_student.html', message=message)

@app.route('/success_bonus')
def success_bonus():
    message = "Bonus added successfully."
    return render_template('success_student.html', message=message)
	
if __name__ == '__main__':
    app.run(debug=True)
