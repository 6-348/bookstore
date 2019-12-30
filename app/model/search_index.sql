CREATE EXTENSION zhparser;
CREATE TEXT SEARCH CONFIGURATION zhparser (PARSER = zhparser);
ALTER TEXT SEARCH CONFIGURATION zhparser ADD MAPPING FOR n,v,a,i,e,l WITH simple;

ALTER TABLE "StoreBooks" add column ts_search tsvector;
UPDATE "StoreBooks" SET ts_search = to_tsvector('zhparser', coalesce("Tags",'') || ' ' || coalesce("Title",'') || coalesce("Content",'') || coalesce("BookIntro",''));
CREATE INDEX idx_ts_seach ON "StoreBooks" USING gin(ts_search);