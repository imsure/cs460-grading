BEGIN;
CREATE TABLE `assignment` (`assigName` varchar(10) NOT NULL PRIMARY KEY, `dueDate` datetime NOT NULL, `total` integer NOT NULL);
CREATE TABLE `grade` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `submitDateTime` datetime NOT NULL, `deduction` longtext NOT NULL, `score` integer NOT NULL, `assigName_id` varchar(10) NOT NULL);
CREATE TABLE `student` (`netID` varchar(100) NOT NULL PRIMARY KEY, `fname` varchar(100) NOT NULL, `lname` varchar(100) NOT NULL, `status` varchar(1) NOT NULL, `csID` integer NOT NULL);
ALTER TABLE `grade` ADD COLUMN `netID_id` varchar(100) NOT NULL;
ALTER TABLE `grade` ALTER COLUMN `netID_id` DROP DEFAULT;
ALTER TABLE `grade` ADD CONSTRAINT `grade_assigName_id_3d17a6b0248665a7_uniq` UNIQUE (`assigName_id`, `netID_id`);
ALTER TABLE `grade` ADD CONSTRAINT `grade_assigName_id_5a3c98ae8c958838_fk_assignment_assigName` FOREIGN KEY (`assigName_id`) REFERENCES `assignment` (`assigName`);
CREATE INDEX `grade_aff05cb0` ON `grade` (`netID_id`);
ALTER TABLE `grade` ADD CONSTRAINT `grade_netID_id_4e2f9b015fe60366_fk_student_netID` FOREIGN KEY (`netID_id`) REFERENCES `student` (`netID`);

COMMIT;
