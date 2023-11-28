#RODELIKA, logiciel de gestion de la BDD

import mysql.connector
from datetime import datetime
cnx = mysql.connector.connect(user='root',
password='root',
host='localhost',
database='purpledragon')


def print_hello_message():
	print ("-----------------------------------")
	print ("-- Logiciel de gestion : Rodelika --")
	print ("-----------------------------------")
	
def print_menu():
	print (" 1 - Afficher la liste des étudiants ")
	print (" 2 - Afficher le solde des étudiants ")
	print (" 3 - Saisir un nouvel étudiant ")
	print (" 4 - Attribuer un bonus ")
	print (" 5 - Quitter")
	
def get_list_student():
	sql="select etudiant.* from etudiant"
	cursor = cnx.cursor()
	cursor.execute(sql)
	row = cursor.fetchone()
	while row is not None:
		print(row)
		row = cursor.fetchone()
		
def get_list_student_with_sold():
	sql="""select etudiant.*, sum(compte.opr_montant) as sold from etudiant,compte where etudiant.etu_num = compte.etu_num group by compte.etu_num"""
	cursor = cnx.cursor()
	cursor.execute(sql)
	row = cursor.fetchone()
	while row is not None:
		print(row)
		
def new_student():
	nom = input("Nom Etudiant : ")
	pre = input("Pre Etudiant : ")
	sql = """INSERT INTO etudiant (etu_num, etu_nom, etu_prenom) VALUES (NULL, %s,%s);"""
	val = (nom, pre)
	cursor = cnx.cursor()
	cursor.execute(sql, val)
	cnx.commit()
	num = cursor.lastrowid
	sql2 = """INSERT INTO compte(etu_num, opr_date, opr_montant, opr_libelle, type_operation) VALUES(%s, %s, %s, %s, %s);"""
	current_datetime = datetime.now()
	date = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
	val = (num, date, 1.00, "Initialisation", "Bonus")
	cursor = cnx.cursor()
	cursor.execute(sql2, val)
	cnx.commit()
	
def add_bonus():
	num = input("Num Etudiant : ")
	com = input("Commentaire : ")
	sql = """INSERT INTO compte(etu_num, opr_date, opr_montant, opr_libelle, type_operation) VALUES(%s, %s, %s, %s, %s);"""
	current_datetime = datetime.now()
	date = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
	val = (num, date, 1.00, com, "Bonus")
	cursor = cnx.cursor()
	cursor.execute(sql, val)
	cnx.commit()
	print ("Bonus + 1.00 euros")
	
def main():
	n = 1
	print_hello_message()
	while(n != 0):
		print_menu()
		menu = input()
		match menu:
			case "1":
				get_list_student()
				print(" 1 - Retour au menu ")
				print(" 2 - Quitter le programme ")
				submenu = input()
				if (submenu == "2"):
					break
			case "2":
				get_list_student_with_sold()
				print(" 1 - Retour au menu ")
				print(" 2 - Quitter le programme ")
				submenu = input()
				if (submenu == "2"):
					break
			case "3":
				new_student()
				print(" 1 - Retour au menu ")
				print(" 2 - Quitter le programme ")
				submenu = input()
				if (submenu == "2"):
					break
			case "4":
				add_bonus()
				print(" 1 - Retour au menu ")
				print(" 2 - Quitter le programme ")
				submenu = input()
				if (submenu == "2"):
					break
			case "5":
				break
			case _:
				print("ERREUR : Entrée Invalide")
	
main()
