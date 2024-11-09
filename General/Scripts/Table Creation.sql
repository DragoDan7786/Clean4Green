CREATE TABLE user (
    userID INTEGER PRIMARY KEY AUTOINCREMENT
    ,userName VARCHAR(250) NOT NULL UNIQUE
    ,pWord VARCHAR(250) NOT NULL
    ,firstName VARCHAR(250) NOT NULL
    ,lastName VARCHAR(250) NOT NULL
    ,email VARCHAR(250) NOT NULL
    ,isSuspended BINARY
);
CREATE TABLE Submissions (
    SubID INTEGER PRIMARY KEY AUTOINCREMENT
    ,submission_date DATETIME NOT NULL
    ,submission_proof BLOB NOT NULL
    ,userID INTEGER NOT NULL
    ,FOREIGN KEY (userID) REFERENCES user(userID)  -- Assuming a Users table exists with userID as primary key
);