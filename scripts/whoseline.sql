CREATE TABLE "source" (
"id" INTEGER PRIMARY KEY AUTOINCREMENT,
"display_name" TEXT UNIQUE,
"short_name" TEXT UNIQUE,
"url" TEXT,
"description" TEXT
);
CREATE TABLE "line" (
"id" INTEGER PRIMARY KEY AUTOINCREMENT,
"wavelength" REAL NOT NULL,
"species" TEXT,
"priority" REAL,
"source_id" INTEGER REFERENCES "source"("id") ON UPDATE CASCADE ON DELETE CASCADE
);
