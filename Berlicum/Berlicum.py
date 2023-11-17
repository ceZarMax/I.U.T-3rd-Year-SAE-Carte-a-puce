import mysql.connector
import smartcard.System as scardsys
import smartcard.util as scardutil
import smartcard.Exceptions as scardexcp


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
###################################################################################################




def afficher_informations():
	print("--------------------MES INFORMATIONS------------------------")
	print_nom()
	print_prenom()
	print_birth()

def consulter_bonus():
    sql = "SELECT * FROM Compte WHERE etu_num = %s AND type_operation = 'Bonus';"
    val = (etu_num)
    cursor = cnx.cursor()
    cursor.execute(sql, val)
    rows = cursor.fetchall()
    for row in rows:
        print(row)

def transferer_bonus(etu_num):
    sql_select = "SELECT * FROM Compte WHERE etu_num = %s AND type_operation = 'Bonus';"
    sql_update = "UPDATE compte SET type_operation = 'Bonus transféré' WHERE etu_num = %s AND type_operation = 'Bonus';"
    val = (etu_num,)
    cursor = cnx.cursor()
    cursor.execute(sql_select, val)
    bonuses = cursor.fetchall()
    if bonuses:
        cursor.execute(sql_update, val)
        cnx.commit()
        print("Bonus transférés avec succès.")
    else:
        print("Aucun bonus à transférer.")

def consulter_credit():
    print("-------------------------MON SOLDE -------------------------")
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
    print(""" 
        Solde de la carte : %.2f €""" % (solde))
    return

def lire_solde_db(etu_num):
    sql = "SELECT SUM(opr_montant) as total_bonus FROM Compte WHERE etu_num = %s AND type_operation = 'Bonus';"
    val = (etu_num,)
    cursor = cnx.cursor()
    cursor.execute(sql, val)
    result = cursor.fetchone()
    return result[0] if result else 0

def recharger_carte():
    try:
        # Demander à l'utilisateur le montant à recharger (en euros)
        montant_recharge_euros = float(input("Entrez le montant à recharger (en euros) : "))
        montant_recharge_centimes = int(montant_recharge_euros * 100)  # Convertir en centimes

        # Préparation de l'APDU pour recharger le crédit
        apdu = [0x82, 0x02, 0x00, 0x00, 0x02, montant_recharge_centimes >> 8, montant_recharge_centimes & 0xFF]

        # Transmission de l'APDU à la carte
        data, sw1, sw2 = conn_reader.transmit(apdu)
        print(f"\nsw1 : 0x{sw1:02X} | sw2 : 0x{sw2:02X}")

        if sw1 == 0x90 and sw2 == 0x00:
            print(f"Succès !\nCrédit ajouté : {montant_recharge_euros} €")
        else:
            print(f"Erreur lors de la recharge du crédit: SW1 = {sw1}, SW2 = {sw2}")

    except ValueError:
        print("Veuillez entrer un montant valide.")
    except scardexcp.CardConnectionException as e:
        print("Erreur de connexion avec la carte : ", e)
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
            transferer_bonus(etu_num)
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

