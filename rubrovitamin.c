#include <io.h>
#include <inttypes.h>
#include <avr/eeprom.h>

//------------------------------------------------
// Programme "rubrovitamin" pour carte à puce
// 
//------------------------------------------------


// déclaration des fonctions d'entrée/sortie définies dans "io.c"
void sendbytet0(uint8_t b);
uint8_t recbytet0(void);

// Définition de la version
#define size_ver 4
const char ver_str[size_ver] PROGMEM = "1.00";


// variables globales en static ram
uint8_t cla, ins, p1, p2, p3; // entête de commande
uint8_t sw1, sw2;   // status word

int taille;   // taille des données introduites -- est initialisé à 0 avant la boucle
#define MAXI 128  // taille maxi des données lues
uint8_t data[MAXI]; // données introduites
uint8_t nom[MAXI];
uint8_t prenom[MAXI];
uint8_t date[MAXI];

//------------------------------------------------
// Variables EEPROM
// 
//------------------------------------------------

#define MAX_PERSO 32
uint8_t ee_taille_perso EEMEM=0;
unsigned char ee_perso[MAX_PERSO] EEMEM;
//------------------------------------------------
//------------------------------------------------

// Procédure qui renvoie l'ATR
void atr(uint8_t n, char* hist)
{
  sendbytet0(0x3b); // définition du protocole
  
  n = 0xF0 + n  +1 ;
  sendbytet0(n);    // nombre d'octets d'historique
  sendbytet0(0x01); //TA 
  sendbytet0(0x05); //TB
  sendbytet0(0x05); //TC 
  sendbytet0(0x00); //TD protocole t=0
  sendbytet0(0x00); //CAT 

  while(n--)    // Boucle d'envoi des octets d'historique
    {
      sendbytet0(*hist++);
    }
}


// émission de la version
// t est la taille de la chaîne sv
void version()
{
      int i;
      // vérification de la taille
      if (p3!=size_ver)
      {
          sw1=0x6c; // taille incorrecte
          sw2=size_ver;    // taille attendue
          return;
      }
  sendbytet0(ins);  // acquittement
  // émission des données
  for(i=0;i<p3;i++)
      {
          sendbytet0(pgm_read_byte(ver_str+i));
      }
      sw1=0x90;
}


// Programme principal
//--------------------
int main(void)
{
  // initialisation des ports
  ACSR=0x80;
  PORTB=0xff;
  DDRB=0xff;
  DDRC=0xff;
  DDRD=0;
  PORTC=0xff;
  PORTD=0xff;
  ASSR=(1<<EXCLK)+(1<<AS2);
  //TCCR2A=0;
  //  ASSR|=1<<AS2;
  PRR=0x87;


  // ATR
  atr(11,"Hello scard");

  taille=0;
  sw2=0;    // pour éviter de le répéter dans toutes les commandes
  // boucle de traitement des commandes
// boucle de traitement des commandes
for(;;)
{
    // lecture de l'entête
    cla = recbytet0();
    ins = recbytet0();
    p1 = recbytet0();
    p2 = recbytet0();
    p3 = recbytet0();
    sw2 = 0;
    switch (cla)
    {
        case 0x81: // Classe de personnalisation
            switch (ins) {
                case 0:
                    version(4, "1.00");
                    break;

                case 1:
                    intro_data();
                    break;

                case 2:
                    lire_data();
                    break;

                case 3:
                    sortir_data();
                    break;

                case 4:
                    intro_perso();
                    break;

                case 5:
                    lire_perso(); // lire dans l'eeprom
                    break;

                case 6: // 80 06 00 00 07 "Maxence"
                    inserer_nom();
                    break;

                case 7: // Nouvelle commande pour insérer le prénom
                    inserer_prenom();
                    break;

                case 8: // Nouvelle commande pour insérer la date de naissance
                    inserer_date_naissance();
                    break;

                case 9: // Nouvelle commande pour lire les informations
                    lire_nom();
                    break;

                case 10: 
                    lire_prenom();
                    break;

                case 11:
                    lire_date();
                    break;

                default:
                    sw1 = 0x6d; // code erreur ins inconnu
            }
            break;

        default:
            sw1 = 0x6e; // code erreur classe inconnue
    }
    sendbytet0(sw1); // envoi du status word
    sendbytet0(sw2);
}

}