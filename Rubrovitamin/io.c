// fichier "io.c"
//---------------
// lecture et écriture d'octets en t=0
// prototype des fonctions définies dans ce fichier :
// uint8_t recbytet0();		// reçoit un octet t=0
// void sendbytet0(uint8_t);	// émet un octet t=0
//
// Les entrées-sorties sont synchronisées sur l'horloge externe.
// Ce programme utilise le compteur asynchrone TCNT2 pour fonctionner y compris lorsque 
// le cpu fonctionne sur l'horloge interne à 8 MHz.
//

// Corrige pour fonctionner avec les lecteurs "watchdata" qui ont une fréquence trop faible
// Le problème était dû une mauvaise initialisation du compteur asynchrone TCNT2
// En répétant l'affectation TCNT2=0, cela corrige le problème
//
#include <inttypes.h>
#include <avr/io.h>

// un bit tous les 372 clocks -- 1 etu = 372 clock de l'entrée clock externe
// Un etu (elementary time unit) fait théoriquement 372 coups d'horloge externe, soit
// environ 46 itérations du compteur CNT2 cadencé à CK/8
// 8 * 46.5 = 372
// 8 * 46 =  368	cette valeur semble convenir sur tous les lecteurs
// La fréquence standard des lecteurs est de 3.58 MHz = 104uS pour 372 cycles = 9600 bauds
// la plupart des lecteurs ont une fréquence plus élevée, de 3,7 à 4,7 MHz.

// broche I/O sur le port b
#define IOPIN	4

// envoi d'un bit sur le lien série
static void sendbit(uint8_t b)
{
	uint8_t outB;
	// calcule la valeur à sortir
	outB=(b&1)<<IOPIN;
	// attend la fin de l'envoi de l'octet précédent
	do; while (TCNT2<46);
	// écriture du bit
	PORTB=outB;	// pendant les 4 clocks dispos de l'horloge externe
	// relance le compteur
	TCNT2=0;
	TCNT2=0;	// /!\ nécessaire si la fréquence du lecteur est trop faible
}

// envoi d'un octet sur le lien série
void sendbytet0(uint8_t b)
{
	uint8_t i;	// compteur
	uint8_t p;	// parité
	uint8_t b_save;	// valeur sauvegardée en cas d'erreur
	
	b_save=b;
	TCCR2B=2;	// lance le compteur sur CK/8
	TCNT2=40;	// initialise TCNT2 pour attente lors du premier envoi
reenvoyer:
	PORTB|=1<<IOPIN;	// affecter la valeur
	DDRB|=1<<IOPIN;		// avant de positionner le port en sortie
	// bit start
	sendbit(0);
	p=0;			// initialisation de la parité
	for (i=0;i<8;i++)
	{	// boucle d'émission des 8 bits de l'octet
		sendbit(b);
		p^=b;
		b>>=1;
	}
	sendbit(p);	// bit de parité
	sendbit(1);	// bit stop
	do; while (TCNT2<46);	// attendre fin du bit stop 
	// commuter en mode entrée pour lire si le lecteur demande la réémission
	DDRB&=~(1<<IOPIN);
	PORTB&=~(1<<IOPIN);
	do; while(TCNT2<93);	// attendre encore 1 etu
	// lire le signal d'erreur
	if ((PINB&(1<<IOPIN))==0)
	{ 	// si on lit 0
		do; while ((PINB&(1<<IOPIN))==0);	// attendre la fin du signal d'erreur
		TCNT2=22;	// positionner le compteur pour attendre encore 1/2 etu avant envoi
		b=b_save;	// restaurer l'octet à envoyer
		goto reenvoyer;
	}
	TCCR2B=0;	// arrête le compteur
}


// lecture d'un bit
// rend 0 ou 0x80
static uint8_t getbit()
{
	uint8_t b;
	// attendre la fin du bit précédent
	do; while (TCNT2<46);
	TCNT2=0;
	TCNT2=0;	// réinitialise le compteur
	// vote majoritaire sur lecture à trois instants
	do; while (TCNT2<12);
	b=(PINB&(1<<IOPIN));
	do; while (TCNT2<23);
	b+=(PINB&(1<<IOPIN));
	do; while (TCNT2<34);
	b+=(PINB&(1<<IOPIN));	// le bit reçu est en position IOPIN+1 si la somme des trois bits est >=2
	// positionner le bit reçu en b7
	return (b<<(6-IOPIN))&0x80;
}

// réception d'un octet
uint8_t recbytet0()
{
	uint8_t i;	// compteur
	uint8_t r;	// résultat
	uint8_t p;	// parité
	uint8_t b;	// bit reçu
	
	TCCR2B=2;	// démarre CNT2 sur CKEXT/8
relire:
	DDRB&=~(1<<IOPIN);		// mode entrée sur pb4
	PORTB|=(1<<IOPIN);		// pull-up sur IOPIN
	r=0;
	// attendre le bit start
	do; while ((PINB&(1<<IOPIN))!=0);
	do; while ((PINB&(1<<IOPIN))!=0);	// anti rebond
	TCNT2=0;	// initialisation double du compteur
	TCNT2=0;
	p=0;
	for (i=0;i<8;i++)
	{	// boucle de lecture des 8 bits d'un octet lsb first
		b=getbit();
		r=(r>>1)+b;
		p^=b;
	}
	p^=getbit();	// p contient 0x80 si erreur de parité
	// attendre la fin du bit de parité + 1 etu 
	do; while (TCNT2<93);
	// si erreur de parité, demander une réémission en mettant la ligne à 0 pendant environ 1.5 etu
	if (p)
	{

		PORTB&=~(1<<IOPIN);	// signal 0
		DDRB|=(1<<IOPIN);	// sortie
		do; while (TCNT2<162);	// pendant 1.5 etu
		goto relire;
	}
	else
	{
		// sinon, attendre  1 etu du bit stop
		do; while (TCNT2<139);
	}
	TCCR2B=0;	// arrêter le compteur
	return r;
}


