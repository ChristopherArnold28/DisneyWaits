CREATE DATABASE `DisneyDB` /*!40100 DEFAULT CHARACTER SET latin1 */;


CREATE TABLE `Park` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `Name` text NOT NULL,
  `OpeningDate` text,
  `DisplayName` varchar(45) NOT NULL,
  `Latitude` float DEFAULT '0',
  `Longitude` float DEFAULT '0',
  PRIMARY KEY (`Id`),
  UNIQUE KEY `Id` (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=latin1;


CREATE TABLE `ParkHours` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `Date` text,
  `ParkId` int(11) DEFAULT NULL,
  `ParkOpen` text,
  `ParkClose` text,
  `EMHOpen` text,
  `EMHClose` text,
  `SpecialOpen` text,
  `SpecialClose` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1000 DEFAULT CHARSET=latin1;


CREATE TABLE `Ride` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `Name` text NOT NULL,
  `OpeningDate` text,
  `Tier` text,
  `Location` text NOT NULL,
  `ParkId` int(11) DEFAULT NULL,
  `IntellectualProp` varchar(45) DEFAULT NULL,
  `HasWaits` int(11) NOT NULL DEFAULT '0',
  `GeoSearchName` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  UNIQUE KEY `Id` (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=80069789 DEFAULT CHARSET=latin1;


CREATE TABLE `Ride_Waits` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `RideId` int(11) NOT NULL,
  `Date` date NOT NULL,
  `Time` text NOT NULL,
  `Wait` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=72881 DEFAULT CHARSET=latin1;

CREATE TABLE `Ride_Waits_Today` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `RideId` int(11) NOT NULL,
  `Date` date NOT NULL,
  `Time` text NOT NULL,
  `Wait` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=72635 DEFAULT CHARSET=latin1;


CREATE TABLE `Weather` (
  `Date` varchar(45) NOT NULL,
  `Time` text NOT NULL,
  `Status` text NOT NULL,
  `Temperature` float NOT NULL,
  `CloudCover` float NOT NULL,
  `SimpleStatus` text NOT NULL,
  `RainAccumulation` float NOT NULL,
  `IconName` varchar(45) NOT NULL,
  `ParkId` int(11) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11008 DEFAULT CHARSET=latin1;


CREATE TABLE `Metrics` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `Name` text NOT NULL,
  `Value` float DEFAULT NULL,
  PRIMARY KEY (`Id`),
  UNIQUE KEY `Id` (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=62 DEFAULT CHARSET=latin1;

CREATE TABLE `Ride_Current_Status` (
  `RideId` int(11) NOT NULL,
  `Status` text NOT NULL,
  `FastPassAvailable` text NOT NULL,
  PRIMARY KEY (`RideId`)
) ENGINE=InnoDB AUTO_INCREMENT=94482 DEFAULT CHARSET=latin1;

