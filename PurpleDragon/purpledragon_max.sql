-- phpMyAdmin SQL Dump
-- version 5.2.1deb1
-- https://www.phpmyadmin.net/
--
-- Hôte : localhost:3306
-- Généré le : jeu. 16 nov. 2023 à 15:24
-- Version du serveur : 10.11.3-MariaDB-1
-- Version de PHP : 8.2.7

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `purpledragon`
--

-- --------------------------------------------------------

--
-- Structure de la table `boissons`
--

CREATE TABLE `boissons` (
  `boisson_id` int(11) NOT NULL,
  `boisson_nom` varchar(20) NOT NULL,
  `nombres_ventes` int(11) NOT NULL,
  `montant_total` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `boissons`
--

INSERT INTO `boissons` (`boisson_id`, `boisson_nom`, `nombres_ventes`, `montant_total`) VALUES
(1, 'Café', 0, 0),
(2, 'Café long', 0, 0),
(3, 'Cappuccino', 1, 0.4),
(4, 'Café BIO', 0, 0),
(5, 'Chocolat chaud', 0, 0),
(6, 'Thé', 0, 0);

-- --------------------------------------------------------

--
-- Structure de la table `compte`
--

CREATE TABLE `compte` (
  `etu_num` int(11) NOT NULL,
  `opr_date` datetime NOT NULL,
  `opr_montant` decimal(15,2) DEFAULT 0.00,
  `opr_libelle` varchar(50) DEFAULT NULL,
  `type_operation` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `compte`
--

INSERT INTO `compte` (`etu_num`, `opr_date`, `opr_montant`, `opr_libelle`, `type_operation`) VALUES
(1, '2023-03-09 09:15:34', 1.00, 'Initial', 'Bonus'),
(1, '2023-11-16 16:20:43', 0.40, 'Cappuccino', 'Dépense'),
(2, '2023-05-09 11:18:32', 1.00, 'Blague marrante durant un cours', 'Bonus'),
(2, '2023-05-16 08:23:32', 1.00, 'Inital', 'Bonus'),
(2, '2023-07-04 15:24:35', 1.00, 'bonne initiative', 'Bonus'),
(3, '2023-05-18 15:26:38', 1.00, 'initial', 'Bonus'),
(4, '2023-07-13 15:27:04', 1.00, 'intiial', 'Bonus');

-- --------------------------------------------------------

--
-- Structure de la table `etudiant`
--

CREATE TABLE `etudiant` (
  `etu_num` int(11) NOT NULL,
  `etu_nom` varchar(255) DEFAULT NULL,
  `etu_prenom` varchar(255) DEFAULT NULL,
  `etu_solde` float(99) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `etudiant`
--

INSERT INTO `etudiant` (`etu_num`, `etu_nom`, `etu_prenom`, `etu_solde`) VALUES
(1, 'Arvin-Berod', 'Maxence', 0),
(2, 'Hubert', 'Quentin', 0),
(3, 'El Beki', 'Sohayb', 0),
(4, 'Girault', 'Adrien', 0);

-- --------------------------------------------------------

--
-- Structure de la table `type`
--

CREATE TABLE `type` (
  `type_operation` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `type`
--

INSERT INTO `type` (`type_operation`) VALUES
('Bonus'),
('Bonus transféré'),
('Dépense'),
('Recharge');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `boissons`
--
ALTER TABLE `boissons`
  ADD PRIMARY KEY (`boisson_id`);

--
-- Index pour la table `compte`
--
ALTER TABLE `compte`
  ADD PRIMARY KEY (`etu_num`,`opr_date`),
  ADD KEY `type_operation` (`type_operation`);

--
-- Index pour la table `etudiant`
--
ALTER TABLE `etudiant`
  ADD PRIMARY KEY (`etu_num`);

--
-- Index pour la table `type`
--
ALTER TABLE `type`
  ADD PRIMARY KEY (`type_operation`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `etudiant`
--
ALTER TABLE `etudiant`
  MODIFY `etu_num` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `compte`
--
ALTER TABLE `compte`
  ADD CONSTRAINT `compte_ibfk_1` FOREIGN KEY (`etu_num`) REFERENCES `etudiant` (`etu_num`),
  ADD CONSTRAINT `compte_ibfk_2` FOREIGN KEY (`type_operation`) REFERENCES `type` (`type_operation`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
