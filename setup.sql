CREATE DATABASE kyles_cool_gym;
USE kyles_cool_gym;

CREATE TABLE person (
	id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(80) NOT NULL,
    password VARCHAR(80) NOT NULL,
    email VARCHAR(80) NOT NULL,
    telephone_number CHAR(12),
    PRIMARY KEY (id)
);

CREATE TABLE manager (
	manager_id INT NOT NULL,
    PRIMARY KEY (manager_id),
    FOREIGN KEY (manager_id) REFERENCES person(id)
);

CREATE TABLE trainer (
	trainer_id INT NOT NULL,
    PRIMARY KEY (trainer_id),
    FOREIGN KEY (trainer_id) REFERENCES person(id)
);

CREATE TABLE member (
	member_id INT NOT NULL,
    PRIMARY KEY (member_id),
    FOREIGN KEY (member_id) REFERENCES person(id)
);

CREATE TABLE gym (
	gym_id INT NOT NULL,
    manager_id INT NOT NULL,
    name VARCHAR(80) NOT NULL,
    address VARCHAR(80) NOT NULL,
    telephone_number CHAR(12) NOT NULL,
    PRIMARY KEY (gym_id),
    FOREIGN KEY (manager_id) REFERENCES manager(manager_id)
);

CREATE TABLE attends (
	gym_id INT NOT NULL,
    trainer_id INT NOT NULL,
    member_id INT NOT NULL,
    FOREIGN KEY (gym_id) REFERENCES gym(gym_id),
    FOREIGN KEY (trainer_id) REFERENCES trainer(trainer_id),
    FOREIGN KEY (member_id) REFERENCES member (member_id)
);

CREATE TABLE trainer_schedule (
	schedule_id INT NOT NULL AUTO_INCREMENT,
    trainer_id INT NOT NULL,
    member_id INT,
    member_book BOOLEAN,
    member_cancel BOOLEAN,
    date DATE NOT NULL,
    time TIME NOT NULL,
    booked BOOLEAN,
    available BOOLEAN,
    PRIMARY KEY (schedule_id),
    FOREIGN KEY (trainer_id) REFERENCES trainer(trainer_id),
    FOREIGN KEY (member_id) REFERENCES member(member_id)
);

CREATE TABLE membership (
	member_id INT NOT NULL,
    gold BOOLEAN NOT NULL,
    silver BOOLEAN NOT NULL,
    active BOOLEAN NOT NULL,
    inactive BOOLEAN NOT NULL,
    PRIMARY KEY (member_id),
    FOREIGN KEY (member_id) REFERENCES member(member_id)
);

CREATE TABLE workout (
	workout_id INT NOT NULL AUTO_INCREMENT,
    member_id INT NOT NULL,
    member_date DATE,
    member_time TIME,
    easy BOOLEAN,
    hard BOOLEAN,
    PRIMARY KEY (workout_id),
    FOREIGN KEY (member_id) REFERENCES member(member_id)
);

CREATE TABLE strength (
	workout_id INT NOT NULL,
    rest_time VARCHAR(10),
    reps INT,
    weight VARCHAR(10),
    FOREIGN KEY (workout_id) REFERENCES workout(workout_id)
);

CREATE TABLE cardio (
	workout_id INT NOT NULL,
    distance VARCHAR(10),
    duration VARCHAR(10),
    FOREIGN KEY (workout_id) REFERENCES workout(workout_id)
);

