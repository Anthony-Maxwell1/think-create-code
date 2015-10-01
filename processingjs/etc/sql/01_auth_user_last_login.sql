-- could not figure out how to fix my migrations!  so ugly hack follows:
alter table auth_user modify last_login datetime NULL DEFAULT NULL;
