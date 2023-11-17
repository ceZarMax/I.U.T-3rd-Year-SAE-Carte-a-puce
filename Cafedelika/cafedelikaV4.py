

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
    except scardexcp.CardConnectionException as e:
        # Gestion des erreurs de connexion avec la carte
        print("Erreur : ", e)

    # Calcul du solde à partir des données reçues
    solde = (int(data[0]) * 100 + int(data[1])) / 100.00 # Les données sont interprétées comme deux octets représentant le solde en centimes. 
    # Ils sont convertis en entiers, multipliés par 100 pour obtenir le montant en euros, puis divisés par 100.00 pour obtenir un nombre à virgule flottante.

    # Affichage des résultats, y compris les codes SW1 et SW2 et le solde
    print("""\n
        Solde de la carte : %.2f €""" % (solde))

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
            host='localhost',
            user='root',
            password='root',
            database='purpledragon'
        )

        cursor = connection.cursor()

        # Récupérer l'identifiant de l'étudiant basé sur le nom et le prénom
        select_etu_query = "SELECT etu_num, etu_solde FROM etudiant WHERE etu_nom = %s AND etu_prenom = %s"
        cursor.execute(select_etu_query, (nom, prenom))
        result = cursor.fetchone()

        if result:
            etu_num, etu_solde = result
            # Vérifie si le solde de l'étudiant est supérieur ou égal au montant voulant être débité
            if etu_solde >= montant:
                # Insérer la transaction dans la table "compte"
                insert_query = "INSERT INTO compte (etu_num, opr_date, opr_montant, opr_libelle, type_operation) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(insert_query, (etu_num, datetime.now(), montant, libelle, type_operation))

                # Débiter le solde de l'étudiant
                update_solde_query = "UPDATE etudiant SET etu_solde = etu_solde - %s WHERE etu_num = %s"
                cursor.execute(update_solde_query, (montant, etu_num))

                # Valider la transaction dans la base de données
                connection.commit()
                print("Solde et transaction enregistrés dans la base de données.")
                
                # Mettre à jour les statistiques de la boisson dans la table "boissons"
                update_boisson_query = "UPDATE boissons SET nombres_ventes = nombres_ventes + 1, montant_total = montant_total + %s WHERE boisson_nom = %s"
                cursor.execute(update_boisson_query, (montant, libelle))
                connection.commit()
                print("Statistiques de vente mises à jour.")
            else:
                print("Solde insuffisant pour effectuer la transaction.")
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
# Fonction pour débiter la carte et enregistrer la transaction
def debiter_carte(montant, libelle, type_operation):

    # Obtenez le solde actuel sur la carte
    solde_carte = get_solde_carte()

    # Définir une marge d'erreur acceptable pour la comparaison des nombres flottants
    marge_erreur = 0.01  # Vous pouvez ajuster cette valeur en fonction de vos besoins

    # Comparer le solde de la carte avec le montant enregistré dans la base de données
    if abs(solde_carte - get_montant_base_de_donnees()) < marge_erreur:
        apdu = [0x82, 0x03, 0x00, 0x00, 0x02, 0x00, int(montant * 100)]  # Convertir le montant en centimes
        try:
            data, sw1, sw2 = conn_reader.transmit(apdu)
            if sw1 == 0x90:
                # Appel de la fonction pour enregistrer la transaction dans la base de données
                enregistrer_transaction(montant, libelle, type_operation)
                
                print(f"Préparation du {libelle} en cours...")
                # Barre de chargement
                for i in range(1, 11):
                    print("\rChargement en cours : [{}{}] {}%".format("#" * i, " " * (10 - i), i * 10), end="")
                    time.sleep(0.5)
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
                print(f"\nERREUR : pas assez d'argent sur la carte")
                print(print_solde())
        except scardexcp.CardConnectionException as e:
            print("Erreur : ", e)
    else:
        print("ERREUR : Le montant sur la carte ne correspond pas au montant enregistré dans la base de données.")
        print("Solde sur la carte : %.2f €" % solde_carte)
        print("Montant enregistré dans la base de données : %.2f €" % get_montant_base_de_donnees())
        print("Veuillez aller à la borne de recharge pour mettre à jour votre solde.")


# Fonction pour obtenir le solde actuel sur la carte
def get_solde_carte():
    apdu = [0x82, 0x01, 0x00, 0x00, 0x02]
    try:
        data, sw1, sw2 = conn_reader.transmit(apdu)
        solde = (int(data[0]) * 100 + int(data[1])) / 100.00
        return solde
    except scardexcp.CardConnectionException as e:
        print("Erreur : ", e)

# Fonction pour obtenir le montant enregistré dans la base de données
def get_montant_base_de_donnees():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='purpledragon'
        )

        cursor = connection.cursor()

        # Récupérer le solde de l'étudiant
        select_etu_query = "SELECT etu_solde FROM etudiant"
        cursor.execute(select_etu_query)
        result = cursor.fetchone()

        if result:
            montant_base_de_donnees, = result  # Déballer le tuple
            return montant_base_de_donnees
        else:
            return None

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Erreur d'authentification à la base de données")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("La base de données spécifiée n'existe pas")
        else:
            print("Erreur inattendue :", err)


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
                                                                                                 

 -- Version 4.00 --
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
            debiter_carte(montant, libelle, type_operation)
        elif cmd == 7:
            break  # Utilisez 'break' pour sortir de la boucle
        else:
            print("Commande inconnue !")
        print("\n ---\n")

    # Code à exécuter après la boucle
    print("Fermeture de l'application.")

if __name__ == "__main__":
    main()




