CREATE TABLE
    IF NOT EXISTS Keywords (keyword_id INTEGER PRIMARY KEY, keyword TEXT);

CREATE TABLE
    IF NOT EXISTS Listings (
        listing_id TEXT PRIMARY KEY,
        listing_title TEXT,
        listing_vip_url TEXT,
        listing_keyword TEXT,
        tstamp INTEGER
    );

CREATE TABLE
    IF NOT EXISTS last_inserted (
        id INTEGER PRIMARY KEY CHECK (id = 0),
        listing_id TEXT,
        listing_title TEXT
    );

CREATE INDEX IF NOT EXISTS idx_keywords on Keywords (keyword_id);

CREATE INDEX IF NOT EXISTS idx_listings on Listings (listing_id);

CREATE INDEX IF NOT EXISTS idx_last_inserted on last_inserted (listing_id);

CREATE TABLE Blacklist (
sellerID int
);