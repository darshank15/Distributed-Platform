CREATE TABLE `user` (
	`user_id` INT NOT NULL AUTO_INCREMENT,
	`name` VARCHAR(100) NOT NULL,
	`email` VARCHAR(100) NOT NULL,
	`password` VARCHAR(100) NOT NULL,
	`mobile_no` VARCHAR(10) NOT NULL,
	PRIMARY KEY (`user_id`)
);

CREATE TABLE `model` (
	`model_id` INT NOT NULL AUTO_INCREMENT,
	`model_name` VARCHAR(100) NOT NULL,
	`user_id` INT(100) NOT NULL,
	`url` VARCHAR(100) NOT NULL,
	`file_name` VARCHAR(100) NOT NULL,
	`status` VARCHAR(100) NOT NULL,
	`type` VARCHAR(100) NOT NULL,
	PRIMARY KEY (`model_id`)
);

CREATE TABLE `gateway` (
	`gateway_id` INT NOT NULL AUTO_INCREMENT,
	`ip` VARCHAR(20) NOT NULL,
	`uname` VARCHAR(100) NOT NULL,
	`password` VARCHAR(100) NOT NULL,
	`location` VARCHAR(100) NOT NULL,
	`gatewayname` VARCHAR(100) NOT NULL,
	PRIMARY KEY (`gateway_id`)
);

CREATE TABLE `sensor` (
	`sensor_id` INT NOT NULL AUTO_INCREMENT,
	`type` VARCHAR(100) NOT NULL,
	`name` VARCHAR(100) NOT NULL,
	`maker` VARCHAR(100),
	`datatype` VARCHAR(100),
	`format` VARCHAR(100),
	`streamrate` VARCHAR(100),
	`sensorSupport` VARCHAR(20),
	PRIMARY KEY (`sensor_id`)
);

CREATE TABLE `schedule` (
	`schedule_id` INT NOT NULL AUTO_INCREMENT,
	`start_time` VARCHAR(10) NOT NULL,
	`end_time` VARCHAR(10) NOT NULL,
	`interval_` INT NOT NULL,
	`count_` INT NOT NULL,
	`repeat_` VARCHAR(5) NOT NULL,
	`deploy_socket` VARCHAR(20) NOT NULL,
	`deploy_loc` VARCHAR(20) NOT NULL,
	`model_id` INT NOT NULL,
	`repeat_period` INT NOT NULL,
	`indefinately` VARCHAR(100) NOT NULL,
	`uname` VARCHAR(100),
	`password` VARCHAR(100),
	PRIMARY KEY (`schedule_id`)
);

CREATE TABLE `services` (
	`service_id` INT NOT NULL AUTO_INCREMENT,
	`service_name` VARCHAR(100) NOT NULL,
	`user_id` INT,
	`type` VARCHAR(100) NOT NULL,
	`mininstance` INT,
	`highmark` FLOAT,
	`lowmark` FLOAT,
	`minresponsetime` VARCHAR(255),
	`model_id` INT,
	`maxinstance` INT,
	PRIMARY KEY (`service_id`)
);

CREATE TABLE `model_sensor` (
	`model_sensor_id` INT NOT NULL AUTO_INCREMENT,
	`model_id` INT NOT NULL,
	`user_sensor_id` INT NOT NULL,
	PRIMARY KEY (`model_sensor_id`)
);

CREATE TABLE `services_dep` (
	`dep_id` INT NOT NULL AUTO_INCREMENT,
	`service_id` INT NOT NULL,
	`dep_service_id` INT NOT NULL,
	PRIMARY KEY (`dep_id`)
);

CREATE TABLE `gateway_sensor` (
	`gateway_sensor_id` INT NOT NULL AUTO_INCREMENT,
	`gateway_id` INT NOT NULL,
	`user_sensor_id` INT NOT NULL,
	PRIMARY KEY (`gateway_sensor_id`)
);

CREATE TABLE `service_sensor_dep` (
	`service_sensor_id` INT NOT NULL AUTO_INCREMENT,
	`service_id` INT NOT NULL,
	`user_sensor_id` INT NOT NULL,
	PRIMARY KEY (`service_sensor_id`)
);

CREATE TABLE `user_sensor` (
	`user_sensor_id` INT NOT NULL AUTO_INCREMENT,
	`user_id` INT NOT NULL,
	`sensor_id` INT NOT NULL,
	`sensor_location` VARCHAR(30) NOT NULL,
	PRIMARY KEY (`user_sensor_id`)
);

ALTER TABLE `model` ADD CONSTRAINT `model_fk0` FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`);

ALTER TABLE `schedule` ADD CONSTRAINT `schedule_fk0` FOREIGN KEY (`model_id`) REFERENCES `model`(`model_id`);

ALTER TABLE `services` ADD CONSTRAINT `services_fk0` FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`);

ALTER TABLE `services` ADD CONSTRAINT `services_fk1` FOREIGN KEY (`model_id`) REFERENCES `model`(`model_id`);

ALTER TABLE `model_sensor` ADD CONSTRAINT `model_sensor_fk0` FOREIGN KEY (`model_id`) REFERENCES `model`(`model_id`);

ALTER TABLE `model_sensor` ADD CONSTRAINT `model_sensor_fk1` FOREIGN KEY (`user_sensor_id`) REFERENCES `user_sensor`(`user_sensor_id`);

ALTER TABLE `services_dep` ADD CONSTRAINT `services_dep_fk0` FOREIGN KEY (`service_id`) REFERENCES `services`(`service_id`);

ALTER TABLE `services_dep` ADD CONSTRAINT `services_dep_fk1` FOREIGN KEY (`dep_service_id`) REFERENCES `services`(`service_id`);

ALTER TABLE `gateway_sensor` ADD CONSTRAINT `gateway_sensor_fk0` FOREIGN KEY (`gateway_id`) REFERENCES `gateway`(`gateway_id`);

ALTER TABLE `gateway_sensor` ADD CONSTRAINT `gateway_sensor_fk1` FOREIGN KEY (`user_sensor_id`) REFERENCES `user_sensor`(`user_sensor_id`);

ALTER TABLE `service_sensor_dep` ADD CONSTRAINT `service_sensor_dep_fk0` FOREIGN KEY (`service_id`) REFERENCES `services`(`service_id`);

ALTER TABLE `service_sensor_dep` ADD CONSTRAINT `service_sensor_dep_fk1` FOREIGN KEY (`user_sensor_id`) REFERENCES `user_sensor`(`user_sensor_id`);

ALTER TABLE `user_sensor` ADD CONSTRAINT `user_sensor_fk0` FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`);

ALTER TABLE `user_sensor` ADD CONSTRAINT `user_sensor_fk1` FOREIGN KEY (`sensor_id`) REFERENCES `sensor`(`sensor_id`);

