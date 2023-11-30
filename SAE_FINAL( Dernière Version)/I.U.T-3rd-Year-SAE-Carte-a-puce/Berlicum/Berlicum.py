import mysql.connector
import smartcard.System as scardsys
import smartcard.util as scardutil
import smartcard.Exceptions as scardexcp
from decimal import Decimal
import datetime


conn_reader = None

#---------------------------------------------------------

# LOGICIEL BORNE DE RECHARGE Berlicum

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

# Assurez-vous de remplacer les valeurs de connexion par les vôtres
cnx = mysql.connector.connect(user='root',
                              password='root',
                              host='localhost',
                              database='purpledragon')

def print_hello_message():
    print("-------------------------------------------------")
    print("-- Logiciel embarqué sur la borne de recharge --")
    print("-------------------------------------------------")

def print_menu():
    print("1 - Afficher mes informations")
    print("2 - Consulter mes bonus")
    print("3 - Transférer mes bonus sur ma carte")
    print("4 - Consulter le crédit disponible sur ma carte")
    print("5 - Recharger ma carte")
    print("6 - Quitter")




#------------------------------------------------------#
#------RECUPERATION DES INFORMATIONS DE LA CARTE-------#
#------------------------------------------------------#
def print_nom():
    apdu = [0x81, 0x02, 0x00, 0x00, 0x00] # Instruction à transmettre à la carte
    data, sw1, sw2 = conn_reader.transmit(apdu) # Envoyer la commande à la carte et récupérer les données, ainsi que les codes SW1 et SW2 en retour
    apdu[4] = sw2 # Met à jour le cinquième octet de l'instruction qui correspond à l'octet SW2
    data, sw1, sw2 = conn_reader.transmit(apdu) # On renvoie la commande et on récupère ses données
    str = ""
    for e in data:
        str += chr(e)
    print (""" 
        Nom : %s""" % (str))    
    return

def print_prenom():
    apdu = [0x81, 0x04, 0x00, 0x00, 0x00] # Instruction à transmettre à la carte
    data, sw1, sw2 = conn_reader.transmit(apdu) # Envoyer la commande à la carte et récupérer les données, ainsi que les codes SW1 et SW2 en retour
    apdu[4] = sw2 # Met à jour le cinquième octet de l'instruction qui correspond à l'octet SW2
    data, sw1, sw2 = conn_reader.transmit(apdu) # On renvoie la commande et on récupère ses données
    str = ""
    for e in data:
        str += chr(e)
    print ("""
        Prénom : %s""" % (str))    
    return

def print_birth():
    apdu = [0x81, 0x06, 0x00, 0x00, 0x00] # Instruction à transmettre à la carte
    data, sw1, sw2 = conn_reader.transmit(apdu) # Envoyer la commande à la carte et récupérer les données, ainsi que les codes SW1 et SW2 en retour
    apdu[4] = sw2 # Met à jour le cinquième octet de l'instruction qui correspond à l'octet SW2
    data, sw1, sw2 = conn_reader.transmit(apdu) # On renvoie la commande et on récupère ses données
    

    str = ""
    for e in data:
        str += chr(e)
        birthdate_formatted = f"{str[:2]}/{str[2:4]}/{str[4:]}" # Afficher la date de naissance avec des /
    print ("""
        Date de naissance : %s""" % (birthdate_formatted))   
    return

def print_etu():
    apdu = [0x81, 0x08, 0x00, 0x00, 0x00] # Instruction à transmettre à la carte
    data, sw1, sw2 = conn_reader.transmit(apdu) # Envoyer la commande à la carte et récupérer les données, ainsi que les codes SW1 et SW2 en retour
    print ("""
        sw1 : 0x%02X | 
        sw2 : 0x%02X |""" % (sw1,sw2)) # Si erreur ici lors de l'éxécutio c'est normal
    apdu[4] = sw2 # Met à jour le cinquième octet de l'instruction qui correspond à l'octet SW2
    data, sw1, sw2 = conn_reader.transmit(apdu) # On renvoie la commande et on récupère ses données
    

    str = ""
    for e in data:
        str += chr(e)
    print ("""
        sw1 : 0x%02X | 
        sw2 : 0x%02X | 
        Numéro étudiant : %s""" % (sw1,sw2,str))   
    return


# Fonction pour imprimer le solde de la carte
def print_solde():
    # APDU pour obtenir le solde, avec une demande de 4 octets de données
    apdu = [0x82, 0x01, 0x00, 0x00, 0x04]

    try:
        # Transmission de l'APDU à la carte à puce
        data, sw1, sw2 = conn_reader.transmit(apdu)
        solde = (data[0] << 24) + (data[1] << 16) + (data[2] << 8) + data[3]
        solde_decimal = solde / 100.00  # Convertir en euros

        # Affichage du solde
        print(""" 
            Solde de la carte : %.2f €""" % (solde_decimal))
    except scardexcp.CardConnectionException as e:
        # Gestion des erreurs de connexion avec la carte
        print("Erreur : ", e)
    return
