CREATE DATABASE IF NOT EXISTS Cisam;

SET character_set_client = utf8;
SET character_set_connection = utf8;
SET character_set_results = utf8;
SET collation_connection = utf8_general_ci;


USE Cisam;

-- CreateTable
CREATE TABLE IF NOT EXISTS `UserCisam` (
    `user_lgpd` VARCHAR(50) NOT NULL,
    `user_prontuario` VARCHAR(50) NOT NULL,

     PRIMARY KEY (`user_prontuario`)
);
