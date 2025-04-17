CREATE TABLE IF NOT EXISTS "Users" (
	"user_id" INTEGER,
	"username" TEXT NOT NULL UNIQUE,
	"email" TEXT NOT NULL UNIQUE,
	"password_hash" TEXT NOT NULL,
	"Role" VARCHAR,
	PRIMARY KEY("user_id")
);

CREATE TABLE IF NOT EXISTS "Currencies" (
	"currency_id" INTEGER,
	"code" TEXT NOT NULL UNIQUE,
	"name" TEXT,
	"symbol" TEXT,
	PRIMARY KEY("currency_id")
);

CREATE TABLE IF NOT EXISTS "Accounts" (
	"account_id" INTEGER,
	"user_id" INTEGER NOT NULL,
	"name" TEXT NOT NULL,
	"balance" REAL NOT NULL DEFAULT 0,
	"currency_id" INTEGER NOT NULL,
	"description" TEXT,
	PRIMARY KEY("account_id"),
	FOREIGN KEY ("user_id") REFERENCES "Users"("user_id")
	ON UPDATE NO ACTION ON DELETE CASCADE,
	FOREIGN KEY ("currency_id") REFERENCES "Currencies"("currency_id")
	ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE TABLE IF NOT EXISTS "Categories" (
	"category_id" INTEGER,
	"user_id" INTEGER NOT NULL,
	"name" TEXT NOT NULL,
	"type" TEXT NOT NULL CHECK("type" IN income AND expense),
	"parent_id" INTEGER,
	PRIMARY KEY("category_id"),
	FOREIGN KEY ("user_id") REFERENCES "Users"("user_id")
	ON UPDATE NO ACTION ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "Transactions" (
	"transaction_id" INTEGER,
	"account_id" INTEGER NOT NULL,
	"category_id" INTEGER NOT NULL,
	"amount" REAL NOT NULL,
	"date" TEXT NOT NULL,
	"description" TEXT,
	"type" TEXT NOT NULL CHECK("type" IN income AND expense),
	PRIMARY KEY("transaction_id"),
	FOREIGN KEY ("account_id") REFERENCES "Accounts"("account_id")
	ON UPDATE NO ACTION ON DELETE CASCADE,
	FOREIGN KEY ("category_id") REFERENCES "Categories"("category_id")
	ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE TABLE IF NOT EXISTS "ScheduledTransactions" (
	"scheduled_id" INTEGER,
	"user_id" INTEGER NOT NULL,
	"account_id" INTEGER NOT NULL,
	"category_id" INTEGER NOT NULL,
	"amount" REAL NOT NULL,
	"planned_date" TEXT NOT NULL,
	"description" TEXT,
	"type" TEXT NOT NULL CHECK("type" IN income AND expense),
	"repeat_interval" TEXT,
	PRIMARY KEY("scheduled_id"),
	FOREIGN KEY ("user_id") REFERENCES "Users"("user_id")
	ON UPDATE NO ACTION ON DELETE CASCADE,
	FOREIGN KEY ("account_id") REFERENCES "Accounts"("account_id")
	ON UPDATE NO ACTION ON DELETE NO ACTION,
	FOREIGN KEY ("category_id") REFERENCES "Categories"("category_id")
	ON UPDATE NO ACTION ON DELETE NO ACTION
);