###################################################################################################




def afficher_informations():
	print("--------------------MES INFORMATIONS------------------------")
	print_nom()
	print_prenom()
	print_birth()

def lire_numero_etudiant():
    apdu = [0x81, 0x08, 0x00, 0x00, 0x00]
    try:
        data, sw1, sw2 = conn_reader.transmit(apdu)

        if sw1 == 0x6C:
            apdu[-1] = sw2  # Mettre à jour P3 avec la taille correcte
            data, sw1, sw2 = conn_reader.transmit(apdu)

            if sw1 == 0x90:
                num_etudiant_str = ''.join(chr(e) for e in data)
                return num_etudiant_str
            else:
                # En cas d'erreur de lecture, renvoyer None
                return None
        else:
            # En cas de réponse inattendue, renvoyer None
            return None
    except Exception as e:
        # En cas d'erreur de communication, renvoyer None
        return None

def consulter_bonus():
    etu_num = lire_numero_etudiant()

    if etu_num is None:
        print("Impossible de lire le numéro d'étudiant à partir de la carte.")
        return

    # Sélectionnez uniquement les enregistrements de type 'Bonus'
    sql = "SELECT SUM(opr_montant) FROM compte WHERE etu_num = %s AND type_operation = 'Bonus';"
    val = (etu_num,)
    cursor = cnx.cursor()
    cursor.execute(sql, val)
    result = cursor.fetchone()

    if result and result[0] is not None:
        total_bonus = float(result[0])
        print(f"Voici le montant de vos bonus : {total_bonus} €")
    else:
        print("Aucun bonus trouvé pour l'étudiant numéro", etu_num)


def lire_solde_carte():
    # APDU pour obtenir le solde, avec une demande de 4 octets de données
    apdu = [0x82, 0x01, 0x00, 0x00, 0x04]

    try:
        # Tentative de transmission de l'APDU à la carte à puce
        data, sw1, sw2 = conn_reader.transmit(apdu)
        if sw1 != 0x90:
            print("Erreur lors de la lecture du solde: SW1 = 0x{:02X}, SW2 = 0x{:02X}".format(sw1, sw2))
            return None

        # Calcul du solde à partir des données reçues
        solde = (data[0] << 24) + (data[1] << 16) + (data[2] << 8) + data[3]
        solde_decimal = solde / 100.00
        return solde_decimal
    except scardexcp.CardConnectionException as e:
        print("Erreur de connexion avec la carte: ", e)
        return None
        
def ecrire_solde_carte(montant):
    # Convertir le montant en centimes
    montant_centimes = int(Decimal(montant) * 100)

    # Décomposition du montant en quatre octets
    montant_bas = montant_centimes & 0xFF
    montant_moyen_bas = (montant_centimes >> 8) & 0xFF
    montant_moyen_haut = (montant_centimes >> 16) & 0xFF
    montant_haut = (montant_centimes >> 24) & 0xFF

    # APDU pour ajouter du crédit
    apdu_credit = [0x82, 0x02, 0x00, 0x00, 0x04, montant_haut, montant_moyen_haut, montant_moyen_bas, montant_bas]

    try:
        data, sw1, sw2 = conn_reader.transmit(apdu_credit)
        return sw1 == 0x90
    except Exception as e:
        print("Erreur lors de la mise à jour du solde sur la carte : ", e)
        return False

def transferer_bonus():

    # Création d'un curseur à partir de la connexion à la base de données
    cursor = cnx.cursor()

    etu_num = lire_numero_etudiant()

    if etu_num is None:
        print("Impossible de lire le numéro d'étudiant à partir de la carte.")
        return

    # Récupérer le total des bonus de la base de données
    sql = "SELECT SUM(opr_montant) FROM compte WHERE etu_num = %s AND type_operation = 'Bonus';"
    cursor.execute(sql, (etu_num,))
    total_bonus_result = cursor.fetchone()
    total_bonus = float(total_bonus_result[0]) if total_bonus_result else 0.0

    print(f"Total des bonus disponibles : {total_bonus} €")

    try:
        montant_a_transferer = float(input("Entrez le montant du bonus à transférer : "))
    except ValueError:
        print("Veuillez entrer un nombre valide.")
        return

    if montant_a_transferer > total_bonus:
        print("Montant trop élevé, pas assez de bonus.")
        return
    elif montant_a_transferer <= 0:
        print("Veuillez entrer un montant positif.")
        return

    if not ecrire_solde_carte(montant_a_transferer):
        print("Échec de la mise à jour du solde sur la carte.")
        return

    # Mettre à jour la base de données pour refléter le nouveau total des bonus
    try:
        # Mise à jour des bonus existants pour refléter le montant transféré
        update_sql = "UPDATE compte SET opr_montant = opr_montant - %s WHERE etu_num = %s AND type_operation = 'Bonus';"
        cursor.execute(update_sql, (montant_a_transferer, etu_num))

        # Insérer un enregistrement pour le bonus transféré
        insert_sql = "INSERT INTO compte (etu_num, opr_date, opr_montant, opr_libelle, type_operation) VALUES (%s, %s, %s, %s, 'Bonus transféré')"
        opr_date = datetime.datetime.now()
        cursor.execute(insert_sql, (etu_num, opr_date, -montant_a_transferer, 'Recharge par borne'))

        cnx.commit()
        print(f"Bonus de {montant_a_transferer} € transférés avec succès.")
    except Exception as e:
        print("Erreur lors de la mise à jour de la base de données: ", e)
        cnx.rollback()





