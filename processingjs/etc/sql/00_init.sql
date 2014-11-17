-- run as root
CREATE DATABASE processingjs_gallery;
CREATE USER `gallery_rw`@`localhost` IDENTIFIED BY 'gAll3rY-rw';
GRANT ALL PRIVILEGES ON `processingjs_gallery`.* TO `gallery_rw`@`localhost`;
