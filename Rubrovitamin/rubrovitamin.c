#include <io.h>
#include <inttypes.h>
#include <avr/eeprom.h> // EEPROM
#include <avr/pgmspace.h> // MEMOIRE FLASH


//------------------------------------------------
// Programme "rubrovitamin" pour carte à puce
// 
//------------------------------------------------


// déclaration des fonctions d'entrée/sortie définies dans "io.c"
void sendbytet0(uint8_t b);
uint8_t recbytet0(void);

// Définition de la version
#define size_ver 4
const char ver_str[size_ver] PROGMEM = "1.00"; // Tableau vers_str de 4 caractères qui stocke 1.00 dans la mémoire flash


// variables globales en static ram
uint8_t cla, ins, p1, p2, p3; // entête de commande
uint8_t sw1, sw2;   // status word

int taille;   // taille des données introduites -- est initialisé à 0 avant la boucle
#define MAXI 128  // taille maxi des données lues
uint8_t data_nom[MAXI];
uint8_t data_prenom[MAXI];
uint8_t data_birth[MAXI];

//------------------------------------------------
// Variables EEPROM
// 
//------------------------------------------------

#define MAX_PERSO 32 // Constante max de 32 OCTETS
uint8_t ee_taille_nom EEMEM=0; // Variable stockée dans l'EEPROM, stocke la taille de la chaine de car de NOM
unsigned char ee_nom[MAX_PERSO] EEMEM; // Tableau de caractères avec taille max 'MAX_PERSO(32octets)'. Stocké dans l'EEPROM. Stocke la chaine de car de nom
uint8_t ee_taille_prenom EEMEM=0;
unsigned char ee_prenom[MAX_PERSO] EEMEM;
uint8_t ee_taille_birth EEMEM=0;
unsigned char ee_birth[MAX_PERSO] EEMEM;
//------------------------------------------------
//------------------------------------------------


//------------------------------------------------
// ATR
// 
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

//------------------------------------------------
// Partie Classe de personnalisation
// 
//------------------------------------------------

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

void intro_nom(){ // Fonction de personnalisation, données écrite dans l'EEPROM
    int i;
    unsigned char data_nom[MAX_PERSO];
    // vérification de la taille
    if (p3>MAX_PERSO){
        sw1=0x6c; // P3 incorrect
        sw2=MAX_PERSO; // sw2 contient l'information de la taille correcte
        return;
    }
    sendbytet0(ins); // acquitement
    for(i=0;i<p3;i++){ // boucle d'envoi du message
        data_nom[i]=recbytet0();
    }
    eeprom_write_block(data_nom,ee_nom,p3);
    eeprom_write_byte(&ee_taille_nom,p3);
    sw1=0x90;
}

void lire_nom(){
    int i;
    char buffer[MAX_PERSO];
    uint8_t taille;
    taille=eeprom_read_byte(&ee_taille_nom);
    if (p3!=taille){
        sw1=0x6c; // P3 incorrect
        sw2=taille;
        return;
    }
    sendbytet0(ins);
    eeprom_read_block(buffer, ee_nom, taille);

    for (i=0;i<p3;i++){
        sendbytet0(buffer[i]);
    }
    sw1=0x90;
}

void intro_prenom(){ // Fonction de personnalisation, données écrite dans l'EEPROM
    int i;
    unsigned char data_prenom[MAX_PERSO];
    // vérification de la taille
    if (p3>MAX_PERSO){
        sw1=0x6c; // P3 incorrect
        sw2=MAX_PERSO; // sw2 contient l'information de la taille correcte
        return;
    }
    sendbytet0(ins); // acquitement
    for(i=0;i<p3;i++){ // boucle d'envoi du message
        data_prenom[i]=recbytet0();
    }
    eeprom_write_block(data_prenom,ee_prenom,p3);
    eeprom_write_byte(&ee_taille_prenom,p3);
    sw1=0x90;
}

void lire_prenom(){
    int i;
    char buffer[MAX_PERSO];
    uint8_t taille;
    taille=eeprom_read_byte(&ee_taille_prenom);
    if (p3!=taille){
        sw1=0x6c; // P3 incorrect
        sw2=taille;
        return;
    }
    sendbytet0(ins);
    eeprom_read_block(buffer, ee_prenom, taille);

    for (i=0;i<p3;i++){
        sendbytet0(buffer[i]);
    }
    sw1=0x90;
}