def consulter_credit():
    print("-------------------------MON SOLDE -------------------------")
    # APDU pour obtenir le solde, avec une demande de 4 octets de données
    apdu = [0x82, 0x01, 0x00, 0x00, 0x04]

    try:
        # Transmission de l'APDU à la carte à puce
        data, sw1, sw2 = conn_reader.transmit(apdu)
        solde = (data[0] << 24) + (data[1] << 16) + (data[2] << 8) + data[3]
        solde_decimal = solde / 100.00  # Convertir en euros

        # Affichage du solde
        print(""" 
            Solde de la carte : %.2f €""" % (solde_decimal))
    except scardexcp.CardConnectionException as e:
        # Gestion des erreurs de connexion avec la carte
        print("Erreur : ", e)
    return

def lire_solde_db(etu_num):
    sql = "SELECT SUM(opr_montant) as total_bonus FROM Compte WHERE etu_num = %s AND type_operation = 'Bonus';"
    val = (etu_num,)
    cursor = cnx.cursor()
    cursor.execute(sql, val)
    result = cursor.fetchone()
    return result[0] if result else 0

def recharger_carte():
    etu_num = lire_numero_etudiant()
    if etu_num is None:
        print("Impossible de lire le numéro d'étudiant à partir de la carte.")
        return

    # Demande à l'utilisateur de saisir le montant à ajouter
    montant = Decimal(input("Entrez le montant à ajouter (en euros, max 255) : "))

    # Vérifie que le montant est dans les limites acceptables
    if montant < 0 or montant > 255:
        print("Le montant doit être compris entre 0 et 255 euros.")
        return

    # Convertit le montant en centimes
    montant_centimes = int(montant * 100)
    montant_haut = montant_centimes >> 24  # Partie haute du montant
    montant_moyen_haut = (montant_centimes >> 16) & 0xFF
    montant_moyen_bas = (montant_centimes >> 8) & 0xFF
    montant_bas = montant_centimes & 0xFF

    # APDU pour ajouter du crédit
    apdu_credit = [0x82, 0x02, 0x00, 0x00, 0x04, montant_haut, montant_moyen_haut, montant_moyen_bas, montant_bas]

    try:
        # Envoi de la commande APDU
        data, sw1, sw2 = conn_reader.transmit(apdu_credit)
        if sw1 == 0x90:
            print(f"Succès ! Crédit de {montant} € ajouté.")
            # Mettre à jour la base de données
            opr_date = datetime.datetime.now()

            # Récupérer le solde actuel
            cursor = cnx.cursor()
            sql = "SELECT etu_solde FROM etudiant WHERE etu_num = %s"
            cursor.execute(sql, (etu_num,))
            current_balance = Decimal(cursor.fetchone()[0])

            # Mettre à jour le solde dans la table 'etudiant'
            new_balance = current_balance + montant
            sql_update_balance = "UPDATE etudiant SET etu_solde = %s WHERE etu_num = %s"
            cursor.execute(sql_update_balance, (float(new_balance), etu_num))

            # Enregistrer l'opération de recharge dans la table 'compte'
            sql_insert_operation = "INSERT INTO compte (etu_num, opr_date, opr_montant, opr_libelle, type_operation) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql_insert_operation, (etu_num, opr_date, float(montant), 'Rechargement par carte', 'Recharge'))

            # Valider les modifications
            cnx.commit()

        else:
            print(f"Erreur lors de l'ajout du crédit : 0x{sw1:02X} 0x{sw2:02X}")
    except scardexcp.CardConnectionException as e:
        print("Erreur : ", e)

    return

def main():
    init_smart_card()
    print_hello_message()
    while True:
        print_menu()
        choice = input("Choix : ")
        if choice == '1':
            afficher_informations()
            print("------------------------------------------------------------")
        elif choice == '2':
            consulter_bonus()
            print("")
        elif choice == '3':
            transferer_bonus()
            print("")
        elif choice == '4':
            consulter_credit()
            print("------------------------------------------------------------")
        elif choice == '5':
            recharger_carte()
            print("")
            
        elif choice == '6':
            print("Merci d'avoir utilisé le logiciel Berlicum. À bientôt !")
            break
        else:
            print("Choix non valide, veuillez réessayer.")

if __name__ == "__main__":
    main()
