-- CREACIÓN DE UNA BASE DE DATOS DE NOMBRE hashMD5 CON CHARSET UTF8
CREATE DATABASE hashTable CHARACTER SET utf8 COLLATE utf8_general_ci;

-- SELECCIÓN DE LA BASE
USE hashTable;

-- TABLA DE PALABRAS CIFRADAS
CREATE TABLE palabras (
    palabra VARCHAR(50) PRIMARY KEY, -- Palabra única, clave primaria
    cifradoMD5 CHAR(32), -- Valor cifrado en MD5 (32),
    cifradoSHA1 CHAR(40), -- Valor cifrado en SHA1 (40),
    cifradoSHA256 CHAR(64) -- Valor cifrado en SHA256 (64)
) ENGINE=InnoDB;

-- CREACIÓN DE PROCEDIMIENTOS
DELIMITER $$

-- Procedimiento para descifrar un hash
CREATE PROCEDURE descifrarHash(
    paramCifradoMD5 CHAR(32),
    paramCifradoSHA1 CHAR(40),
    paramCifradoSHA256 CHAR(64)
)
BEGIN
    SELECT * FROM palabras
    WHERE (paramCifradoMD5 IS NULL OR cifradoMD5=paramCifradoMD5) AND
    (paramCifradoSHA1 IS NULL OR cifradoSHA1=paramCifradoSHA1) AND
    (paramCifradoSHA256 IS NULL OR cifradoSHA256=paramCifradoSHA256);
END $$

-- Procedimiento para añadir una palabra
CREATE PROCEDURE insertarPalabra(paramPalabra VARCHAR(50))
BEGIN
    -- Inserta una palabra y su valor directamente cifrado
    INSERT INTO palabras VALUES (
        paramPalabra,
        MD5(paramPalabra),
        SHA1(paramPalabra),
        SHA2(paramPalabra, 256)
    );
END $$
DELIMITER ;

-- FINALIZADO