void intro_birth(){ // Fonction de personnalisation, données écrite dans l'EEPROM
    int i;
    unsigned char data_birth[MAX_PERSO];
    // vérification de la taille
    if (p3>MAX_PERSO){
        sw1=0x6c; // P3 incorrect
        sw2=MAX_PERSO; // sw2 contient l'information de la taille correcte
        return;
    }
    sendbytet0(ins); // acquitement
    for(i=0;i<p3;i++){ // boucle d'envoi du message
        data_birth[i]=recbytet0();
    }
    eeprom_write_block(data_birth,ee_birth,p3);
    eeprom_write_byte(&ee_taille_birth,p3);
    sw1=0x90;
}

void lire_birth(){
    int i;
    char buffer[MAX_PERSO];
    uint8_t taille;
    taille=eeprom_read_byte(&ee_taille_birth);
    if (p3!=taille){
        sw1=0x6c; // P3 incorrect
        sw2=taille;
        return;
    }
    sendbytet0(ins);
    eeprom_read_block(buffer, ee_birth, taille);

    for (i=0;i<p3;i++){
        sendbytet0(buffer[i]);
    }
    sw1=0x90;
}

//------------------------------------------------
// Partie Classe de gestion de paiement
// 
//------------------------------------------------

uint16_t solde EEMEM = 0;  // Définit une variable "solde" stockée en mémoire EEPROM, initialisée à 0.

void LectureSolde(){
    if(p3 != 2){
        sw1 = 0x6c;   // Si la taille des données attendues (p3) n'est pas de 2 octets, renvoie une erreur 0x6C avec le code d'erreur 2.
        sw2 = 2;
        return;      
    }
    sendbytet0(ins);  // Envoie un octet d'acquittement (ins) à la carte.

    // Lecture du solde depuis la mémoire EEPROM.
    uint16_t mot = eeprom_read_word(&solde);  // Lecture d'un mot de 16 bits (2 octets) depuis la mémoire EEPROM.

    // Envoi des octets du solde en deux parties : poids fort (high byte) suivi du poids faible (low byte).
    sendbytet0(mot >> 8);  // Envoie d'abord le bit de poids fort (8 bits de poids fort).
    sendbytet0(mot);       // Puis envoie le bit de poids faible (8 bits de poids faible).

    sw1 = 0x90;  // Indique le succès en définissant sw1 à 0x90.
}

void credit(){ // Créditer la carte lors d'un rechargement
    if(p3 != 2){
        sw1 = 0x6c ;
        sw2 = 2;
        return ;
    }
    sendbytet0(ins) ;
    uint16_t ajout = ((uint16_t)recbytet0() << 8) + (uint16_t)recbytet0();
    uint16_t solde_mot = eeprom_read_word(&solde) ;
    uint16_t montant = ajout + solde_mot ; // On ajoute le montant
    if(montant < ajout){ //il y a eu un debordement
        sw1 = 0x61 ;
        return ;
    }
    eeprom_write_word(&solde, montant) ;
    sw1 = 0x90 ;
}

void Depenser(){
    if(p3 != 2){
        sw1 = 0x6c ;
        sw2 = 2;
        return ;
    }
    sendbytet0(ins) ;
    uint16_t retrait = ((uint16_t)recbytet0()<<8) + (uint16_t)recbytet0() ;
    uint16_t solde_mot = eeprom_read_word(&solde) ;
    if(solde_mot < retrait){
        sw1 = 0x61 ; // solde insuffisant
        return;
    }
    uint16_t montant = solde_mot - retrait ; // On débite le montant
    eeprom_write_word(&solde, montant) ;
    sw1 = 0x90 ;
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
                    intro_nom();
                    break;

                case 2:
                    lire_nom();
                    break;

                case 3:
                    intro_prenom();
                    break;

                case 4:
                    lire_prenom();
                    break;

                case 5:
                    intro_birth();
                    break;

                case 6:
                    lire_birth();
                    break;

                default:
                    sw1 = 0x6d; // code erreur ins inconnu
            }
            break;

        case 0x82: // Classe de gestion de paiements
            switch (ins) {
                case 1:
                    LectureSolde();
                    break;

                case 2:
                    credit(); // créditer au format héxadécimal, ex (1€) = 0x64 soit 64 
                    break;

                case 3:
                    Depenser();
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