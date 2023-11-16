

# ---------------------------------------------------------

# Importation des librairies 

#---------------------------------------------------------

import smartcard.System as scardsys
import smartcard.util as scardutil
import smartcard.Exceptions as scardexcp

import time
from datetime import datetime

import mysql.connector
from mysql.connector import errorcode

conn_reader = None

#---------------------------------------------------------

# LOGICIEL MACHINE A CAFE CAFEDELIKA

#---------------------------------------------------------




#-----------------------------------------------------------------------------
#------------------------------ PARTIE smart_card ----------------------------
#-----------------------------------------------------------------------------



# Modification de la fonction init_smart_card

def init_smart_card():
    try:
        lst_readers = scardsys.readers()
    except scardexcp.Exceptions as e:
        print(e)
        return

    if len(lst_readers) < 1:
        print("Pas de lecteur de carte connecté !")
        exit()

    global conn_reader
    conn_reader = lst_readers[0].createConnection()

    try:
        conn_reader.connect()
    except Exception as e:
        if 'Card is unpowered' in str(e):
            print("Pas de carte dans le lecteur : ", e)
            exit()
        else:
            print("Erreur de connexion au lecteur de carte : ", e)
            exit()

    atr = conn_reader.getATR()

    # Stockez l'ATR dans une variable globale
    global card_atr
    card_atr = atr

    return

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------



#-----------------------------------------------------------------------------
#------------------------------ PARTIE PRINT----------------------------------
#-----------------------------------------------------------------------------

# Fonction pour imprimer le solde de la carte
def print_solde():
    # Définition d'une APDU pour obtenir le solde
    apdu = [0x82, 0x01, 0x00, 0x00, 0x02]

    try:
        # Tentative de transmission de l'APDU à la carte à puce
        data, sw1, sw2 = conn_reader.transmit(apdu)
        # Affichage des codes SW1 et SW2 en cas de succès
        print ("sw1 : 0x%02X | sw2 : 0x%02X" % (sw1, sw2))
    except scardexcp.CardConnectionException as e:
        # Gestion des erreurs de connexion avec la carte
        print("Erreur : ", e)

    # Calcul du solde à partir des données reçues
    solde = (int(data[0]) * 100 + int(data[1])) / 100.00 # Les données sont interprétées comme deux octets représentant le solde en centimes. 
    # Ils sont convertis en entiers, multipliés par 100 pour obtenir le montant en euros, puis divisés par 100.00 pour obtenir un nombre à virgule flottante.

    # Affichage des résultats, y compris les codes SW1 et SW2 et le solde
    print("""
        sw1 : 0x%02X | 
        sw2 : 0x%02X | 
        Solde de la carte : %.2f €""" % (sw1, sw2, solde))
    return

def print_nom():
    apdu = [0x81, 0x02, 0x00, 0x00, 0x00]  # Instruction à transmettre à la carte
    data, sw1, sw2 = conn_reader.transmit(apdu)
    apdu[4] = sw2
    data, sw1, sw2 = conn_reader.transmit(apdu)
    nom = "".join(chr(e) for e in data)
    return nom

def print_prenom():
    apdu = [0x81, 0x04, 0x00, 0x00, 0x00]  # Instruction à transmettre à la carte
    data, sw1, sw2 = conn_reader.transmit(apdu)
    apdu[4] = sw2
    data, sw1, sw2 = conn_reader.transmit(apdu)
    prenom = "".join(chr(e) for e in data)
    return prenom


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

# Fonction pour enregistrer la transaction dans la base de données
def enregistrer_transaction(montant, libelle, type_operation):
    nom = print_nom()
    prenom = print_prenom()

    try:
        connection = mysql.connector.connect(
            host='localhost',  # Correction de l'adresse du serveur MySQL
            user='root',
            password='root',
            database='purpledragon'
        )

        cursor = connection.cursor()

        # Récupérer l'identifiant de l'étudiant basé sur le nom et le prénom
        select_etu_query = "SELECT etu_num FROM etudiant WHERE etu_nom = %s AND etu_prenom = %s"
        cursor.execute(select_etu_query, (nom, prenom))
        result = cursor.fetchone()

        if result:
            etu_num = result[0]

            # Insérer la transaction dans la table "compte"
            insert_query = "INSERT INTO compte (etu_num, opr_date, opr_montant, opr_libelle, type_operation) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (etu_num, datetime.now(), montant, libelle, type_operation))

            # Valider la transaction dans la base de données
            connection.commit()
            print("Transaction enregistrée dans la base de données.")
        else:
            print("Étudiant non trouvé dans la base de données.")

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Erreur d'authentification à la base de données")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("La base de données spécifiée n'existe pas")
        else:
            print("Erreur inattendue :", err)
    finally:
        # Fermer le curseur et la connexion
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()



