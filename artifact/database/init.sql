-- Table: public.requests

-- DROP TABLE IF EXISTS public.requests;

CREATE TABLE IF NOT EXISTS public.requests
(
    id SERIAL,
    host character varying(128) COLLATE pg_catalog."default" NOT NULL,
    url character varying(256) COLLATE pg_catalog."default",
    method character varying(8) COLLATE pg_catalog."default" NOT NULL,
    query character varying(256) COLLATE pg_catalog."default",
    request character varying(10240) COLLATE pg_catalog."default",
    response character varying(10240) COLLATE pg_catalog."default",
    responsecode integer,
    "timestamp" timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT requests_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

-- ALTER TABLE IF EXISTS public.requests OWNER to postgres;

GRANT ALL ON TABLE public.requests TO openapi;

--GRANT ALL ON TABLE public.requests TO postgres;
