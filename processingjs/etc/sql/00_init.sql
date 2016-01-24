-- run as root
CREATE USER `gallery_rw`@`localhost` IDENTIFIED BY '<password>';

CREATE DATABASE processingjs_dev;
GRANT ALL PRIVILEGES ON `processingjs_dev`.* TO `gallery_rw`@`localhost`;
