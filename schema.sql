-- USE [sql_db-accounting_system-dev];

-- CREATE SCHEMA acc;

-- DROP TABLE acc.users;

CREATE TABLE acc.users(
    user_id INT IDENTITY(1,1) PRIMARY KEY,
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(30) NOT NULL,
    email NVARCHAR(50) NOT NULL UNIQUE,
    created_at DATE NOT NULL DEFAULT GETDATE(),
    is_verified BIT DEFAULT 0,
    verification_code INT,
    code_issued_at DATETIME
)

-- CREATE TABLE acc.posts(
--     author_id INT FOREIGN KEY REFERENCES acc.users.user_id NOT NULL,
--     post_id INT IDENTITY(1,1) PRIMARY KEY,
--     content text NOT NULL
-- )


-- CREATE LOGIN Backend WITH PASSWORD='MIIBUwIBADANBgkqhkiG9';

-- CREATE USER fastapi WITH PASSWORD='MIIBUwIBADANBgkqhkiG9';
-- GRANT SELECT, INSERT, UPDATE, EXEC ON SCHEMA::acc TO fastapi;

-- DROP PROCEDURE acc.InsertUser;

-- CREATE PROCEDURE acc.InsertUser
--     @first_name NVARCHAR(30),
--     @last_name NVARCHAR(30),
--     @email NVARCHAR(50)
-- AS
-- BEGIN
--     SET NOCOUNT ON;
--     INSERT INTO acc.users (first_name, last_name, email)
--     VALUES (@first_name, @last_name, @email);
    
--     DECLARE @new_user_id INT = SCOPE_IDENTITY();
--     SELECT * FROM acc.users WHERE user_id = @new_user_id;
-- END;

-- DROP PROCEDURE acc.GenerateActivationCode

CREATE PROCEDURE acc.GenerateActivationCode
    @email NVARCHAR(50),
    @verification_code INT
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE acc.users SET verification_code = @verification_code, code_issued_at = GETDATE()
    WHERE email = @email;

    SELECT email, verification_code FROM acc.users
    WHERE email = @email; 
END;

-- CREATE PROCEDURE acc.ActivateAccount
--     @email NVARCHAR(50)
-- AS
-- BEGIN 
--     UPDATE acc.users SET is_verified = 1
--     WHERE email = @email;

--     SELECT email, verification_code FROM acc.users
--     WHERE email = @email;
-- END

-- CREATE PROCEDURE acc.DeleteActivationCode
--     @email NVARCHAR(50)
-- AS
-- BEGIN 
--     UPDATE acc.users SET verification_code = null
--     WHERE email = @email;

--     SELECT email, verification_code FROM acc.users
--     WHERE email = @email;
-- END

-- EXEC [acc].[InsertUser] @email="gabriel.suazo1211@gmail.com", @first_name="Gabriel", @last_name="Suazo";
DELETE FROM acc.users WHERE email = 'gabriel.suazo1211@gmail.com';