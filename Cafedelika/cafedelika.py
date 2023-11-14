

# ---------------------------------------------------------

# Importation des librairies 

#---------------------------------------------------------

import smartcard.System as scardsys
import smartcard.util as scardutil
import smartcard.Exceptions as scardexcp

import time

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


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
#------------------------------ PARTIE ECRIRE---------------------------------
#-----------------------------------------------------------------------------


# Fonction pour débiter la carte
def debiter():
    apdu = [0x82, 0x03, 0x00, 0x00, 0x02, 0x00, 0x14]

    try:
        data, sw1, sw2 = conn_reader.transmit(apdu)
        if sw1 == 0x90:
            print("Préparation de la boisson en cours...")

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
                                                                                                 

 -- Version 1.00 --
 -- "Un café... mais délicat"
 -- Auteur : Maxence -- \n \n""")



# Modification du menu
def print_menu():
    print (" 1 - Café (0.20€) ")
    print (" 2 - Chocolat chaud (0.20€) ")
    print (" 3 - Thé (0.20€) ")
    print (" 4 - Quitter ")

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
        if cmd == 1:
            debiter()
        elif cmd == 2:
            debiter()
        elif cmd == 3:
            debiter()
        elif cmd == 4:
            break  # Utilisez 'break' pour sortir de la boucle
        else:
            print("Commande inconnue !")
        print("\n ---\n")

    # Code à exécuter après la boucle
    print("Fermeture de l'application.")

if __name__ == "__main__":
    main()




