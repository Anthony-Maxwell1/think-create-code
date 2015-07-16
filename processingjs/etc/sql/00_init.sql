-- run as root
CREATE USER `gallery_rw`@`localhost` IDENTIFIED BY 'gAll3rY-rw';

CREATE DATABASE processingjs_gallery;
GRANT ALL PRIVILEGES ON `processingjs_gallery`.* TO `gallery_rw`@`localhost`;

CREATE DATABASE processingjs_gallery_dev;
GRANT ALL PRIVILEGES ON `processingjs_gallery_dev`.* TO `gallery_rw`@`localhost`;

CREATE DATABASE processingjs_gallery_3t2015;
GRANT ALL PRIVILEGES ON `processingjs_gallery_3t2015`.* TO `gallery_rw`@`localhost`;
