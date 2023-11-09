

# ---------------------------------------------------------

# Importation des librairies 

#---------------------------------------------------------

import smartcard.System as scardsys
import smartcard.util as scardutil
import smartcard.Exceptions as scardexcp

conn_reader = None

#---------------------------------------------------------

# LOGICIEL ADMINISTRATEUR LUBIANA

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

def print_version():
	apdu = [0x81, 0x00, 0x00, 0x00, 0x04] # Instruction à transmettre à la carte
	data, sw1, sw2 = conn_reader.transmit(apdu)
	if(sw1 != 0x90 and sw2 != 0x00):
		print ("""
			sw1 : 0x%02X | 
			sw2 : 0x%02X | 
			Version de la carte : erreur de lecture version""" % (sw1,sw2))
	str = ""
	for e in data:
		str += chr(e)
	print ("""
		sw1 : 0x%02X | 
		sw2 : 0x%02X | 
		Version de la carte : %s""" % (sw1,sw2,str))
	return

def print_nom():
    apdu = [0x81, 0x02, 0x00, 0x00, 0x00] # Instruction à transmettre à la carte
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
        Nom : %s""" % (sw1,sw2,str))    
    return

def print_prenom():
    apdu = [0x81, 0x04, 0x00, 0x00, 0x00] # Instruction à transmettre à la carte
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
        Prénom : %s""" % (sw1,sw2,str))    
    return

def print_birth():
    apdu = [0x81, 0x06, 0x00, 0x00, 0x00] # Instruction à transmettre à la carte
    data, sw1, sw2 = conn_reader.transmit(apdu) # Envoyer la commande à la carte et récupérer les données, ainsi que les codes SW1 et SW2 en retour
    print ("""
        sw1 : 0x%02X | 
        sw2 : 0x%02X |""" % (sw1,sw2)) # Si erreur ici lors de l'éxécutio c'est normal
    apdu[4] = sw2 # Met à jour le cinquième octet de l'instruction qui correspond à l'octet SW2
    data, sw1, sw2 = conn_reader.transmit(apdu) # On renvoie la commande et on récupère ses données
    

    str = ""
    for e in data:
        str += chr(e)
        birthdate_formatted = f"{str[:2]}/{str[2:4]}/{str[4:]}" # Afficher la date de naissance avec des /
    print ("""
        sw1 : 0x%02X | 
        sw2 : 0x%02X | 
        Date de naissance : %s""" % (sw1,sw2,birthdate_formatted))   
    return
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
#------------------------------ PARTIE ECRIRE---------------------------------
#-----------------------------------------------------------------------------
def intro_nom():
    apdu = [0x81, 0x01, 0x00, 0x00]

    # Saisie du nom
    nom = input("Saisissez le Nom de l'élève : ")
    length_nom = len(nom)
    apdu.append(length_nom)
    for e in nom:
        apdu.append(ord(e))

    print(apdu)

    try:
        data, sw1, sw2 = conn_reader.transmit(apdu)
        print(f"\nsw1 : 0x{sw1:02X} | sw2 : 0x{sw2:02X}")
        if sw1 == 0x90:
            print(f"Succès !\nNom de l'élève : {nom}")
        else:
            print(f"Erreur : {sw1}")
    except scardexcp.CardConnectionException as e:
        print("Erreur : ", e)
    return

def intro_prenom():
    apdu = [0x81, 0x03, 0x00, 0x00]

    # Saisie du nom
    prenom = input("Saisissez le Préom de l'élève : ")
    length_prenom = len(prenom)
    apdu.append(length_prenom)
    for e in prenom:
        apdu.append(ord(e))

    print(apdu)

    try:
        data, sw1, sw2 = conn_reader.transmit(apdu)
        print(f"\nsw1 : 0x{sw1:02X} | sw2 : 0x{sw2:02X}")
        if sw1 == 0x90:
            print(f"Succès !\nPrénom de l'élève : {prenom}")
        else:
            print(f"Erreur : {sw1}")
    except scardexcp.CardConnectionException as e:
        print("Erreur : ", e)
    return


def intro_birth():
    apdu = [0x81, 0x05, 0x00, 0x00]

    # Saisie du nom
    birth = input("Saisissez la date de naissance (Format : JJMMAAAA) : ")
    length_bith = len(birth)
    apdu.append(length_bith)
    for e in birth:
        apdu.append(ord(e))

    print(apdu)

    birthdate_formatted = f"{birth[:2]}/{birth[2:4]}/{birth[4:]}"

    try:
        data, sw1, sw2 = conn_reader.transmit(apdu)
        print(f"\nsw1 : 0x{sw1:02X} | sw2 : 0x{sw2:02X}")
        if sw1 == 0x90:
            print(f"Succès !\nDate de naissance : {birthdate_formatted}")
        else:
            print(f"Erreur : {sw1}")
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

  ____                              _        _____           _                           
 |  _ \                            | |      |  __ \         | |                          
 | |_) | ___  _ __ _ __   ___    __| | ___  | |__) |___  ___| |__   __ _ _ __ __ _  ___  
 |  _ < / _ \| '__| '_ \ / _ \  / _` |/ _ \ |  _  // _ \/ __| '_ \ / _` | '__/ _` |/ _ \ 
 | |_) | (_) | |  | | | |  __/ | (_| |  __/ | | \ \  __/ (__| | | | (_| | | | (_| |  __/ 
 |____/ \___/|_|  |_| |_|\___|  \__,_|\___| |_|  \_\___|\___|_| |_|\__,_|_|  \__, |\___| 
                                                                              __/ |      
                                                                             |___/       
  _           _     _                                                                    
 | |         | |   (_)                                                                   
 | |    _   _| |__  _  __ _ _ __   __ _                                                  
 | |   | | | | '_ \| |/ _` | '_ \ / _` |                                                 
 | |___| |_| | |_) | | (_| | | | | (_| |                                                 
 |______\__,_|_.__/|_|\__,_|_| |_|\__,_|                                                 

 -- Version 1.00 --
 -- Auteur : Maxence, Adrien, Quentin -- \n \n""")

def print_data():
    print_nom()
    print_prenom()
    print_birth()

def assign_card():
    intro_nom()
    intro_prenom()
    intro_birth()

# Modification du menu
def print_menu():
    print (" 1 - Afficher la version de carte ")
    print (" 2 - Afficher les données de la carte ")
    print (" 3 - Attribuer la carte ")
    print (" 4 - Mettre le solde initial ")
    print (" 5 - Consulter le solde ")
    print (" 6 - Quitter ")

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------




#-----------------------------------------------------------------------------
#------------------------------ PARTIE MAIN ----------------------------------
#-----------------------------------------------------------------------------

def main():
    init_smart_card()
    print_hello_message()
    # Imprime l'ATR en utilisant la variable globale card_atr
    print("ATR (HEX) : ", scardutil.toHexString(card_atr))
    print("ATR (ASCII): ", scardutil.toASCIIString(card_atr), "\n")

    while True:
        print_menu()
        cmd = int(input("Choix : "))
        if cmd == 1:
            print_version()
        elif cmd == 2:
        	print_data()
        elif cmd == 3:
        	assign_card()
        elif cmd == 6:
            return
        else:
            print("Commande inconnue !")
        print("\n ---\n")
    print_menu()


if __name__ == '__main__':
	main()



