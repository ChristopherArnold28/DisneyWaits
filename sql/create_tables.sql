CREATE TABLE `Park` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `Name` text NOT NULL,
  `OpeningDate` text,
  PRIMARY KEY (`Id`),
  UNIQUE KEY `Id` (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;

CREATE TABLE `ParkHours` (
  `Date` text,
  `ParkId` int(11) DEFAULT NULL,
  `ParkOpen` text,
  `ParkClose` text,
  `EMHOpen` text,
  `EMHClose` text
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `Ride` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `Name` text NOT NULL,
  `OpeningDate` text,
  `Tier` text,
  `Location` text NOT NULL,
  `ParkId` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  UNIQUE KEY `Id` (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=413 DEFAULT CHARSET=latin1;

CREATE TABLE `Ride_Waits` (
  `RideId` int(11) NOT NULL,
  `Date` date NOT NULL,
  `Time` text NOT NULL,
  `Wait` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `Weather` (
  `Date` varchar(45) NOT NULL,
  `Time` text NOT NULL,
  `Status` text NOT NULL,
  `Temperature` float NOT NULL,
  `CloudCover` float NOT NULL,
  `SimpleStatus` text NOT NULL,
  `RainAccumulation` float NOT NULL,
  `Location` varchar(45) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

