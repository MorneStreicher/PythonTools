CREATE TABLE journal
(
	id BIGINT(20) NOT NULL AUTO_INCREMENT,
  uuid VARCHAR(36) NOT NULL,
	description VARCHAR(100) NULL,
	date DATETIME NOT NULL,
	debit_account VARCHAR(19) NOT NULL,
	credit_account VARCHAR(19) NOT NULL,
  amount FLOAT NOT NULL DEFAULT 0,

	PRIMARY KEY (id),
  INDEX ix_uuid (uuid),
	INDEX ix_date (date),
	INDEX ix_debit_account (debit_account),
	INDEX ix_credit_account (credit_account)
) ENGINE=InnoDB;


