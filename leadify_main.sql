-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Erstellungszeit: 12. Jan 2026 um 12:32
-- Server-Version: 10.4.32-MariaDB
-- PHP-Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Datenbank: `leadify_main`
--

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `anrede`
--

CREATE TABLE `anrede` (
  `id` int(11) NOT NULL,
  `bezeichnung` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Daten für Tabelle `anrede`
--

INSERT INTO `anrede` (`id`, `bezeichnung`) VALUES
(2, 'Frau'),
(1, 'Herr');

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `ansprechpartner`
--

CREATE TABLE `ansprechpartner` (
  `id` int(11) NOT NULL,
  `anrede_id` int(11) NOT NULL,
  `vorname` varchar(60) NOT NULL,
  `nachname` varchar(60) NOT NULL,
  `email` varchar(160) NOT NULL,
  `telefon` varchar(40) NOT NULL,
  `position_id` int(11) NOT NULL,
  `firma_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Daten für Tabelle `ansprechpartner`
--

INSERT INTO `ansprechpartner` (`id`, `anrede_id`, `vorname`, `nachname`, `email`, `telefon`, `position_id`, `firma_id`) VALUES
(1, 2, 'Anna', 'Bender', 'anna.bender@urbanvision.de', '+49 791 7674084', 6, 1),
(2, 2, 'Melanie', 'Jäger', 'melanie.jaeger@urbanvision.de', '+49 89 5612695', 13, 1),
(3, 2, 'Maja', 'König', 'maja.koenig@beckerpartner.de', '+49 751 7613827', 1, 2),
(4, 1, 'Maximilian', 'Bender', 'maximilian.bender@designworks.de', '+49 761 6353600', 6, 3),
(5, 1, 'Markus', 'Albrecht', 'markus.albrecht@peakline.de', '+49 651 8936543', 11, 4),
(6, 2, 'Paulina', 'Huber', 'paulina.huber@peakline.de', '+49 211 4372548', 9, 4),
(7, 2, 'Sophie', 'Arnold', 'sophie.arnold@schmidtpartner.de', '+49 371 4412335', 10, 5),
(8, 2, 'Miriam', 'Pohl', 'miriam.pohl@schmidtpartner.de', '+49 641 2322388', 5, 5),
(9, 2, 'Paulina', 'Huber', 'paulina.huber@schmidtpartner.de', '+49 361 7869624', 2, 5),
(10, 2, 'Nadine', 'Schütte', 'nadine.schuette@lineworks.de', '+49 621 1186940', 5, 6),
(11, 1, 'Niklas', 'Huber', 'niklas.huber@lineworks.de', '+49 741 2964711', 3, 6),
(12, 1, 'Markus', 'Vogel', 'markus.vogel@nordmedia.de', '+49 751 8899843', 14, 7),
(13, 2, 'Melanie', 'Schuster', 'melanie.schuster@schwarzpartner.de', '+49 581 9973147', 10, 8),
(14, 1, 'Felix', 'Kraft', 'felix.kraft@tradingworks.de', '+49 381 8388170', 1, 9),
(15, 1, 'Sebastian', 'Bender', 'sebastian.bender@nordenergy.de', '+49 551 8708355', 4, 10),
(16, 2, 'Sophie', 'Hahn', 'sophie.hahn@nordenergy.de', '+49 421 4768218', 8, 10),
(17, 2, 'Lea', 'Schütte', 'lea.schuette@nordenergy.de', '+49 761 5283655', 14, 10),
(18, 1, 'Erik', 'Peters', 'erik.peters@muellerpartner.de', '+49 531 1538873', 14, 11),
(19, 1, 'Jonas', 'Voigt', 'jonas.voigt@muellerpartner.de', '+49 351 3912374', 13, 11),
(20, 1, 'Maximilian', 'Schütte', 'maximilian.schuette@healthworks.de', '+49 371 9508167', 2, 12),
(21, 2, 'Sabine', 'Bender', 'sabine.bender@sueddesign.de', '+49 611 1277797', 1, 13),
(22, 1, 'Jan', 'Weiß', 'jan.weiss@schmitzpartner.de', '+49 631 1837142', 4, 14),
(23, 1, 'Jonas', 'Huber', 'jonas.huber@schmitzpartner.de', '+49 371 2401627', 5, 14),
(24, 2, 'Carina', 'Peters', 'carina.peters@schmitzpartner.de', '+49 731 5591086', 15, 14),
(25, 1, 'Tobias', 'Lindner', 'tobias.lindner@bauworks.de', '+49 371 6619647', 7, 15),
(26, 1, 'Markus', 'Weiß', 'markus.weiss@bauworks.de', '+49 561 2241782', 4, 15),
(27, 1, 'Erik', 'Heinrich', 'erik.heinrich@bauworks.de', '+49 211 2139189', 10, 15),
(28, 2, 'Paulina', 'Schütte', 'paulina.schuette@quantumbau.de', '+49 791 3473352', 5, 16),
(29, 1, 'Erik', 'Schütz', 'erik.schuetz@quantumbau.de', '+49 521 6847825', 3, 16),
(30, 2, 'Laura', 'Voigt', 'laura.voigt@quantumbau.de', '+49 621 1699618', 9, 16),
(31, 2, 'Melanie', 'Seidel', 'melanie.seidel@bauerpartner.de', '+49 40 4998702', 1, 17),
(32, 2, 'Miriam', 'Arnold', 'miriam.arnold@bauerpartner.de', '+49 40 4652106', 6, 17),
(33, 1, 'David', 'Vogel', 'david.vogel@worldworks.de', '+49 581 2361726', 6, 18),
(34, 2, 'Paulina', 'Kraft', 'paulina.kraft@worldworks.de', '+49 721 8128840', 11, 18),
(35, 1, 'Lukas', 'Sommer', 'lukas.sommer@peakbau.de', '+49 721 1375807', 4, 19),
(36, 1, 'Niklas', 'Schuster', 'niklas.schuster@schneiderpartner.de', '+49 571 4179444', 7, 20),
(37, 2, 'Larissa', 'Hahn', 'larissa.hahn@maritimeworks.de', '+49 531 1374131', 5, 21),
(38, 1, 'Michael', 'Huber', 'michael.huber@neoworks.de', '+49 541 2277029', 7, 22),
(39, 2, 'Vanessa', 'Albrecht', 'vanessa.albrecht@neoworks.de', '+49 581 2919129', 12, 22),
(40, 1, 'Simon', 'Lorenz', 'simon.lorenz@schmidtpartner.de', '+49 221 8447955', 2, 23),
(41, 1, 'Felix', 'Nowak', 'felix.nowak@schmidtpartner.de', '+49 551 4282680', 2, 23),
(42, 1, 'Markus', 'Pohl', 'markus.pohl@schmidtpartner.de', '+49 711 7177981', 3, 23),
(43, 2, 'Miriam', 'Bender', 'miriam.bender@systemsworks.de', '+49 69 8446776', 10, 24),
(44, 2, 'Nina', 'Krämer', 'nina.kraemer@nordbau.de', '+49 211 7877655', 6, 25),
(45, 2, 'Sarah', 'Keller', 'sarah.keller@nordbau.de', '+49 371 9698179', 1, 25),
(46, 1, 'Sebastian', 'Böhm', 'sebastian.boehm@schulzpartner.de', '+49 621 4921530', 10, 26),
(47, 1, 'Maximilian', 'Böhm', 'maximilian.boehm@schulzpartner.de', '+49 621 5542259', 10, 26),
(48, 1, 'Jan', 'Haas', 'jan.haas@schulzpartner.de', '+49 571 7655566', 4, 26),
(49, 2, 'Julia', 'Kraft', 'julia.kraft@solutionsworks.de', '+49 741 6307340', 15, 27),
(50, 2, 'Nina', 'Arnold', 'nina.arnold@novasolutions.de', '+49 711 3195678', 12, 28),
(51, 2, 'Carina', 'Graf', 'carina.graf@wernerpartner.de', '+49 351 2382213', 8, 29),
(52, 1, 'Maximilian', 'König', 'maximilian.koenig@wernerpartner.de', '+49 571 7836692', 12, 29),
(53, 1, 'Matthias', 'Franke', 'matthias.franke@lineworks2.de', '+49 561 9713580', 12, 30),
(54, 2, 'Paulina', 'Kraft', 'paulina.kraft@peakdynamics.de', '+49 621 6204673', 2, 31),
(55, 2, 'Katharina', 'Weiß', 'katharina.weiss@peakdynamics.de', '+49 741 1266912', 9, 31),
(56, 2, 'Vanessa', 'Seidel', 'vanessa.seidel@wolfpartner.de', '+49 361 7262412', 2, 32),
(57, 1, 'Fabian', 'Voigt', 'fabian.voigt@logisticsworks.de', '+49 651 8877708', 14, 33),
(58, 2, 'Katharina', 'Kuhn', 'katharina.kuhn@logisticsworks.de', '+49 211 5608632', 11, 33),
(59, 2, 'Katharina', 'Seidel', 'katharina.seidel@logisticsworks.de', '+49 391 8863114', 7, 33),
(60, 2, 'Anna', 'Fuchs', 'anna.fuchs@omegaworld.de', '+49 761 2565982', 3, 34),
(61, 1, 'Sebastian', 'Schütz', 'sebastian.schuetz@omegaworld.de', '+49 761 3902292', 5, 34),
(62, 1, 'Matthias', 'Lorenz', 'matthias.lorenz@schmidtpartner.de', '+49 361 7405961', 10, 35),
(63, 2, 'Melanie', 'Brandt', 'melanie.brandt@analyticsworks.de', '+49 371 2756531', 14, 36),
(64, 2, 'Anna', 'Keller', 'anna.keller@blueworks.de', '+49 221 1465336', 11, 37),
(65, 1, 'Oliver', 'Marquardt', 'oliver.marquardt@blueworks.de', '+49 40 6099938', 5, 37),
(66, 2, 'Sophie', 'Hahn', 'sophie.hahn@blueworks.de', '+49 521 9247653', 5, 37),
(67, 1, 'Michael', 'Brandt', 'michael.brandt@wagnerpartner.de', '+49 711 5258933', 8, 38),
(68, 1, 'Erik', 'Jäger', 'erik.jaeger@analyticsworks.de', '+49 571 9826231', 12, 39),
(69, 2, 'Miriam', 'Haas', 'miriam.haas@analyticsworks.de', '+49 361 8787070', 9, 39),
(70, 2, 'Maja', 'Weiß', 'maja.weiss@nextlogistics.de', '+49 721 2255382', 8, 40),
(71, 1, 'Jonas', 'Krämer', 'jonas.kraemer@nextlogistics.de', '+49 551 4937850', 4, 40),
(72, 2, 'Sarah', 'Kuhn', 'sarah.kuhn@nextlogistics.de', '+49 791 8386123', 4, 40),
(73, 2, 'Carina', 'Schütte', 'carina.schuette@beckerpartner.de', '+49 721 6106055', 8, 41),
(74, 1, 'Leon', 'Schütte', 'leon.schuette@securityworks.de', '+49 721 3464524', 10, 42),
(75, 1, 'Michael', 'Franke', 'michael.franke@securityworks.de', '+49 741 7118710', 5, 42),
(76, 2, 'Lisa', 'Ulrich', 'lisa.ulrich@neoanalytics.de', '+49 361 3706992', 13, 43),
(77, 1, 'Michael', 'Haas', 'michael.haas@beckerpartner.de', '+49 89 6834189', 6, 44),
(78, 2, 'Laura', 'Albrecht', 'laura.albrecht@beckerpartner.de', '+49 751 5615582', 14, 44),
(79, 2, 'Johanna', 'Fuchs', 'johanna.fuchs@mediaworks.de', '+49 361 1997453', 6, 45),
(80, 2, 'Maja', 'Seidel', 'maja.seidel@mediaworks.de', '+49 621 8733363', 4, 45),
(81, 2, 'Lea', 'Schütte', 'lea.schuette@mediaworks.de', '+49 69 1461637', 3, 45),
(82, 2, 'Carina', 'Voigt', 'carina.voigt@blueworld.de', '+49 721 2529446', 3, 46),
(83, 1, 'Erik', 'Kuhn', 'erik.kuhn@weberpartner.de', '+49 381 5025902', 10, 47),
(84, 1, 'Simon', 'Nowak', 'simon.nowak@weberpartner.de', '+49 741 8255911', 8, 47),
(85, 2, 'Miriam', 'Huber', 'miriam.huber@weberpartner.de', '+49 351 5266040', 13, 47),
(86, 2, 'Paulina', 'Keller', 'paulina.keller@healthworks.de', '+49 731 3714728', 12, 48),
(87, 1, 'Fabian', 'Brandt', 'fabian.brandt@healthworks.de', '+49 761 7447229', 3, 48),
(88, 2, 'Sabine', 'Schuster', 'sabine.schuster@healthworks.de', '+49 791 8172800', 4, 48),
(89, 1, 'Andreas', 'Marquardt', 'andreas.marquardt@quantumanalytics.de', '+49 371 5224340', 7, 49),
(90, 2, 'Johanna', 'Hahn', 'johanna.hahn@neumannpartner.de', '+49 89 8223262', 9, 50),
(91, 1, 'Andreas', 'Hahn', 'andreas.hahn@tradingworks.de', '+49 761 4856140', 3, 51),
(92, 1, 'Matthias', 'Huber', 'matthias.huber@urbantrading.de', '+49 771 4625331', 10, 52),
(93, 1, 'Sebastian', 'Lorenz', 'sebastian.lorenz@urbantrading.de', '+49 781 4054684', 5, 52),
(94, 2, 'Claudia', 'Dietrich', 'claudia.dietrich@schmitzpartner.de', '+49 571 5916714', 9, 53),
(95, 2, 'Nina', 'Franke', 'nina.franke@bauworks.de', '+49 351 6879899', 7, 54),
(96, 2, 'Lea', 'Schütz', 'lea.schuetz@solarconsult.de', '+49 371 3971689', 5, 55),
(97, 2, 'Laura', 'Schütz', 'laura.schuetz@solarconsult.de', '+49 711 7715201', 12, 55),
(98, 1, 'Niklas', 'Nowak', 'niklas.nowak@muellerpartner.de', '+49 541 6755450', 3, 56),
(99, 1, 'Oliver', 'Weiß', 'oliver.weiss@muellerpartner.de', '+49 521 1519700', 4, 56),
(100, 2, 'Anna', 'Vogel', 'anna.vogel@mediaworks.de', '+49 651 4388739', 2, 57),
(101, 2, 'Katharina', 'Berger', 'katharina.berger@cloudbau.de', '+49 781 2617666', 11, 58),
(102, 2, 'Carina', 'Hahn', 'carina.hahn@kruegerpartner.de', '+49 421 8745706', 6, 59),
(103, 1, 'Michael', 'König', 'michael.koenig@kruegerpartner.de', '+49 791 3379767', 12, 59),
(104, 2, 'Anna', 'Kraft', 'anna.kraft@kruegerpartner.de', '+49 651 9573880', 15, 59),
(105, 2, 'Lea', 'Dietrich', 'lea.dietrich@designworks.de', '+49 391 8665742', 15, 60),
(106, 1, 'Markus', 'Reinhardt', 'markus.reinhardt@primetrading.de', '+49 231 4435662', 8, 61),
(107, 2, 'Larissa', 'Voigt', 'larissa.voigt@braunpartner.de', '+49 741 2379261', 8, 62),
(108, 1, 'Jonas', 'Huber', 'jonas.huber@foodsworks.de', '+49 381 8488518', 11, 63),
(109, 1, 'Felix', 'Berger', 'felix.berger@urbansolutions.de', '+49 581 9095833', 10, 64),
(110, 2, 'Claudia', 'Kraft', 'claudia.kraft@beckerpartner.de', '+49 641 9468007', 9, 65),
(111, 1, 'Leon', 'Vogel', 'leon.vogel@beckerpartner.de', '+49 391 2438822', 6, 65),
(112, 2, 'Julia', 'Arnold', 'julia.arnold@beckerpartner.de', '+49 631 3418319', 13, 65),
(113, 1, 'Andreas', 'Pohl', 'andreas.pohl@dynamicsworks.de', '+49 791 1115285', 11, 66),
(114, 1, 'Sebastian', 'Krämer', 'sebastian.kraemer@dynamicsworks.de', '+49 351 5766026', 3, 66),
(115, 1, 'Simon', 'Pohl', 'simon.pohl@bluefoods.de', '+49 351 7545833', 6, 67),
(116, 2, 'Sabine', 'Peters', 'sabine.peters@schmitzpartner.de', '+49 731 2568454', 12, 68),
(117, 2, 'Miriam', 'Marquardt', 'miriam.marquardt@schmitzpartner.de', '+49 781 5829806', 13, 68),
(118, 2, 'Claudia', 'Weiß', 'claudia.weiss@schmitzpartner.de', '+49 221 6388319', 9, 68),
(119, 2, 'Laura', 'Reinhardt', 'laura.reinhardt@designworks.de', '+49 351 1639972', 15, 69),
(120, 2, 'Kim', 'Nowak', 'kim.nowak@designworks.de', '+49 371 2686375', 14, 69),
(121, 2, 'Lisa', 'Lindner', 'lisa.lindner@peakconsult.de', '+49 741 1939361', 8, 70),
(122, 2, 'Vanessa', 'Peters', 'vanessa.peters@neumannpartner.de', '+49 751 5258484', 10, 71),
(123, 1, 'Maximilian', 'Pohl', 'maximilian.pohl@worksworks.de', '+49 40 5055169', 14, 72),
(124, 1, 'Niklas', 'Engel', 'niklas.engel@worksworks.de', '+49 211 1467941', 6, 72),
(125, 2, 'Larissa', 'Krämer', 'larissa.kraemer@worksworks.de', '+49 211 5831519', 5, 72),
(126, 1, 'Lukas', 'Marquardt', 'lukas.marquardt@alphaanalytics.de', '+49 621 4918348', 14, 73),
(127, 2, 'Lea', 'Albrecht', 'lea.albrecht@wolfpartner.de', '+49 221 7999835', 3, 74),
(128, 2, 'Miriam', 'Fuchs', 'miriam.fuchs@bauworks.de', '+49 391 6507439', 9, 75),
(129, 1, 'Sebastian', 'Berger', 'sebastian.berger@nordline.de', '+49 40 4058585', 11, 76),
(130, 2, 'Nadine', 'Nowak', 'nadine.nowak@nordline.de', '+49 631 9434762', 4, 76),
(131, 1, 'Lukas', 'Lorenz', 'lukas.lorenz@nordline.de', '+49 421 9962848', 1, 76),
(132, 2, 'Nadine', 'Keller', 'nadine.keller@muellerpartner.de', '+49 521 3112102', 2, 77),
(133, 2, 'Vanessa', 'Krämer', 'vanessa.kraemer@muellerpartner.de', '+49 521 8581724', 7, 77),
(134, 1, 'Matthias', 'Lindner', 'matthias.lindner@securityworks.de', '+49 89 2439255', 5, 78),
(135, 1, 'Oliver', 'Kuhn', 'oliver.kuhn@securityworks.de', '+49 791 7126253', 4, 78),
(136, 1, 'Lukas', 'Voigt', 'lukas.voigt@techline.de', '+49 511 5235923', 5, 79),
(137, 1, 'Oliver', 'Kraft', 'oliver.kraft@techline.de', '+49 661 6699120', 1, 79),
(138, 2, 'Paulina', 'Albrecht', 'paulina.albrecht@beckerpartner.de', '+49 761 4267821', 7, 80),
(139, 1, 'Leon', 'Kraft', 'leon.kraft@worldworks.de', '+49 771 5844948', 14, 81),
(140, 1, 'Lukas', 'Heinrich', 'lukas.heinrich@worldworks.de', '+49 89 6757761', 7, 81),
(141, 2, 'Katharina', 'Albrecht', 'katharina.albrecht@bluemedia.de', '+49 521 3614331', 6, 82),
(142, 2, 'Vanessa', 'Böhm', 'vanessa.boehm@schulzpartner.de', '+49 221 6484120', 1, 83),
(143, 1, 'Erik', 'Schuster', 'erik.schuster@schulzpartner.de', '+49 211 2924555', 8, 83),
(144, 1, 'Andreas', 'Pohl', 'andreas.pohl@schulzpartner.de', '+49 30 3164113', 12, 83),
(145, 1, 'Fabian', 'Weiß', 'fabian.weiss@worksworks2.de', '+49 441 5064921', 9, 84),
(146, 1, 'Markus', 'Albrecht', 'markus.albrecht@worksworks2.de', '+49 721 6466886', 5, 84),
(147, 1, 'Simon', 'Dietrich', 'simon.dietrich@worksworks2.de', '+49 721 2008692', 13, 84),
(148, 2, 'Claudia', 'Böhm', 'claudia.boehm@neosecurity.de', '+49 571 5231749', 10, 85),
(149, 2, 'Katharina', 'Keller', 'katharina.keller@neosecurity.de', '+49 531 6667841', 5, 85),
(150, 1, 'Andreas', 'Ott', 'andreas.ott@beckerpartner.de', '+49 631 6835026', 8, 86),
(151, 2, 'Maja', 'Arnold', 'maja.arnold@healthworks.de', '+49 741 8409037', 8, 87),
(152, 1, 'Jan', 'Brandt', 'jan.brandt@healthworks.de', '+49 361 8379954', 8, 87),
(153, 1, 'Matthias', 'Krämer', 'matthias.kraemer@healthworks.de', '+49 761 1342217', 14, 87),
(154, 2, 'Julia', 'Marquardt', 'julia.marquardt@urbanbau.de', '+49 361 9624791', 2, 88),
(155, 2, 'Julia', 'Lindner', 'julia.lindner@urbanbau.de', '+49 751 5667114', 1, 88),
(156, 2, 'Johanna', 'Hahn', 'johanna.hahn@urbanbau.de', '+49 741 1161108', 9, 88),
(157, 2, 'Julia', 'Keller', 'julia.keller@bauerpartner.de', '+49 761 8395501', 9, 89),
(158, 2, 'Julia', 'Schütte', 'julia.schuette@healthworks.de', '+49 661 9253937', 2, 90),
(159, 2, 'Melanie', 'Jäger', 'melanie.jaeger@greenbau.de', '+49 521 2969625', 5, 91),
(160, 2, 'Nina', 'Haas', 'nina.haas@richterpartner.de', '+49 221 4827652', 8, 92),
(161, 2, 'Sabine', 'Pohl', 'sabine.pohl@richterpartner.de', '+49 221 7691519', 2, 92),
(162, 1, 'Leon', 'Seidel', 'leon.seidel@richterpartner.de', '+49 731 1571154', 12, 92),
(163, 1, 'Fabian', 'Ulrich', 'fabian.ulrich@bauworks2.de', '+49 581 6792562', 15, 93),
(164, 2, 'Anna', 'Ott', 'anna.ott@bauworks2.de', '+49 441 9888790', 5, 93),
(165, 1, 'Daniel', 'Lorenz', 'daniel.lorenz@smartworks.de', '+49 771 6771539', 3, 94),
(166, 2, 'Maja', 'Keller', 'maja.keller@smartworks.de', '+49 441 7013362', 13, 94),
(167, 2, 'Lea', 'Sommer', 'lea.sommer@weberpartner.de', '+49 561 2664939', 10, 95),
(168, 2, 'Lea', 'Nowak', 'lea.nowak@weberpartner.de', '+49 581 4933292', 13, 95),
(169, 2, 'Laura', 'Schütte', 'laura.schuette@consultworks.de', '+49 611 1542600', 7, 96),
(170, 1, 'Daniel', 'Huber', 'daniel.huber@consultworks.de', '+49 641 8926347', 1, 96),
(171, 2, 'Vanessa', 'Dietrich', 'vanessa.dietrich@aerodynamics.de', '+49 511 4647150', 7, 97),
(172, 1, 'Oliver', 'Albrecht', 'oliver.albrecht@aerodynamics.de', '+49 221 8905839', 13, 97),
(173, 1, 'Daniel', 'König', 'daniel.koenig@wolfpartner.de', '+49 541 2577225', 12, 98),
(174, 2, 'Katharina', 'Albrecht', 'katharina.albrecht@worldworks.de', '+49 571 4692745', 2, 99),
(175, 1, 'Markus', 'Bender', 'markus.bender@bluedynamics.de', '+49 621 8795419', 2, 100),
(176, 1, 'Felix', 'Ulrich', 'felix.ulrich@bluedynamics.de', '+49 711 6709395', 7, 100),
(177, 1, 'Daniel', 'Schütz', 'daniel.schuetz@bluedynamics.de', '+49 781 1956315', 14, 100),
(178, 1, 'Markus', 'Marquardt', 'markus.marquardt@kleinpartner.de', '+49 631 8972387', 12, 101),
(179, 2, 'Sabine', 'Reinhardt', 'sabine.reinhardt@kleinpartner.de', '+49 761 2737237', 3, 101),
(180, 1, 'Markus', 'Lorenz', 'markus.lorenz@kleinpartner.de', '+49 741 2492036', 3, 101),
(181, 1, 'Paul', 'Pohl', 'paul.pohl@foodsworks.de', '+49 731 9012260', 6, 102),
(182, 1, 'Sebastian', 'Dietrich', 'sebastian.dietrich@foodsworks.de', '+49 421 5682752', 3, 102),
(183, 1, 'Leon', 'Huber', 'leon.huber@quantumworld.de', '+49 631 9236399', 8, 103),
(184, 1, 'David', 'Peters', 'david.peters@richterpartner.de', '+49 561 4284290', 8, 104),
(185, 1, 'Leon', 'Kuhn', 'leon.kuhn@richterpartner.de', '+49 551 8529044', 10, 104),
(186, 2, 'Maja', 'Albrecht', 'maja.albrecht@richterpartner.de', '+49 541 9367437', 6, 104),
(187, 1, 'Oliver', 'Graf', 'oliver.graf@analyticsworks2.de', '+49 771 2841440', 12, 105),
(188, 1, 'Niklas', 'Bender', 'niklas.bender@analyticsworks2.de', '+49 551 9512133', 14, 105),
(189, 2, 'Nadine', 'Dietrich', 'nadine.dietrich@analyticsworks2.de', '+49 361 7485961', 4, 105),
(190, 1, 'Lukas', 'Ulrich', 'lukas.ulrich@aerosystems.de', '+49 631 1758357', 10, 106),
(191, 1, 'Leon', 'Nowak', 'leon.nowak@aerosystems.de', '+49 751 9907853', 9, 106),
(192, 1, 'Jan', 'Nowak', 'jan.nowak@langepartner.de', '+49 221 2115067', 11, 107),
(193, 2, 'Sarah', 'Schuster', 'sarah.schuster@designworks.de', '+49 791 7607547', 13, 108),
(194, 1, 'Paul', 'Vogel', 'paul.vogel@designworks.de', '+49 30 2005239', 4, 108),
(195, 2, 'Melanie', 'Seidel', 'melanie.seidel@designworks.de', '+49 791 3268303', 6, 108),
(196, 1, 'Oliver', 'Schütte', 'oliver.schuette@alphaworks.de', '+49 371 4531402', 8, 109),
(197, 1, 'Paul', 'König', 'paul.koenig@zimmermannpartner.de', '+49 351 9513321', 6, 110),
(198, 1, 'Maximilian', 'Lindner', 'maximilian.lindner@industriesworks.de', '+49 761 5946706', 8, 111),
(199, 1, 'Maximilian', 'Kuhn', 'maximilian.kuhn@industriesworks.de', '+49 211 4071732', 13, 111),
(200, 2, 'Julia', 'Huber', 'julia.huber@industriesworks.de', '+49 231 7933692', 15, 111),
(201, 2, 'Sabine', 'Voigt', 'sabine.voigt@greensecurity.de', '+49 391 6653623', 6, 112),
(202, 2, 'Vanessa', 'Ott', 'vanessa.ott@greensecurity.de', '+49 641 7444022', 3, 112),
(203, 2, 'Nadine', 'Haas', 'nadine.haas@neumannpartner.de', '+49 40 8554232', 8, 113),
(204, 2, 'Lea', 'Berger', 'lea.berger@worldworks2.de', '+49 441 3105560', 13, 114),
(205, 2, 'Laura', 'Reinhardt', 'laura.reinhardt@primeline.de', '+49 231 9189796', 3, 115),
(206, 1, 'Niklas', 'Heinrich', 'niklas.heinrich@wernerpartner.de', '+49 351 3689019', 9, 116),
(207, 2, 'Maja', 'Albrecht', 'maja.albrecht@analyticsworks.de', '+49 641 7012871', 6, 117),
(208, 1, 'Maximilian', 'Kraft', 'maximilian.kraft@neodynamics.de', '+49 561 7292388', 11, 118),
(209, 1, 'Jonas', 'Weiß', 'jonas.weiss@neodynamics.de', '+49 561 2193999', 6, 118),
(210, 2, 'Melanie', 'Albrecht', 'melanie.albrecht@neodynamics.de', '+49 651 7103258', 10, 118),
(211, 1, 'Felix', 'Dietrich', 'felix.dietrich@braunpartner.de', '+49 771 8103838', 9, 119),
(212, 1, 'Markus', 'Peters', 'markus.peters@healthworks2.de', '+49 391 4228389', 10, 120),
(213, 1, 'Jan', 'Berger', 'jan.berger@healthworks2.de', '+49 741 2394196', 14, 120),
(214, 1, 'Matthias', 'Schütte', 'matthias.schuette@healthworks2.de', '+49 741 5189056', 7, 120),
(215, 2, 'Vanessa', 'Dietrich', 'vanessa.dietrich@suedworks.de', '+49 381 1841505', 13, 121),
(216, 2, 'Sophie', 'Schuster', 'sophie.schuster@suedworks.de', '+49 541 3309808', 5, 121),
(217, 1, 'Maximilian', 'Reinhardt', 'maximilian.reinhardt@beckerpartner.de', '+49 741 6629369', 2, 122),
(218, 2, 'Nina', 'Nowak', 'nina.nowak@analyticsworks.de', '+49 621 6551681', 13, 123),
(219, 2, 'Larissa', 'Lindner', 'larissa.lindner@analyticsworks.de', '+49 661 2045055', 5, 123),
(220, 2, 'Anna', 'Bender', 'anna.bender@analyticsworks.de', '+49 531 4562425', 8, 123),
(221, 2, 'Lisa', 'Weiß', 'lisa.weiss@alphaenergy.de', '+49 441 9306744', 14, 124),
(222, 2, 'Paulina', 'Ulrich', 'paulina.ulrich@alphaenergy.de', '+49 381 7303281', 13, 124),
(223, 1, 'Niklas', 'Krämer', 'niklas.kraemer@alphaenergy.de', '+49 791 4599720', 5, 124),
(224, 2, 'Sarah', 'Kuhn', 'sarah.kuhn@schmitzpartner.de', '+49 551 3965380', 14, 125),
(225, 2, 'Lisa', 'Peters', 'lisa.peters@visionworks.de', '+49 651 1605543', 14, 126),
(226, 2, 'Katharina', 'Weiß', 'katharina.weiss@visionworks.de', '+49 371 8286277', 14, 126),
(227, 1, 'Leon', 'Dietrich', 'leon.dietrich@metrosecurity.de', '+49 371 6915402', 11, 127),
(228, 1, 'Maximilian', 'Sommer', 'maximilian.sommer@schneiderpartner.de', '+49 221 5129447', 12, 128),
(229, 1, 'Jan', 'Heinrich', 'jan.heinrich@schneiderpartner.de', '+49 741 4351040', 14, 128),
(230, 2, 'Laura', 'Heinrich', 'laura.heinrich@schneiderpartner.de', '+49 611 9702037', 13, 128),
(231, 2, 'Claudia', 'Ulrich', 'claudia.ulrich@mediaworks.de', '+49 441 6065399', 6, 129),
(232, 2, 'Maja', 'Seidel', 'maja.seidel@mediaworks.de', '+49 791 2338951', 13, 129),
(233, 1, 'Michael', 'Schuster', 'michael.schuster@nextsolutions.de', '+49 231 7418529', 1, 130),
(234, 1, 'Felix', 'Bender', 'felix.bender@beckerpartner.de', '+49 721 1008009', 4, 131),
(235, 2, 'Katharina', 'Pohl', 'katharina.pohl@beckerpartner.de', '+49 381 9955489', 2, 131),
(236, 2, 'Nina', 'König', 'nina.koenig@beckerpartner.de', '+49 621 7803711', 1, 131),
(237, 1, 'Markus', 'Ott', 'markus.ott@systemsworks.de', '+49 661 7712494', 12, 132),
(238, 1, 'Niklas', 'Hahn', 'niklas.hahn@aerotrading.de', '+49 211 2354705', 9, 133),
(239, 2, 'Julia', 'Berger', 'julia.berger@braunpartner.de', '+49 581 9362975', 14, 134),
(240, 1, 'Lukas', 'Hahn', 'lukas.hahn@tradingworks.de', '+49 211 3347276', 2, 135),
(241, 2, 'Lisa', 'Vogel', 'lisa.vogel@urbandesign.de', '+49 571 4765902', 3, 136),
(242, 1, 'Lukas', 'Jäger', 'lukas.jaeger@fischerpartner.de', '+49 211 6431138', 10, 137),
(243, 2, 'Vanessa', 'Schütz', 'vanessa.schuetz@fischerpartner.de', '+49 441 7433480', 15, 137),
(244, 1, 'Maximilian', 'Lindner', 'maximilian.lindner@tradingworks.de', '+49 221 2023293', 13, 138),
(245, 1, 'Leon', 'Schütz', 'leon.schuetz@suedsystems.de', '+49 661 4223290', 4, 139),
(246, 1, 'Daniel', 'Weiß', 'daniel.weiss@langepartner.de', '+49 781 7155668', 13, 140),
(247, 2, 'Julia', 'Pohl', 'julia.pohl@worksworks.de', '+49 441 6309348', 4, 141),
(248, 2, 'Sophie', 'Krämer', 'sophie.kraemer@cloudfoods.de', '+49 521 6067322', 2, 142),
(249, 1, 'David', 'Sommer', 'david.sommer@cloudfoods.de', '+49 761 1126916', 15, 142),
(250, 1, 'Leon', 'Reinhardt', 'leon.reinhardt@cloudfoods.de', '+49 651 4749951', 11, 142),
(251, 1, 'Fabian', 'Sommer', 'fabian.sommer@schmidtpartner.de', '+49 40 7012106', 1, 143),
(252, 1, 'Michael', 'Krämer', 'michael.kraemer@healthworks3.de', '+49 641 6185693', 11, 144),
(253, 2, 'Nadine', 'Ulrich', 'nadine.ulrich@greenvision.de', '+49 641 1849791', 9, 145),
(254, 2, 'Nina', 'König', 'nina.koenig@greenvision.de', '+49 561 1809377', 15, 145),
(255, 1, 'Lukas', 'Nowak', 'lukas.nowak@schmitzpartner.de', '+49 571 5002083', 5, 146),
(256, 2, 'Sabine', 'Krämer', 'sabine.kraemer@schmitzpartner.de', '+49 521 1888118', 2, 146),
(257, 1, 'Erik', 'Krämer', 'erik.kraemer@schmitzpartner.de', '+49 561 7823877', 2, 146),
(258, 1, 'Lukas', 'Berger', 'lukas.berger@logisticsworks2.de', '+49 381 6086680', 9, 147),
(259, 2, 'Nina', 'Brandt', 'nina.brandt@logisticsworks2.de', '+49 621 2295403', 12, 147),
(260, 2, 'Julia', 'Huber', 'julia.huber@aerotrading.de', '+49 661 3789582', 2, 148),
(261, 1, 'Oliver', 'Sommer', 'oliver.sommer@schwarzpartner.de', '+49 741 5669368', 6, 149),
(262, 1, 'Oliver', 'Brandt', 'oliver.brandt@schwarzpartner.de', '+49 621 2615179', 13, 149),
(263, 1, 'Oliver', 'Fuchs', 'oliver.fuchs@bauworks2.de', '+49 511 8589336', 1, 150),
(264, 1, 'Thomas', 'Weiß', 'thomas.weiss@bauworks2.de', '+49 69 5836963', 7, 150),
(265, 2, 'Sarah', 'Schuster', 'sarah.schuster@bauworks2.de', '+49 781 9227870', 4, 150),
(266, 1, 'Paul', 'Kuhn', 'paul.kuhn@nexttrading.de', '+49 541 9452276', 10, 151),
(267, 1, 'Simon', 'Krämer', 'simon.kraemer@bauerpartner.de', '+49 391 3289450', 1, 152),
(268, 2, 'Laura', 'Heinrich', 'laura.heinrich@healthworks2.de', '+49 551 8926090', 6, 153),
(269, 1, 'Maximilian', 'Berger', 'maximilian.berger@greensystems.de', '+49 621 3055777', 10, 154),
(270, 2, 'Johanna', 'Weiß', 'johanna.weiss@greensystems.de', '+49 721 4779083', 13, 154),
(271, 2, 'Larissa', 'Weiß', 'larissa.weiss@schmidtpartner.de', '+49 371 1067718', 1, 155),
(272, 1, 'Jan', 'Berger', 'jan.berger@schmidtpartner.de', '+49 581 1017164', 14, 155),
(273, 2, 'Sophie', 'Vogel', 'sophie.vogel@schmidtpartner.de', '+49 441 6424902', 7, 155),
(274, 1, 'Michael', 'Jäger', 'michael.jaeger@worksworks3.de', '+49 541 1951719', 15, 156),
(275, 1, 'Simon', 'Marquardt', 'simon.marquardt@urbansolutions.de', '+49 621 5692391', 10, 157),
(276, 1, 'Lukas', 'Haas', 'lukas.haas@braunpartner.de', '+49 211 7062020', 7, 158),
(277, 2, 'Katharina', 'Weiß', 'katharina.weiss@braunpartner.de', '+49 551 3676161', 15, 158),
(278, 2, 'Maja', 'Kuhn', 'maja.kuhn@braunpartner.de', '+49 711 3784827', 2, 158),
(279, 2, 'Katharina', 'Engel', 'katharina.engel@dynamicsworks.de', '+49 231 2592731', 3, 159),
(280, 1, 'Andreas', 'Marquardt', 'andreas.marquardt@primehealth.de', '+49 351 6486870', 13, 160),
(281, 1, 'Markus', 'Heinrich', 'markus.heinrich@meyerpartner.de', '+49 531 9722964', 2, 161),
(282, 1, 'Markus', 'Schuster', 'markus.schuster@meyerpartner.de', '+49 441 9556370', 3, 161),
(283, 1, 'Sebastian', 'Schütz', 'sebastian.schuetz@meyerpartner.de', '+49 641 6251802', 11, 161),
(284, 1, 'Felix', 'Keller', 'felix.keller@healthworks3.de', '+49 641 9758408', 9, 162),
(285, 2, 'Sabine', 'Vogel', 'sabine.vogel@suedconsult.de', '+49 721 2043290', 2, 163),
(286, 1, 'Sebastian', 'Peters', 'sebastian.peters@richterpartner.de', '+49 421 9437563', 6, 164),
(287, 2, 'Paulina', 'König', 'paulina.koenig@richterpartner.de', '+49 531 9322228', 1, 164),
(288, 2, 'Claudia', 'Bender', 'claudia.bender@richterpartner.de', '+49 361 1946432', 2, 164),
(289, 1, 'Maximilian', 'Krämer', 'maximilian.kraemer@foodsworks2.de', '+49 381 6878096', 14, 165),
(290, 2, 'Carina', 'Keller', 'carina.keller@foodsworks2.de', '+49 631 7997990', 3, 165),
(291, 1, 'Felix', 'Lorenz', 'felix.lorenz@smartenergy.de', '+49 541 5563435', 1, 166),
(292, 2, 'Johanna', 'Weiß', 'johanna.weiss@smartenergy.de', '+49 551 6107750', 15, 166),
(293, 2, 'Anna', 'König', 'anna.koenig@hoffmannpartner.de', '+49 541 4923248', 7, 167),
(294, 1, 'Simon', 'Weiß', 'simon.weiss@hoffmannpartner.de', '+49 771 9131319', 7, 167),
(295, 2, 'Miriam', 'Hahn', 'miriam.hahn@dynamicsworks2.de', '+49 771 9008940', 6, 168),
(296, 2, 'Melanie', 'Kuhn', 'melanie.kuhn@smartanalytics.de', '+49 631 3763946', 1, 169),
(297, 1, 'Sebastian', 'Keller', 'sebastian.keller@smartanalytics.de', '+49 541 1598728', 9, 169),
(298, 1, 'Oliver', 'Ott', 'oliver.ott@smartanalytics.de', '+49 381 2025060', 11, 169),
(299, 1, 'Matthias', 'Krämer', 'matthias.kraemer@schulzpartner.de', '+49 511 6897363', 6, 170),
(300, 2, 'Sarah', 'Kraft', 'sarah.kraft@logisticsworks.de', '+49 521 7066210', 13, 171),
(301, 2, 'Miriam', 'Engel', 'miriam.engel@logisticsworks.de', '+49 40 8206761', 10, 171),
(302, 2, 'Kim', 'Graf', 'kim.graf@logisticsworks.de', '+49 741 6556063', 3, 171),
(303, 1, 'Daniel', 'Krämer', 'daniel.kraemer@cloudanalytics.de', '+49 511 7164584', 1, 172),
(304, 2, 'Julia', 'Huber', 'julia.huber@cloudanalytics.de', '+49 421 9253137', 6, 172),
(305, 2, 'Maja', 'Krämer', 'maja.kraemer@muellerpartner.de', '+49 40 2513320', 13, 173),
(306, 1, 'Simon', 'Böhm', 'simon.boehm@logisticsworks3.de', '+49 211 4827481', 10, 174),
(307, 1, 'Markus', 'Kuhn', 'markus.kuhn@neologistics.de', '+49 361 2618157', 13, 175),
(308, 2, 'Carina', 'Kuhn', 'carina.kuhn@fischerpartner.de', '+49 391 8246846', 4, 176),
(309, 2, 'Sarah', 'Albrecht', 'sarah.albrecht@solutionsworks.de', '+49 561 8515825', 3, 177),
(310, 1, 'Thomas', 'Reinhardt', 'thomas.reinhardt@solarmaritime.de', '+49 641 9711530', 3, 178),
(311, 2, 'Johanna', 'Ott', 'johanna.ott@solarmaritime.de', '+49 791 2069129', 3, 178),
(312, 1, 'Daniel', 'Weiß', 'daniel.weiss@solarmaritime.de', '+49 611 4273750', 11, 178),
(313, 2, 'Laura', 'Huber', 'laura.huber@richterpartner.de', '+49 711 1115345', 4, 179),
(314, 1, 'Daniel', 'Schütz', 'daniel.schuetz@logisticsworks.de', '+49 531 9052770', 12, 180),
(315, 1, 'Leon', 'Bender', 'leon.bender@solarvision.de', '+49 651 2707783', 8, 181),
(316, 2, 'Miriam', 'Nowak', 'miriam.nowak@solarvision.de', '+49 631 2038855', 13, 181),
(317, 2, 'Paulina', 'Ott', 'paulina.ott@solarvision.de', '+49 381 5622207', 13, 181),
(318, 2, 'Sophie', 'Keller', 'sophie.keller@bauerpartner.de', '+49 571 3672715', 2, 182),
(319, 1, 'Leon', 'Brandt', 'leon.brandt@bauerpartner.de', '+49 211 6602525', 6, 182),
(320, 2, 'Johanna', 'Hahn', 'johanna.hahn@lineworks.de', '+49 40 5413703', 10, 183),
(321, 2, 'Sarah', 'Krämer', 'sarah.kraemer@metroindustries.de', '+49 231 4394367', 4, 184),
(322, 1, 'Matthias', 'Nowak', 'matthias.nowak@hartmannpartner.de', '+49 531 7765612', 5, 185),
(323, 1, 'Michael', 'Haas', 'michael.haas@hartmannpartner.de', '+49 791 6629043', 3, 185),
(324, 1, 'Thomas', 'Ulrich', 'thomas.ulrich@hartmannpartner.de', '+49 221 4018869', 4, 185),
(325, 1, 'Niklas', 'Brandt', 'niklas.brandt@mediaworks2.de', '+49 551 1838758', 14, 186),
(326, 1, 'Leon', 'Hahn', 'leon.hahn@mediaworks2.de', '+49 741 7765341', 2, 186),
(327, 2, 'Lea', 'Kraft', 'lea.kraft@solarindustries.de', '+49 621 4907052', 3, 187),
(328, 1, 'Tobias', 'Bender', 'tobias.bender@langepartner.de', '+49 721 3694706', 14, 188),
(329, 1, 'Michael', 'Jäger', 'michael.jaeger@langepartner.de', '+49 231 1876632', 13, 188),
(330, 2, 'Kim', 'Ott', 'kim.ott@tradingworks2.de', '+49 781 1627342', 14, 189),
(331, 2, 'Larissa', 'Hahn', 'larissa.hahn@tradingworks2.de', '+49 791 3418803', 5, 189),
(332, 1, 'Michael', 'Schütte', 'michael.schuette@tradingworks2.de', '+49 791 6293415', 2, 189),
(333, 2, 'Vanessa', 'Kraft', 'vanessa.kraft@smarthealth.de', '+49 381 3164157', 3, 190),
(334, 1, 'Daniel', 'Ulrich', 'daniel.ulrich@smarthealth.de', '+49 421 9423422', 14, 190),
(335, 2, 'Maja', 'Sommer', 'maja.sommer@wernerpartner.de', '+49 221 4977510', 9, 191),
(336, 1, 'Tobias', 'Voigt', 'tobias.voigt@wernerpartner.de', '+49 721 9941202', 13, 191),
(337, 2, 'Kim', 'Voigt', 'kim.voigt@wernerpartner.de', '+49 651 2157790', 3, 191),
(338, 1, 'Oliver', 'Engel', 'oliver.engel@maritimeworks2.de', '+49 231 2082654', 13, 192),
(339, 1, 'Matthias', 'Schütz', 'matthias.schuetz@quantumtrading.de', '+49 651 3707275', 11, 193),
(340, 1, 'Erik', 'Hahn', 'erik.hahn@hoffmannpartner.de', '+49 69 2765512', 7, 194),
(341, 1, 'Erik', 'Haas', 'erik.haas@hoffmannpartner.de', '+49 69 5056431', 12, 194),
(342, 1, 'Fabian', 'Lorenz', 'fabian.lorenz@worksworks.de', '+49 621 1206535', 14, 195),
(343, 2, 'Sophie', 'Lorenz', 'sophie.lorenz@neomaritime.de', '+49 741 9782609', 14, 196),
(344, 1, 'Markus', 'Bender', 'markus.bender@neomaritime.de', '+49 571 3757828', 10, 196),
(345, 2, 'Claudia', 'Bender', 'claudia.bender@neomaritime.de', '+49 441 9437671', 12, 196),
(346, 1, 'Simon', 'Böhm', 'simon.boehm@wolfpartner.de', '+49 89 6273604', 2, 197),
(347, 1, 'Simon', 'Haas', 'simon.haas@energyworks.de', '+49 361 8999589', 15, 198),
(348, 2, 'Sarah', 'Graf', 'sarah.graf@cloudfoods.de', '+49 421 9571944', 4, 199),
(349, 1, 'Michael', 'Böhm', 'michael.boehm@wernerpartner.de', '+49 421 3807035', 14, 200),
(350, 1, 'Leon', 'Fuchs', 'leon.fuchs@wernerpartner.de', '+49 40 3477102', 8, 200);

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `benutzer`
--

CREATE TABLE `benutzer` (
  `benutzer_id` int(11) NOT NULL,
  `is_approved` tinyint(4) NOT NULL,
  `vorname` varchar(50) NOT NULL,
  `nachname` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `passwort_hash` varchar(100) NOT NULL,
  `rolle_id` int(11) NOT NULL,
  `anrede` int(11) NOT NULL,
  `session_token` varchar(255) DEFAULT NULL,
  `token_created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Daten für Tabelle `benutzer`
--

INSERT INTO `benutzer` (`benutzer_id`, `is_approved`, `vorname`, `nachname`, `email`, `passwort_hash`, `rolle_id`, `anrede`, `session_token`, `token_created_at`) VALUES
(1, 1, 'admin', 'admin', 'admin@leadify.com', '$2b$12$kpQADaFRDkUhGDpegsvRdeb.zqdOEDgH6vA25XL3mp5GsZHbmpR02', 0, 1, '2b1c8fa9-7fcd-481f-a9a4-530aa5842642', '2026-01-07 11:20:19'),
(2, 0, 'admin', 'konto', 'admin2@leadify.com', '', 0, 1, NULL, NULL),
(3, 1, 'Max', 'Mustermann', 'ausendienst@leadify.com', '$2b$12$39iutKR0m1VYuVojRN5Rs.zV0kvWPvimP4wc3C3pncwJKkJQgScgy', 1, 1, NULL, '2026-01-07 10:08:20'),
(4, 0, 'Martin', 'Musterdienst', 'ausendienst2@leadify.com', '', 1, 1, NULL, NULL),
(5, 0, 'Michael', 'Innendienst', 'innendienst@leadify.com', '', 2, 1, NULL, NULL),
(6, 0, 'Mareike', 'Musterfrau', 'innendienst2@leadify.com', '', 2, 2, NULL, NULL),
(69, 1, 'Denis', 'Russland', 'Russland@leadify.com', '$2b$12$ZQwOoB9vM9m3sff6izKOSOKVlvzjfW.mBmOvtKxcPBzVwkPElonRy', 4, 1, NULL, '2026-01-07 09:14:26');

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `bild`
--

CREATE TABLE `bild` (
  `bild_id` int(11) NOT NULL,
  `pfad` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Daten für Tabelle `bild`
--

INSERT INTO `bild` (`bild_id`, `pfad`) VALUES
(0, '\"KEIN BILD ANGEFÜGT\"');

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `branche`
--

CREATE TABLE `branche` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Daten für Tabelle `branche`
--

INSERT INTO `branche` (`id`, `name`) VALUES
(2, 'Bauwesen'),
(11, 'Bildung'),
(8, 'Einzelhandel'),
(9, 'Energie'),
(5, 'Finanzdienstleistungen'),
(4, 'Gesundheitswesen'),
(13, 'Immobilien'),
(1, 'IT-Dienstleistungen'),
(15, 'Lebensmittelproduktion'),
(7, 'Logistik'),
(6, 'Marketing & Werbung'),
(3, 'Maschinenbau'),
(14, 'Pharmaindustrie'),
(10, 'Telekommunikation'),
(12, 'Tourismus');

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `firma`
--

CREATE TABLE `firma` (
  `id` int(11) NOT NULL,
  `name` varchar(120) NOT NULL,
  `strasse` varchar(120) NOT NULL,
  `hausnummer` varchar(10) NOT NULL,
  `branche_id` int(11) NOT NULL,
  `ort_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Daten für Tabelle `firma`
--

INSERT INTO `firma` (`id`, `name`, `strasse`, `hausnummer`, `branche_id`, `ort_id`) VALUES
(1, 'UrbanVision KG', 'Feldweg', '69A', 11, 72),
(2, 'Becker & Partner AG', 'Lindenweg', '65', 1, 118),
(3, 'DesignWorks GmbH', 'Schillerstraße', '14A', 6, 81),
(4, 'PeakLine UG', 'Industriestraße', '56', 12, 98),
(5, 'Schmidt & Partner GmbH', 'Seestraße', '79B', 13, 70),
(6, 'LineWorks AG', 'Am Mühlengraben', '56B', 5, 7),
(7, 'NordMedia GmbH', 'Kirchweg', '107', 5, 118),
(8, 'Schwarz & Partner AG', 'Kirchweg', '97A', 10, 89),
(9, 'TradingWorks UG', 'Mittelweg', '44', 8, 56),
(10, 'NordEnergy KG', 'Ringstraße', '63', 6, 18),
(11, 'Müller & Partner AG', 'Marktplatz', '36B', 12, 55),
(12, 'HealthWorks KG', 'Eichenweg', '2B', 4, 6),
(13, 'SüdDesign AG', 'Kirchweg', '93A', 8, 97),
(14, 'Schmitz & Partner KG', 'Kirchweg', '89A', 11, 80),
(15, 'BauWorks GmbH', 'Am Mühlengraben', '102', 2, 22),
(16, 'QuantumBau KG', 'Kirchweg', '52', 5, 61),
(17, 'Bauer & Partner KG', 'Feldweg', '61B', 9, 31),
(18, 'WorldWorks UG', 'Dorfstraße', '96B', 6, 88),
(19, 'PeakBau UG', 'Am Mühlengraben', '35', 5, 31),
(20, 'Schneider & Partner KG', 'Parkallee', '93', 6, 24),
(21, 'MaritimeWorks KG', 'Eichenweg', '98', 4, 40),
(22, 'NeoWorks GmbH', 'Schillerstraße', '36B', 13, 73),
(23, 'Schmidt & Partner AG', 'Im Gewerbepark', '37', 14, 82),
(24, 'SystemsWorks GmbH', 'Berliner Allee', '30', 3, 114),
(25, 'NordBau UG', 'Hauptstraße', '91B', 3, 118),
(26, 'Schulz & Partner UG', 'Bahnhofstraße', '7B', 5, 33),
(27, 'SolutionsWorks AG', 'Schillerstraße', '14', 10, 36),
(28, 'NovaSolutions AG', 'Schillerstraße', '62A', 6, 112),
(29, 'Werner & Partner KG', 'Bahnhofstraße', '33A', 2, 14),
(30, 'LineWorks 2 AG', 'Mittelweg', '63', 10, 52),
(31, 'PeakDynamics AG', 'Industriestraße', '20B', 5, 110),
(32, 'Wolf & Partner UG', 'Kirchweg', '16B', 13, 22),
(33, 'LogisticsWorks AG', 'Im Gewerbepark', '77B', 4, 29),
(34, 'OmegaWorld AG', 'Mittelweg', '58A', 5, 80),
(35, 'Schmidt & Partner KG', 'Dorfstraße', '40B', 10, 96),
(36, 'AnalyticsWorks KG', 'Im Gewerbepark', '95', 13, 88),
(37, 'BlueWorks KG', 'Gartenweg', '34', 3, 7),
(38, 'Wagner & Partner UG', 'Ringstraße', '71', 3, 115),
(39, 'AnalyticsWorks UG', 'Dorfstraße', '58B', 8, 8),
(40, 'NextLogistics AG', 'Bahnhofstraße', '30', 12, 92),
(41, 'Becker & Partner KG', 'Am Mühlengraben', '10', 15, 55),
(42, 'SecurityWorks UG', 'Bergstraße', '85', 7, 1),
(43, 'NeoAnalytics KG', 'Eichenweg', '29', 15, 87),
(44, 'Becker & Partner 2 AG', 'Industriestraße', '10', 3, 99),
(45, 'MediaWorks UG', 'Im Gewerbepark', '96B', 15, 93),
(46, 'BlueWorld GmbH', 'Am Mühlengraben', '16A', 12, 13),
(47, 'Weber & Partner AG', 'Mittelweg', '35B', 9, 129),
(48, 'HealthWorks GmbH', 'Am Mühlengraben', '11B', 1, 3),
(49, 'QuantumAnalytics UG', 'Marktplatz', '78', 1, 103),
(50, 'Neumann & Partner KG', 'Kirchweg', '87B', 10, 33),
(51, 'TradingWorks GmbH', 'Seestraße', '74', 13, 60),
(52, 'UrbanTrading KG', 'Schillerstraße', '67A', 15, 68),
(53, 'Schmitz & Partner 2 KG', 'Ringstraße', '75A', 11, 104),
(54, 'BauWorks KG', 'Lindenweg', '61', 7, 109),
(55, 'SolarConsult UG', 'Marktplatz', '86', 14, 22),
(56, 'Müller & Partner KG', 'Marktplatz', '53A', 5, 67),
(57, 'MediaWorks AG', 'Eichenweg', '5A', 2, 33),
(58, 'CloudBau KG', 'Seestraße', '42', 13, 106),
(59, 'Krüger & Partner AG', 'Goethestraße', '106', 11, 15),
(60, 'DesignWorks KG', 'Am Mühlengraben', '53', 4, 52),
(61, 'PrimeTrading GmbH', 'Feldweg', '80A', 11, 123),
(62, 'Braun & Partner KG', 'Bahnhofstraße', '27', 9, 76),
(63, 'FoodsWorks GmbH', 'Berliner Allee', '57A', 2, 125),
(64, 'UrbanSolutions KG', 'Im Gewerbepark', '103', 12, 20),
(65, 'Becker & Partner GmbH', 'Berliner Allee', '71', 9, 34),
(66, 'DynamicsWorks GmbH', 'Lindenweg', '29', 8, 125),
(67, 'BlueFoods GmbH', 'Industriestraße', '64', 9, 83),
(68, 'Schmitz & Partner AG', 'Dorfstraße', '107A', 8, 127),
(69, 'DesignWorks UG', 'Am Mühlengraben', '71', 7, 83),
(70, 'PeakConsult KG', 'Im Gewerbepark', '66', 14, 24),
(71, 'Neumann & Partner UG', 'Seestraße', '99A', 6, 34),
(72, 'WorksWorks AG', 'Seestraße', '106', 5, 58),
(73, 'AlphaAnalytics KG', 'Bergstraße', '75A', 14, 93),
(74, 'Wolf & Partner 2 UG', 'Am Mühlengraben', '69A', 6, 8),
(75, 'BauWorks AG', 'Eichenweg', '98B', 7, 114),
(76, 'NordLine KG', 'Marktplatz', '112', 12, 76),
(77, 'Müller & Partner 2 AG', 'Bergstraße', '50', 14, 82),
(78, 'SecurityWorks AG', 'Bahnhofstraße', '41A', 12, 96),
(79, 'TechLine GmbH', 'Mittelweg', '85', 8, 52),
(80, 'Becker & Partner 2 GmbH', 'Industriestraße', '65B', 6, 8),
(81, 'WorldWorks KG', 'Am Mühlengraben', '13B', 15, 55),
(82, 'BlueMedia AG', 'Hauptstraße', '93', 7, 2),
(83, 'Schulz & Partner 2 UG', 'Lindenweg', '61', 6, 6),
(84, 'WorksWorks 2 AG', 'Mittelweg', '84', 14, 92),
(85, 'NeoSecurity UG', 'Eichenweg', '49', 11, 99),
(86, 'Becker & Partner UG', 'Eichenweg', '5B', 2, 108),
(87, 'HealthWorks AG', 'Berliner Allee', '30', 7, 48),
(88, 'UrbanBau UG', 'Parkallee', '57', 12, 84),
(89, 'Bauer & Partner UG', 'Hauptstraße', '6', 13, 99),
(90, 'HealthWorks UG', 'Berliner Allee', '46', 7, 10),
(91, 'GreenBau GmbH', 'Kirchweg', '68A', 10, 35),
(92, 'Richter & Partner KG', 'Ringstraße', '23', 10, 57),
(93, 'BauWorks 2 AG', 'Im Gewerbepark', '88', 8, 93),
(94, 'SmartWorks UG', 'Industriestraße', '30A', 11, 115),
(95, 'Weber & Partner UG', 'Am Mühlengraben', '33', 15, 52),
(96, 'ConsultWorks KG', 'Berliner Allee', '87B', 3, 11),
(97, 'AeroDynamics GmbH', 'Am Mühlengraben', '45B', 5, 118),
(98, 'Wolf & Partner GmbH', 'Seestraße', '59', 4, 105),
(99, 'WorldWorks GmbH', 'Schillerstraße', '14', 7, 38),
(100, 'BlueDynamics AG', 'Feldweg', '74', 12, 108),
(101, 'Klein & Partner UG', 'Hauptstraße', '107A', 5, 77),
(102, 'FoodsWorks AG', 'Bergstraße', '111', 15, 119),
(103, 'QuantumWorld AG', 'Schillerstraße', '107', 13, 114),
(104, 'Richter & Partner GmbH', 'Im Gewerbepark', '103', 4, 113),
(105, 'AnalyticsWorks 2 KG', 'Im Gewerbepark', '33', 11, 44),
(106, 'AeroSystems UG', 'Bahnhofstraße', '40A', 1, 76),
(107, 'Lange & Partner UG', 'Feldweg', '94', 2, 33),
(108, 'DesignWorks AG', 'Marktplatz', '96A', 3, 83),
(109, 'AlphaWorks GmbH', 'Industriestraße', '101B', 15, 2),
(110, 'Zimmermann & Partner GmbH', 'Goethestraße', '65', 14, 7),
(111, 'IndustriesWorks GmbH', 'Seestraße', '117A', 13, 109),
(112, 'GreenSecurity UG', 'Marktplatz', '103', 8, 102),
(113, 'Neumann & Partner AG', 'Industriestraße', '97', 14, 7),
(114, 'WorldWorks 2 GmbH', 'Eichenweg', '47', 13, 16),
(115, 'PrimeLine GmbH', 'Hauptstraße', '34B', 2, 123),
(116, 'Werner & Partner AG', 'Feldweg', '87', 10, 82),
(117, 'AnalyticsWorks GmbH', 'Feldweg', '14', 8, 98),
(118, 'NeoDynamics GmbH', 'Im Gewerbepark', '114B', 6, 102),
(119, 'Braun & Partner GmbH', 'Kirchweg', '83', 11, 96),
(120, 'HealthWorks 2 KG', 'Berliner Allee', '84A', 2, 67),
(121, 'SüdWorks KG', 'Bahnhofstraße', '5', 8, 115),
(122, 'Becker & Partner 2 KG', 'Parkallee', '31B', 3, 102),
(123, 'AnalyticsWorks AG', 'Am Mühlengraben', '48B', 7, 53),
(124, 'AlphaEnergy KG', 'Industriestraße', '114A', 11, 99),
(125, 'Schmitz & Partner GmbH', 'Schillerstraße', '79A', 5, 128),
(126, 'VisionWorks UG', 'Feldweg', '28A', 8, 31),
(127, 'MetroSecurity GmbH', 'Feldweg', '13', 9, 89),
(128, 'Schneider & Partner AG', 'Bahnhofstraße', '51', 4, 86),
(129, 'MediaWorks KG', 'Am Mühlengraben', '12', 11, 50),
(130, 'NextSolutions GmbH', 'Hauptstraße', '7', 4, 93),
(131, 'Becker & Partner 3 KG', 'Bergstraße', '27', 14, 79),
(132, 'SystemsWorks AG', 'Gartenweg', '76', 14, 19),
(133, 'AeroTrading KG', 'Marktplatz', '100', 13, 16),
(134, 'Braun & Partner 2 GmbH', 'Hauptstraße', '36', 3, 42),
(135, 'TradingWorks KG', 'Seestraße', '103', 2, 119),
(136, 'UrbanDesign KG', 'Industriestraße', '2', 13, 110),
(137, 'Fischer & Partner GmbH', 'Bergstraße', '42', 3, 83),
(138, 'TradingWorks AG', 'Bahnhofstraße', '17A', 9, 103),
(139, 'SüdSystems AG', 'Lindenweg', '61A', 13, 59),
(140, 'Lange & Partner KG', 'Goethestraße', '76', 8, 55),
(141, 'WorksWorks KG', 'Kirchweg', '79', 12, 95),
(142, 'CloudFoods KG', 'Berliner Allee', '59', 1, 114),
(143, 'Schmidt & Partner 2 GmbH', 'Mittelweg', '55', 8, 33),
(144, 'HealthWorks 3 KG', 'Lindenweg', '116', 6, 58),
(145, 'GreenVision KG', 'Industriestraße', '9', 5, 99),
(146, 'Schmitz & Partner 2 AG', 'Bergstraße', '71', 7, 24),
(147, 'LogisticsWorks 2 AG', 'Goethestraße', '38A', 9, 86),
(148, 'AeroTrading UG', 'Dorfstraße', '13', 14, 8),
(149, 'Schwarz & Partner GmbH', 'Gartenweg', '56A', 15, 82),
(150, 'BauWorks 2 GmbH', 'Dorfstraße', '44A', 7, 106),
(151, 'NextTrading GmbH', 'Parkallee', '41A', 6, 129),
(152, 'Bauer & Partner AG', 'Feldweg', '20A', 2, 121),
(153, 'HealthWorks 2 AG', 'Lindenweg', '12A', 2, 128),
(154, 'GreenSystems KG', 'Industriestraße', '72', 10, 66),
(155, 'Schmidt & Partner 2 KG', 'Eichenweg', '43', 7, 115),
(156, 'WorksWorks 3 AG', 'Dorfstraße', '112', 5, 79),
(157, 'UrbanSolutions UG', 'Berliner Allee', '46', 10, 88),
(158, 'Braun & Partner AG', 'Gartenweg', '20A', 4, 94),
(159, 'DynamicsWorks AG', 'Feldweg', '109B', 6, 71),
(160, 'PrimeHealth GmbH', 'Seestraße', '74', 13, 13),
(161, 'Meyer & Partner KG', 'Eichenweg', '99B', 10, 34),
(162, 'HealthWorks 3 AG', 'Hauptstraße', '78', 1, 45),
(163, 'SüdConsult GmbH', 'Seestraße', '90', 15, 122),
(164, 'Richter & Partner 2 GmbH', 'Feldweg', '1', 14, 77),
(165, 'FoodsWorks 2 AG', 'Bergstraße', '85A', 2, 21),
(166, 'SmartEnergy KG', 'Hauptstraße', '12B', 4, 87),
(167, 'Hoffmann & Partner AG', 'Dorfstraße', '59', 3, 6),
(168, 'DynamicsWorks 2 GmbH', 'Berliner Allee', '93', 13, 17),
(169, 'SmartAnalytics KG', 'Im Gewerbepark', '11', 3, 85),
(170, 'Schulz & Partner GmbH', 'Im Gewerbepark', '7', 5, 83),
(171, 'LogisticsWorks KG', 'Dorfstraße', '63B', 8, 48),
(172, 'CloudAnalytics KG', 'Seestraße', '28B', 2, 28),
(173, 'Müller & Partner GmbH', 'Dorfstraße', '15', 11, 100),
(174, 'LogisticsWorks 3 AG', 'Schillerstraße', '68', 1, 62),
(175, 'NeoLogistics GmbH', 'Mittelweg', '77', 1, 101),
(176, 'Fischer & Partner UG', 'Berliner Allee', '28', 13, 114),
(177, 'SolutionsWorks KG', 'Berliner Allee', '42', 1, 90),
(178, 'SolarMaritime GmbH', 'Dorfstraße', '23', 7, 16),
(179, 'Richter & Partner AG', 'Kirchweg', '65B', 14, 45),
(180, 'LogisticsWorks GmbH', 'Lindenweg', '51', 7, 4),
(181, 'SolarVision AG', 'Am Mühlengraben', '118', 14, 7),
(182, 'Bauer & Partner 2 UG', 'Bergstraße', '55B', 7, 109),
(183, 'LineWorks KG', 'Berliner Allee', '15A', 1, 95),
(184, 'MetroIndustries GmbH', 'Ringstraße', '103B', 8, 96),
(185, 'Hartmann & Partner KG', 'Lindenweg', '56', 4, 31),
(186, 'MediaWorks 2 KG', 'Bergstraße', '52B', 2, 111),
(187, 'SolarIndustries UG', 'Berliner Allee', '96', 4, 60),
(188, 'Lange & Partner 2 KG', 'Ringstraße', '10B', 11, 40),
(189, 'TradingWorks 2 AG', 'Goethestraße', '66', 15, 107),
(190, 'SmartHealth UG', 'Feldweg', '94', 4, 108),
(191, 'Werner & Partner 2 AG', 'Industriestraße', '33', 3, 89),
(192, 'MaritimeWorks 2 KG', 'Industriestraße', '98', 3, 89),
(193, 'QuantumTrading GmbH', 'Am Mühlengraben', '97B', 13, 39),
(194, 'Hoffmann & Partner KG', 'Am Mühlengraben', '88B', 11, 126),
(195, 'WorksWorks UG', 'Marktplatz', '111', 3, 29),
(196, 'NeoMaritime KG', 'Lindenweg', '61A', 11, 112),
(197, 'Wolf & Partner 3 UG', 'Seestraße', '76', 6, 31),
(198, 'EnergyWorks AG', 'Lindenweg', '40A', 8, 34),
(199, 'CloudFoods AG', 'Bahnhofstraße', '48', 2, 2),
(200, 'Werner & Partner GmbH', 'Im Gewerbepark', '77B', 7, 10);

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `kommentar`
--

CREATE TABLE `kommentar` (
  `lead_id` int(11) NOT NULL,
  `kommentar_id` int(11) NOT NULL,
  `Datum` date NOT NULL,
  `text` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `lead`
--

CREATE TABLE `lead` (
  `lead_id` int(11) NOT NULL,
  `datum_erfasst` date NOT NULL DEFAULT current_timestamp(),
  `produktgruppe_id` int(11) NOT NULL,
  `produkt_id` int(11) NOT NULL,
  `produktzustand_id` int(11) NOT NULL,
  `status_id` int(11) NOT NULL,
  `quelle_id` int(11) NOT NULL,
  `ansprechpartner_id` int(11) NOT NULL,
  `erfasser_id` int(11) NOT NULL,
  `bearbeiter_id` int(11) NOT NULL,
  `bild_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Daten für Tabelle `lead`
--

INSERT INTO `lead` (`lead_id`, `datum_erfasst`, `produktgruppe_id`, `produkt_id`, `produktzustand_id`, `status_id`, `quelle_id`, `ansprechpartner_id`, `erfasser_id`, `bearbeiter_id`, `bild_id`) VALUES
(2, '2026-01-07', 1, 3, 1, 1, 4, 242, 3, 3, 0);

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `lead_aktionen`
--

CREATE TABLE `lead_aktionen` (
  `aktion_id` int(11) NOT NULL,
  `lead_id` int(11) NOT NULL,
  `benutzer_id` int(11) NOT NULL,
  `aktion_typ` enum('angenommen','abgelehnt','zugewiesen','erledigt','Angebot erstellt') NOT NULL,
  `ziel_benutzer_id` int(11) DEFAULT NULL,
  `kommentar` varchar(255) DEFAULT NULL,
  `zeitstempel` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `ort`
--

CREATE TABLE `ort` (
  `id_ort` int(11) NOT NULL,
  `plz` varchar(11) NOT NULL,
  `ort` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Daten für Tabelle `ort`
--

INSERT INTO `ort` (`id_ort`, `plz`, `ort`) VALUES
(2, '01067', 'Dresden'),
(83, '01968', 'Senftenberg'),
(32, '02625', 'Bautzen'),
(84, '03238', 'Finsterwalde'),
(5, '04109', 'Leipzig'),
(85, '04924', 'Bad Liebenwerda'),
(89, '06108', 'Halle (Saale)'),
(88, '06217', 'Merseburg'),
(87, '06618', 'Naumburg (Saale)'),
(86, '06712', 'Zeitz'),
(35, '06844', 'Dessau-Roßlau'),
(28, '07743', 'Jena'),
(33, '08523', 'Plauen'),
(27, '09111', 'Chemnitz'),
(1, '10115', 'Berlin'),
(26, '14467', 'Potsdam'),
(81, '14770', 'Brandenburg an der Havel'),
(79, '14943', 'Luckenwalde'),
(80, '15344', 'Strausberg'),
(78, '15806', 'Zossen'),
(82, '16321', 'Bernau bei Berlin'),
(69, '17033', 'Neubrandenburg'),
(74, '17192', 'Waren (Müritz)'),
(75, '17389', 'Anklam'),
(25, '17489', 'Greifswald'),
(24, '18055', 'Rostock'),
(73, '18311', 'Ribnitz-Damgarten'),
(72, '18439', 'Stralsund'),
(76, '18528', 'Bergen auf Rügen'),
(67, '19053', 'Schwerin'),
(77, '19230', 'Hagenow'),
(68, '19370', 'Parchim'),
(3, '20095', 'Hamburg'),
(66, '21244', 'Buchholz in der Nordheide'),
(22, '21335', 'Lüneburg'),
(39, '21337', 'Lüneburg'),
(50, '21423', 'Winsen (Luhe)'),
(63, '21465', 'Reinbek'),
(40, '21614', 'Buxtehude'),
(64, '22113', 'Oststeinbek'),
(65, '22850', 'Norderstedt'),
(53, '23552', 'Lübeck'),
(57, '23795', 'Bad Segeberg'),
(58, '23843', 'Bad Oldesloe'),
(71, '23936', 'Grevesmühlen'),
(70, '23966', 'Wismar'),
(52, '24103', 'Kiel'),
(51, '24534', 'Neumünster'),
(59, '24768', 'Rendsburg'),
(56, '24837', 'Schleswig'),
(55, '24937', 'Flensburg'),
(54, '25813', 'Husum'),
(60, '25899', 'Niebüll'),
(61, '25980', 'Westerland'),
(42, '26121', 'Oldenburg'),
(43, '26441', 'Jever'),
(44, '26506', 'Norden'),
(45, '26721', 'Emden'),
(46, '26871', 'Papenburg'),
(48, '27283', 'Verden (Aller)'),
(41, '27356', 'Rotenburg (Wümme)'),
(62, '27472', 'Cuxhaven'),
(47, '27568', 'Bremerhaven'),
(7, '28195', 'Bremen'),
(49, '28832', 'Achim'),
(38, '29221', 'Celle'),
(6, '30159', 'Hannover'),
(21, '35037', 'Marburg'),
(37, '38820', 'Halberstadt'),
(36, '39104', 'Magdeburg'),
(34, '39576', 'Stendal'),
(10, '40210', 'Düsseldorf'),
(9, '44135', 'Dortmund'),
(8, '45127', 'Essen'),
(23, '49074', 'Osnabrück'),
(11, '50667', 'Köln'),
(12, '55116', 'Mainz'),
(13, '60311', 'Frankfurt am Main'),
(30, '63741', 'Aschaffenburg'),
(20, '72070', 'Tübingen'),
(16, '78462', 'Konstanz'),
(4, '80331', 'München'),
(129, '82319', 'Starnberg'),
(128, '83022', 'Rosenheim'),
(126, '84130', 'Dingolfing'),
(125, '84347', 'Pfarrkirchen'),
(127, '84489', 'Burghausen'),
(15, '86150', 'Augsburg'),
(130, '86899', 'Landsberg am Lech'),
(17, '89073', 'Ulm'),
(14, '90402', 'Nürnberg'),
(103, '90762', 'Fürth'),
(102, '91052', 'Erlangen'),
(119, '91126', 'Schwabach'),
(120, '91522', 'Ansbach'),
(121, '91781', 'Weißenburg in Bayern'),
(101, '92224', 'Amberg'),
(100, '92637', 'Weiden in der Oberpfalz'),
(19, '93047', 'Regensburg'),
(122, '93309', 'Kelheim'),
(124, '94032', 'Passau'),
(123, '94315', 'Straubing'),
(107, '95028', 'Hof'),
(106, '95326', 'Kulmbach'),
(99, '95444', 'Bayreuth'),
(98, '96047', 'Bamberg'),
(97, '96103', 'Hallstadt'),
(105, '96215', 'Lichtenfels'),
(108, '96317', 'Kronach'),
(104, '96450', 'Coburg'),
(18, '97070', 'Würzburg'),
(115, '97076', 'Würzburg'),
(114, '97204', 'Höchberg'),
(113, '97209', 'Veitshöchheim'),
(117, '97232', 'Giebelstadt'),
(116, '97318', 'Kitzingen'),
(110, '97421', 'Schweinfurt'),
(118, '97437', 'Haßfurt'),
(111, '97616', 'Bad Neustadt an der Saale'),
(112, '97688', 'Bad Kissingen'),
(109, '97753', 'Karlstadt'),
(92, '98527', 'Suhl'),
(93, '98617', 'Meiningen'),
(96, '98646', 'Hildburghausen'),
(90, '98693', 'Ilmenau'),
(91, '98716', 'Geschwenda'),
(29, '99084', 'Erfurt'),
(95, '99510', 'Apolda'),
(31, '99817', 'Eisenach'),
(94, '99867', 'Gotha');

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `position`
--

CREATE TABLE `position` (
  `id` int(11) NOT NULL,
  `bezeichnung` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Daten für Tabelle `position`
--

INSERT INTO `position` (`id`, `bezeichnung`) VALUES
(5, 'Assistenz der Geschäftsführung'),
(14, 'Buchhaltung'),
(15, 'Controlling'),
(11, 'Einkauf'),
(6, 'Einkaufsleiter/in'),
(1, 'Geschäftsführer/in'),
(3, 'IT-Leitung'),
(7, 'Kundenberater/in'),
(10, 'Personalreferent/in'),
(4, 'Projektmanager/in'),
(8, 'Serviceleiter/in'),
(13, 'Sicherheitsbeauftragte/r'),
(9, 'Techniker/in'),
(12, 'Vertrieb'),
(2, 'Vertriebsleiter/in');

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `produkte`
--

CREATE TABLE `produkte` (
  `produkt_id` int(11) NOT NULL,
  `produkt` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Daten für Tabelle `produkte`
--

INSERT INTO `produkte` (`produkt_id`, `produkt`) VALUES
(4, 'Automationstechnik'),
(6, 'Hubarbeitsbühnen'),
(2, 'Lagertechnikgeräte'),
(5, 'Reinigungsmaschinen'),
(3, 'Schwerlaststapler'),
(8, 'Sonstige'),
(1, 'Stapler'),
(7, 'Vier- und Mehrwegeseitenstapler');

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `produktgruppe`
--

CREATE TABLE `produktgruppe` (
  `produkt_id` int(11) NOT NULL,
  `produkt` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Daten für Tabelle `produktgruppe`
--

INSERT INTO `produktgruppe` (`produkt_id`, `produkt`) VALUES
(2, 'Industriegeräte'),
(3, 'Serviceleistungen'),
(1, 'Stapler');

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `produktzustand`
--

CREATE TABLE `produktzustand` (
  `id` int(11) NOT NULL,
  `zustand` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Daten für Tabelle `produktzustand`
--

INSERT INTO `produktzustand` (`id`, `zustand`) VALUES
(3, NULL),
(2, 'Gebraucht'),
(1, 'Neu');

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `quelle`
--

CREATE TABLE `quelle` (
  `id_quelle` int(11) NOT NULL,
  `quelle` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Daten für Tabelle `quelle`
--

INSERT INTO `quelle` (`id_quelle`, `quelle`) VALUES
(4, 'Akquise'),
(2, 'Internet'),
(3, 'Messe'),
(1, 'persönliche Anfrage'),
(5, 'Telefonisch');

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `rolle`
--

CREATE TABLE `rolle` (
  `id_rolle` int(11) NOT NULL,
  `rolle` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Daten für Tabelle `rolle`
--

INSERT INTO `rolle` (`id_rolle`, `rolle`) VALUES
(0, 'Admin'),
(4, 'Leseberechtigung'),
(3, 'Techniker'),
(1, 'Vertriebsaußendienst'),
(2, 'Vertriebsinnendienst');

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `status`
--

CREATE TABLE `status` (
  `id` int(11) NOT NULL,
  `status` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Daten für Tabelle `status`
--

INSERT INTO `status` (`id`, `status`) VALUES
(0, ''),
(4, 'abgelehnt'),
(5, 'Angebot erstellt'),
(3, 'erledigt'),
(2, 'in Bearbeitung'),
(1, 'offen');

--
-- Indizes der exportierten Tabellen
--

--
-- Indizes für die Tabelle `anrede`
--
ALTER TABLE `anrede`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `bezeichnung` (`bezeichnung`);

--
-- Indizes für die Tabelle `ansprechpartner`
--
ALTER TABLE `ansprechpartner`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `vorname` (`vorname`,`nachname`,`email`,`telefon`),
  ADD KEY `anrede_id` (`anrede_id`),
  ADD KEY `position_id` (`position_id`),
  ADD KEY `firma_id` (`firma_id`);

--
-- Indizes für die Tabelle `benutzer`
--
ALTER TABLE `benutzer`
  ADD PRIMARY KEY (`benutzer_id`),
  ADD UNIQUE KEY `vorname` (`vorname`,`nachname`,`email`),
  ADD KEY `anrede` (`anrede`),
  ADD KEY `rolle` (`rolle_id`);

--
-- Indizes für die Tabelle `bild`
--
ALTER TABLE `bild`
  ADD PRIMARY KEY (`bild_id`);

--
-- Indizes für die Tabelle `branche`
--
ALTER TABLE `branche`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indizes für die Tabelle `firma`
--
ALTER TABLE `firma`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`,`strasse`,`hausnummer`),
  ADD KEY `branche_id` (`branche_id`),
  ADD KEY `ort_id` (`ort_id`);

--
-- Indizes für die Tabelle `kommentar`
--
ALTER TABLE `kommentar`
  ADD PRIMARY KEY (`kommentar_id`),
  ADD KEY `Lead` (`lead_id`);

--
-- Indizes für die Tabelle `lead`
--
ALTER TABLE `lead`
  ADD PRIMARY KEY (`lead_id`),
  ADD KEY `status` (`status_id`),
  ADD KEY `quelle` (`quelle_id`),
  ADD KEY `ansprechpartner` (`ansprechpartner_id`),
  ADD KEY `erfasser` (`erfasser_id`),
  ADD KEY `bearbeiter` (`bearbeiter_id`),
  ADD KEY `bild` (`bild_id`),
  ADD KEY `produktgruppe` (`produktgruppe_id`),
  ADD KEY `produkt` (`produkt_id`),
  ADD KEY `produktzustand` (`produktzustand_id`);

--
-- Indizes für die Tabelle `lead_aktionen`
--
ALTER TABLE `lead_aktionen`
  ADD PRIMARY KEY (`aktion_id`),
  ADD KEY `lead_id` (`lead_id`),
  ADD KEY `benutzer_id` (`benutzer_id`),
  ADD KEY `ziel_benutzer_id` (`ziel_benutzer_id`);

--
-- Indizes für die Tabelle `ort`
--
ALTER TABLE `ort`
  ADD PRIMARY KEY (`id_ort`),
  ADD UNIQUE KEY `plz` (`plz`,`ort`);

--
-- Indizes für die Tabelle `position`
--
ALTER TABLE `position`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `bezeichnung` (`bezeichnung`);

--
-- Indizes für die Tabelle `produkte`
--
ALTER TABLE `produkte`
  ADD PRIMARY KEY (`produkt_id`),
  ADD UNIQUE KEY `produkt` (`produkt`);

--
-- Indizes für die Tabelle `produktgruppe`
--
ALTER TABLE `produktgruppe`
  ADD PRIMARY KEY (`produkt_id`),
  ADD UNIQUE KEY `produkt` (`produkt`);

--
-- Indizes für die Tabelle `produktzustand`
--
ALTER TABLE `produktzustand`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `zustand` (`zustand`);

--
-- Indizes für die Tabelle `quelle`
--
ALTER TABLE `quelle`
  ADD PRIMARY KEY (`id_quelle`),
  ADD UNIQUE KEY `quelle` (`quelle`);

--
-- Indizes für die Tabelle `rolle`
--
ALTER TABLE `rolle`
  ADD PRIMARY KEY (`id_rolle`),
  ADD UNIQUE KEY `rolle` (`rolle`);

--
-- Indizes für die Tabelle `status`
--
ALTER TABLE `status`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `status` (`status`);

--
-- AUTO_INCREMENT für exportierte Tabellen
--

--
-- AUTO_INCREMENT für Tabelle `anrede`
--
ALTER TABLE `anrede`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT für Tabelle `benutzer`
--
ALTER TABLE `benutzer`
  MODIFY `benutzer_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=70;

--
-- AUTO_INCREMENT für Tabelle `bild`
--
ALTER TABLE `bild`
  MODIFY `bild_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT für Tabelle `branche`
--
ALTER TABLE `branche`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT für Tabelle `kommentar`
--
ALTER TABLE `kommentar`
  MODIFY `kommentar_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT für Tabelle `lead`
--
ALTER TABLE `lead`
  MODIFY `lead_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT für Tabelle `lead_aktionen`
--
ALTER TABLE `lead_aktionen`
  MODIFY `aktion_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT für Tabelle `ort`
--
ALTER TABLE `ort`
  MODIFY `id_ort` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=131;

--
-- AUTO_INCREMENT für Tabelle `position`
--
ALTER TABLE `position`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT für Tabelle `produkte`
--
ALTER TABLE `produkte`
  MODIFY `produkt_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT für Tabelle `produktgruppe`
--
ALTER TABLE `produktgruppe`
  MODIFY `produkt_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT für Tabelle `produktzustand`
--
ALTER TABLE `produktzustand`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Constraints der exportierten Tabellen
--

--
-- Constraints der Tabelle `ansprechpartner`
--
ALTER TABLE `ansprechpartner`
  ADD CONSTRAINT `ansprechpartner_ibfk_1` FOREIGN KEY (`anrede_id`) REFERENCES `anrede` (`id`),
  ADD CONSTRAINT `ansprechpartner_ibfk_2` FOREIGN KEY (`firma_id`) REFERENCES `firma` (`id`),
  ADD CONSTRAINT `ansprechpartner_ibfk_3` FOREIGN KEY (`position_id`) REFERENCES `position` (`id`);

--
-- Constraints der Tabelle `benutzer`
--
ALTER TABLE `benutzer`
  ADD CONSTRAINT `benutzer_ibfk_1` FOREIGN KEY (`rolle_id`) REFERENCES `rolle` (`id_rolle`),
  ADD CONSTRAINT `benutzer_ibfk_2` FOREIGN KEY (`anrede`) REFERENCES `anrede` (`id`);

--
-- Constraints der Tabelle `firma`
--
ALTER TABLE `firma`
  ADD CONSTRAINT `firma_ibfk_1` FOREIGN KEY (`branche_id`) REFERENCES `branche` (`id`),
  ADD CONSTRAINT `firma_ibfk_2` FOREIGN KEY (`ort_id`) REFERENCES `ort` (`id_ort`);

--
-- Constraints der Tabelle `kommentar`
--
ALTER TABLE `kommentar`
  ADD CONSTRAINT `kommentar_ibfk_1` FOREIGN KEY (`lead_id`) REFERENCES `lead` (`lead_id`);

--
-- Constraints der Tabelle `lead`
--
ALTER TABLE `lead`
  ADD CONSTRAINT `lead_ibfk_1` FOREIGN KEY (`bild_id`) REFERENCES `bild` (`bild_id`),
  ADD CONSTRAINT `lead_ibfk_2` FOREIGN KEY (`produktgruppe_id`) REFERENCES `produktgruppe` (`produkt_id`),
  ADD CONSTRAINT `lead_ibfk_3` FOREIGN KEY (`produkt_id`) REFERENCES `produkte` (`produkt_id`),
  ADD CONSTRAINT `lead_ibfk_4` FOREIGN KEY (`produktzustand_id`) REFERENCES `produktzustand` (`id`),
  ADD CONSTRAINT `lead_ibfk_5` FOREIGN KEY (`status_id`) REFERENCES `status` (`id`),
  ADD CONSTRAINT `lead_ibfk_6` FOREIGN KEY (`quelle_id`) REFERENCES `quelle` (`id_quelle`),
  ADD CONSTRAINT `lead_ibfk_7` FOREIGN KEY (`ansprechpartner_id`) REFERENCES `ansprechpartner` (`id`),
  ADD CONSTRAINT `lead_ibfk_8` FOREIGN KEY (`erfasser_id`) REFERENCES `benutzer` (`benutzer_id`),
  ADD CONSTRAINT `lead_ibfk_9` FOREIGN KEY (`bearbeiter_id`) REFERENCES `benutzer` (`benutzer_id`);

--
-- Constraints der Tabelle `lead_aktionen`
--
ALTER TABLE `lead_aktionen`
  ADD CONSTRAINT `lead_aktionen_ibfk_1` FOREIGN KEY (`lead_id`) REFERENCES `lead` (`lead_id`),
  ADD CONSTRAINT `lead_aktionen_ibfk_2` FOREIGN KEY (`benutzer_id`) REFERENCES `benutzer` (`benutzer_id`),
  ADD CONSTRAINT `lead_aktionen_ibfk_3` FOREIGN KEY (`ziel_benutzer_id`) REFERENCES `benutzer` (`benutzer_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
