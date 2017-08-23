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
	
	jdoc  JSON,

	index_1 VARCHAR(10) AS (JSON_UNQUOTE(JSON_EXTRACT(jdoc, '$.index_1'))) VIRTUAL,
	index_2 VARCHAR(10) AS (JSON_UNQUOTE(JSON_EXTRACT(jdoc, '$.index_2'))) VIRTUAL,
	index_3 VARCHAR(10) AS (JSON_UNQUOTE(JSON_EXTRACT(jdoc, '$.index_3'))) VIRTUAL,
	index_4 VARCHAR(10) AS (JSON_UNQUOTE(JSON_EXTRACT(jdoc, '$.index_4'))) VIRTUAL,
	index_5 VARCHAR(10) AS (JSON_UNQUOTE(JSON_EXTRACT(jdoc, '$.index_5'))) VIRTUAL,
  	

	PRIMARY KEY (id),
   
	INDEX ix_date (date_time),
	
	INDEX ix_index_1 (index_1),
	INDEX ix_index_2 (index_2),
	INDEX ix_index_3 (index_3),
	INDEX ix_index_4 (index_4),
	INDEX ix_index_5 (index_5)
	
) ENGINE=InnoDB;


