-- CREATE SCHEMA acc;

CREATE TABLE acc.users(
    user_id INT IDENTITY(1,1) PRIMARY KEY,
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(30) NOT NULL,
    email NVARCHAR(255) NOT NULL UNIQUE,
    password_hash NVARCHAR(255) NOT NULL,
    is_verified BIT DEFAULT 0
)