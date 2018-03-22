CREATE DATABASE IF NOT EXISTS `ezira`;

USE `ezira`;

DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` text NOT NULL,
  `password` text NOT NULL,
  `admin` tinyint(1) NOT NULL,
  `banned` tinyint(1) NOT NULL,
  `premium` tinyint(1) NOT NULL,
  `session` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;

INSERT INTO `users` (`id`, `username`, `password`, `admin`, `banned`, `premium`, `session`) VALUES
(1, 'admin', 'GetHackedRetard', 1, 0, 1, 0);
COMMIT;