#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
#------------------------------ PARTIE ECRIRE---------------------------------
#-----------------------------------------------------------------------------

# Fonction pour débiter la carte et enregistrer la transaction
def debiter_carte(montant, libelle, type_operation):
    nom = print_nom()
    prenom = print_prenom()

    apdu = [0x82, 0x03, 0x00, 0x00, 0x02, 0x00, int(montant * 100)]  # Convertir le montant en centimes

    try:
        data, sw1, sw2 = conn_reader.transmit(apdu)
        if sw1 == 0x90:
            # Enregistrez la transaction dans la base de données
            enregistrer_transaction(montant, libelle, type_operation)
            
            print(f"Préparation de la boisson ({libelle}) en cours...")
            # Barre de chargement
            for i in range(1, 11):
                print("\rChargement en cours : [{}{}] {}%".format("#" * i, " " * (10 - i), i * 10), end="")
                time.sleep(0.5)

            print("\nTransaction enregistrée dans la base de données.")
            print("""\n
                 ______                                 _                                      _                _ 
                (____  \                               | |                      _         _   (_)              | |
                 ____)  ) ___  ____  ____   ____     _ | | ____ ____ _   _  ___| |_  ____| |_  _  ___  ____    | |
                |  __  ( / _ \|  _ \|  _ \ / _  )   / || |/ _  ) _  | | | |/___)  _)/ _  |  _)| |/ _ \|  _ \   |_|
                | |__)  ) |_| | | | | | | ( (/ /   ( (_| ( (/ ( ( | | |_| |___ | |_( ( | | |__| | |_| | | | |   _ 
                |______/ \___/|_| |_|_| |_|\____)   \____|\____)_|| |\____(___/ \___)_||_|\___)_|\___/|_| |_|  |_|
                                                              (_____|                                             
                """)
            print_solde()
        else:
            print(f"Erreur, plus d'argent sur la carte : {sw1}")
    except scardexcp.CardConnectionException as e:
        print("Erreur : ", e)
    return

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------


#-----------------------------------------------------------------------------
#------------------------------ PARTIE DU MENU--------------------------------
#-----------------------------------------------------------------------------

# Modification du message de bienvenue
def print_hello_message():
    print("""

   _____       __         _      _ _ _         
  / ____|     / _|       | |    | (_) |        
 | |     __ _| |_ ___  __| | ___| |_| | ____ _ 
 | |    / _` |  _/ _ \/ _` |/ _ \ | | |/ / _` |
 | |___| (_| | ||  __/ (_| |  __/ | |   < (_| |
  \_____\__,_|_| \___|\__,_|\___|_|_|_|\_\__,_|
                                                                                                 

 -- Version 3.00 --
 -- "Un café... mais délicat"
 -- Auteur : Maxence -- \n \n""")



# Modification du menu
def print_menu():
    print (" 1 - Café (0.20€) ")
    print (" 2 - Café long (0.30€) ")
    print (" 3 - Cappuccino (0.40€) ")
    print (" 4 - Café BIO (0.40€) ")
    print (" 5 - Chocolat chaud (0.30€) ")
    print (" 6 - Thé (0.20€) ")
    print (" 7 - Quitter ")

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------




#-----------------------------------------------------------------------------
#------------------------------ PARTIE MAIN ----------------------------------
#-----------------------------------------------------------------------------

def main():
    init_smart_card()
    print_hello_message()

    while True:
        print_menu()
        cmd = int(input("Choisissez votre boisson : "))
        if cmd in [1, 2, 3, 4, 5, 6]:
            montant = 0.20 if cmd == 1 or cmd == 6 else 0.30 if cmd == 2 or cmd == 5 else 0.40
            libelle = "Café" if cmd == 1 else "Café long" if cmd == 2 else "Cappuccino" if cmd == 3 else "Café BIO" if cmd == 4 else "Chocolat chaud" if cmd == 5 else "Thé"
            type_operation = "Dépense"
            enregistrer_transaction(montant, libelle, type_operation)
        elif cmd == 7:
            break  # Utilisez 'break' pour sortir de la boucle
        else:
            print("Commande inconnue !")
        print("\n ---\n")

    # Code à exécuter après la boucle
    print("Fermeture de l'application.")

if __name__ == "__main__":
    main()




