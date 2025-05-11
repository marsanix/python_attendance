CREATE DATABASE kehadiran_db;

USE kehadiran_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(50),
    role VARCHAR(20)
);

CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    status ENUM('Hadir', 'Izin', 'Sakit', 'Alpa')
);

INSERT INTO `users` (`id`, `username`, `password`, `role`) VALUES (1, 'admin', '0192023a7bbd73250516f069df18b500', 'admin');