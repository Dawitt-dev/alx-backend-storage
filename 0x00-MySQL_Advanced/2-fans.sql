-- 2-fans.sql content
-- content
USE holberton;

SELECT origin, fans as nb_fans
FROM metal_bands
ORDER BY nb_fans DESC;
