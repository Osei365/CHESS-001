-- prepares the app's database

CREATE DATABASE IF NOT EXISTS chess_game;
CREATE USER IF NOT EXISTS 'chess_user'@'localhost' IDENTIFIED BY 'aletheia';
GRANT ALL PRIVILEGES ON chess_game.* TO 'chess_user'@'localhost';
GRANT SELECT ON performance_schema.* TO 'chess_user'@'localhost';
FLUSH PRIVILEGES;