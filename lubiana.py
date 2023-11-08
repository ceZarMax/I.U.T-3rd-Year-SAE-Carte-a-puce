

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
#------------------------------ PARTIE FONCTION-------------------------------
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


# Modification du menu
def print_menu():
	print (" 1 - Afficher la version de carte ")
	print (" 2 - Afficher les données de la carte ")
	print (" 3 - Attribuer la carte ")
	print (" 4 - Mettre le solde initial ")
	print (" 5 - Consulter le solde ")
	print (" 6 - Quitter ")

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
        elif cmd == 6:
            return
        else:
            print("Commande inconnue !")
        print("\n ---\n")
    print_menu()


if __name__ == '__main__':
	main()

#-----------------------------------------------------------------------------
#------------------------------ PARTIE CODE ----------------------------------
#-----------------------------------------------------------------------------


