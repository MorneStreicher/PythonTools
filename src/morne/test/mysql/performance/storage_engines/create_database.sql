USE mysql
GO

DROP DATABASE test_database
GO

CREATE DATABASE test_database
GO

USE test_database
GO

CREATE TABLE test_table
(
	id BIGINT(20) NOT NULL AUTO_INCREMENT,
	date_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(),
	
	varchar_1 VARCHAR(500) NULL,
	varchar_2 VARCHAR(500) NULL,
	varchar_3 VARCHAR(500) NULL,
	varchar_4 VARCHAR(500) NULL,
	varchar_5 VARCHAR(500) NULL,
	varchar_6 VARCHAR(500) NULL,
	varchar_7 VARCHAR(500) NULL,
	varchar_8 VARCHAR(500) NULL,
	varchar_9 VARCHAR(500) NULL,
	varchar_10 VARCHAR(500) NULL,
	varchar_11 VARCHAR(500) NULL,
	varchar_12 VARCHAR(500) NULL,
	varchar_13 VARCHAR(500) NULL,
	varchar_14 VARCHAR(500) NULL,
	varchar_15 VARCHAR(500) NULL,
	varchar_16 VARCHAR(500) NULL,
	varchar_17 VARCHAR(500) NULL,
	varchar_18 VARCHAR(500) NULL,
	varchar_19 VARCHAR(500) NULL,
	varchar_20 VARCHAR(500) NULL,
	
	float_1 FLOAT NULL,
	float_2 FLOAT NULL,
	float_3 FLOAT NULL,
	float_4 FLOAT NULL,
	float_5 FLOAT NULL,
	float_6 FLOAT NULL,
	float_7 FLOAT NULL,
	float_8 FLOAT NULL,
	float_9 FLOAT NULL,
	float_10 FLOAT NULL,
  	float_11 FLOAT NULL,
  	float_12 FLOAT NULL,
  	float_13 FLOAT NULL,
  	float_14 FLOAT NULL,
  	float_15 FLOAT NULL,
  	float_16 FLOAT NULL,
  	float_17 FLOAT NULL,
  	float_18 FLOAT NULL,
  	float_19 FLOAT NULL,
  	float_20 FLOAT NULL,
  	

	PRIMARY KEY (id),
   
	INDEX ix_date (date_time)
) ENGINE=InnoDB;


