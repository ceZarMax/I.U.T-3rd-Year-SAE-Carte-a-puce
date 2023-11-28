CREATE DATABASE IF NOT EXISTS purpledragon
DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE purpledragon;
CREATE TABLE etudiant(
etu_num INT AUTO_INCREMENT,
etu_nom VARCHAR(255),
etu_prenom VARCHAR(255),
etu_solde DECIMAL(15,2) NULL DEFAULT '0.00',
PRIMARY KEY(etu_num)
);
INSERT INTO etudiant (etu_num, etu_nom, etu_prenom, etu_solde) VALUES
(1, 'Arvin-Berod', 'Maxence', 1.00),
(2, 'Hubert', 'Quentin', 1.00),
(3, 'El Beki', 'Sohayb', 1.00),
(4, 'Girault', 'Adrien', 1.00);
CREATE TABLE type(
type_operation VARCHAR(255),
PRIMARY KEY(type_operation)
);
INSERT INTO type (type_operation)
VALUES ('Bonus'), ('Recharge'), ('Dépense'), ('Bonus transféré');
CREATE TABLE compte(
etu_num INT,
opr_date DATETIME,
opr_montant DECIMAL(15,2) NULL DEFAULT '0.00',
opr_libelle VARCHAR(50),
type_operation VARCHAR(255) NOT NULL,
PRIMARY KEY(etu_num, opr_date),
FOREIGN KEY(etu_num) REFERENCES etudiant(etu_num),
FOREIGN KEY(type_operation) REFERENCES type(type_operation)
);
INSERT INTO compte (etu_num, opr_date, opr_montant, opr_libelle, type_operation) VALUES
(1, '2023-03-09 09:15:34', '1.00', 'Initial', 'Bonus'),
(1, '2023-05-15 15:18:44', '-0.20', 'Cafe', 'Dépense'),
(1, '2023-07-11 11:14:05', '-0.20', 'Chocolat', 'Dépense'),
(1, '2023-07-24 15:20:20', '-0.20', 'Café', 'Dépense'),
(2, '2023-05-09 11:18:32', '1.00', 'Blague marrante durant un cours', 'Bonus'),
(2, '2023-05-16 08:23:32', '1.00', 'Inital', 'Bonus'),
(2, '2023-07-04 15:24:35', '1.00', 'bonne initiative', 'Bonus'),
(2, '2023-07-06 15:24:35', '-0.20', 'Thé', 'Dépense'),
(2, '2023-07-26 15:23:32', '1.00', 'Belle présentation', 'Bonus'),
(3, '2023-05-18 15:26:38', '1.00', 'initial', 'Bonus'),
(4, '2023-07-13 15:27:04', '1.00', 'intiial', 'Bonus'),
(4, '2023-07-21 13:10:40', '-0.20', 'Café', 'Dépense');
