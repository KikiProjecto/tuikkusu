# Setup Database untuk Tuikkusu
# Jalankan: sudo mysql < setup_db.sql

CREATE DATABASE IF NOT EXISTS tweak_db;
USE tweak_db;

CREATE TABLE IF NOT EXISTS tb_pilihan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kategori VARCHAR(50) NOT NULL,
    item VARCHAR(50) NOT NULL,
    ukuran FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE USER IF NOT EXISTS 'tuikkusu'@'localhost' IDENTIFIED BY 'tuikkusu123';
GRANT ALL PRIVILEGES ON tweak_db.* TO 'tuikkusu'@'localhost';
FLUSH PRIVILEGES;