INSERT INTO person (name, password, email, telephone_number)
VALUES ('Kyle Westwood', 'password123', 'kylegym@gmail.com', '314-555-5555'),
       ('Bob Billington', 'boblikesdogs', 'bobby@yahoo.com', '314-777-7777'),
       ('Kyle Thompson', 'pssword', 'kyle@gmail.com', '314-999-9999'),
       ('Bob Jenkins', 'boblikescats', 'tigers123@gmail.com', '549-276-3333'),
       ('Alice Rivera', 'morepass', 'alice549@yahoo.com', '123-456-7890'),
       ('John Miller', 'lotsofpass', 'john@gmail.com', '987-654-3210'),
       ('Zara Patel', 'wholelottapass', 'zara@yahoo.com', NULL),
       ('Eli Chen', 'PaSsWoRd', 'chen@gmail.com', '000-000-0000'),
       ('Max Robinson', 'maxattax', 'max@gmail.com', '999-999-9999'),
       ('Olivia Grant', 'chicken', 'grant4@gmail.com', '111-111-1111'),
       ('Mia Walker', 'walkin', 'walker@yahoo.com', '383-389-9999'),
       ('Ethan Brooks', 'talkin', 'brooks@gmail.com', '555-555-5555'),
       ('Ava Richardson', 'rich', 'ava@yahoo.com', '789-256-4444'),
       ('Leo Nguyen', 'LeoIsCool123', 'leo@gmail.com', '647-258-0912'),
       ('Grace Sullivan', 'IAmGrace', 'grace@yahoo.com', NULL),
       ('Noah Parker', 'TheeNoahParker', 'noah@gmail.com', NULL),
       ('Lily Adams', 'AdamesTraore', 'adams@yahoo.com', '387-485-0000'),
       ('Caleb Scott', 'ScottRolen', 'caleb123@gmail.com', '678-012-6666'),
       ('Sophie Kim', 'sophieistheecoolest', 'sophie456@gmail.com', '555-789-1234'),
       ('Isaac Turner', 'TreaTurner', 'isaacemail@gmail,com', NULL),
       ('Emma Davis', 'PASSWORD', 'davis@gmail.com', '567-423-8888');
       
INSERT INTO manager (manager_id)
VALUES (1);

INSERT INTO trainer (trainer_id)
SELECT id FROM person ORDER BY id LIMIT 4 OFFSET 1;

INSERT INTO member (member_id)
SELECT id FROM person
WHERE id NOT IN (
	SELECT manager_id FROM manager
    UNION
    SELECT trainer_id FROM trainer
);

INSERT INTO gym (gym_id, manager_id, name, address, telephone_number)
VALUES (1, 1, 'Kyle''s Cool Gym', '1234 Cool Road, St. Louis, MO', '314-413-4444');

INSERT INTO membership (member_id, gold, silver, active, inactive)
VALUES (6, TRUE, FALSE, TRUE, FALSE),
	   (7, FALSE, TRUE, TRUE, FALSE),
       (8, FALSE, FALSE, FALSE, TRUE),
       (9, FALSE, TRUE, TRUE, FALSE),
       (10, TRUE, FALSE, TRUE, FALSE),
       (11, TRUE, FALSE, TRUE, FALSE),
       (12, TRUE, FALSE, TRUE, FALSE),
       (13, TRUE, FALSE, TRUE, FALSE),
       (14, FALSE, TRUE, TRUE, FALSE),
       (15, FALSE, TRUE, TRUE, FALSE),
       (16, TRUE, FALSE, TRUE, FALSE),
       (17, FALSE, TRUE, TRUE, FALSE),
       (18, TRUE, FALSE, TRUE, FALSE),
       (19, FALSE, FALSE, FALSE, TRUE),
       (20, FALSE, TRUE, TRUE, FALSE),
       (21, FALSE, FALSE, FALSE, TRUE);

INSERT INTO workout (member_id, member_date, member_time, easy, hard)
VALUES (6, '2025-04-16', '09:00:00', TRUE, FALSE),
	   (7, '2025-04-16', '10:00:00', FALSE, TRUE),
       (9, '2025-04-16', '11:30:00', TRUE, FALSE),
       (10, '2025-04-17', '15:00:00', TRUE, FALSE),
       (11, '2025-04-18', '11:00:00', FALSE, TRUE);

INSERT INTO strength (workout_id, rest_time, reps, weight)
VALUES (2, '60s', 10, '135lbs'),
	   (4, '30s', 20, '175lbs');
       
INSERT INTO cardio (workout_id, distance, duration)
VALUES (1, '2mi', '14min'),
	   (3, '1mi', '6min30s'),
       (5, '1mi', '15min');
