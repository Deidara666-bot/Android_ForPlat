CREATE ROLE forensic_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD 'local-dev-only';
ALTER DATABASE android_forensic OWNER TO forensic_app;
CREATE DATABASE android_forensic_test OWNER forensic_app;
