--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.12
-- Dumped by pg_dump version 11.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: api_active_odds; Type: TABLE; Schema: public; Owner: site
--

CREATE TABLE public.api_active_odds (
    id integer NOT NULL,
    datetime timestamp with time zone NOT NULL,
    bookmaker character varying(15) NOT NULL,
    full_time_result jsonb,
    draw_no_bet jsonb,
    both_teams_to_score jsonb,
    double_chance jsonb,
    under_over jsonb,
    event_id integer NOT NULL
);


ALTER TABLE public.api_active_odds OWNER TO site;

--
-- Name: api_active_odds_id_seq; Type: SEQUENCE; Schema: public; Owner: site
--

CREATE SEQUENCE public.api_active_odds_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.api_active_odds_id_seq OWNER TO site;

--
-- Name: api_active_odds_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: site
--

ALTER SEQUENCE public.api_active_odds_id_seq OWNED BY public.api_active_odds.id;


--
-- Name: api_all_odds; Type: TABLE; Schema: public; Owner: site
--

CREATE TABLE public.api_all_odds (
    id integer NOT NULL,
    datetime timestamp with time zone NOT NULL,
    bookmaker character varying(15) NOT NULL,
    full_time_result jsonb,
    draw_no_bet jsonb,
    both_teams_to_score jsonb,
    double_chance jsonb,
    under_over jsonb,
    event_id integer NOT NULL
);


ALTER TABLE public.api_all_odds OWNER TO site;

--
-- Name: api_all_odds_id_seq; Type: SEQUENCE; Schema: public; Owner: site
--

CREATE SEQUENCE public.api_all_odds_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.api_all_odds_id_seq OWNER TO site;

--
-- Name: api_all_odds_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: site
--

ALTER SEQUENCE public.api_all_odds_id_seq OWNED BY public.api_all_odds.id;


--
-- Name: api_events; Type: TABLE; Schema: public; Owner: site
--

CREATE TABLE public.api_events (
    id integer NOT NULL,
    datetime timestamp with time zone NOT NULL,
    country character varying(100) NOT NULL,
    league character varying(100) NOT NULL,
    home_team character varying(100) NOT NULL,
    away_team character varying(100) NOT NULL,
    home_goals integer,
    away_goals integer
);


ALTER TABLE public.api_events OWNER TO site;

--
-- Name: api_events_id_seq; Type: SEQUENCE; Schema: public; Owner: site
--

CREATE SEQUENCE public.api_events_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.api_events_id_seq OWNER TO site;

--
-- Name: api_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: site
--

ALTER SEQUENCE public.api_events_id_seq OWNED BY public.api_events.id;


--
-- Name: api_active_odds id; Type: DEFAULT; Schema: public; Owner: site
--

ALTER TABLE ONLY public.api_active_odds ALTER COLUMN id SET DEFAULT nextval('public.api_active_odds_id_seq'::regclass);


--
-- Name: api_all_odds id; Type: DEFAULT; Schema: public; Owner: site
--

ALTER TABLE ONLY public.api_all_odds ALTER COLUMN id SET DEFAULT nextval('public.api_all_odds_id_seq'::regclass);


--
-- Name: api_events id; Type: DEFAULT; Schema: public; Owner: site
--

ALTER TABLE ONLY public.api_events ALTER COLUMN id SET DEFAULT nextval('public.api_events_id_seq'::regclass);


--
-- Name: api_active_odds api_active_odds_pkey; Type: CONSTRAINT; Schema: public; Owner: site
--

ALTER TABLE ONLY public.api_active_odds
    ADD CONSTRAINT api_active_odds_pkey PRIMARY KEY (id);


--
-- Name: api_all_odds api_all_odds_pkey; Type: CONSTRAINT; Schema: public; Owner: site
--

ALTER TABLE ONLY public.api_all_odds
    ADD CONSTRAINT api_all_odds_pkey PRIMARY KEY (id);


--
-- Name: api_events api_events_pkey; Type: CONSTRAINT; Schema: public; Owner: site
--

ALTER TABLE ONLY public.api_events
    ADD CONSTRAINT api_events_pkey PRIMARY KEY (id);


--
-- Name: api_active_odds_event_id_7d43a33c; Type: INDEX; Schema: public; Owner: site
--

CREATE INDEX api_active_odds_event_id_7d43a33c ON public.api_active_odds USING btree (event_id);


--
-- Name: api_all_odds_event_id_da2c3a91; Type: INDEX; Schema: public; Owner: site
--

CREATE INDEX api_all_odds_event_id_da2c3a91 ON public.api_all_odds USING btree (event_id);


--
-- Name: api_active_odds api_active_odds_event_id_7d43a33c_fk_api_events_id; Type: FK CONSTRAINT; Schema: public; Owner: site
--

ALTER TABLE ONLY public.api_active_odds
    ADD CONSTRAINT api_active_odds_event_id_7d43a33c_fk_api_events_id FOREIGN KEY (event_id) REFERENCES public.api_events(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: api_all_odds api_all_odds_event_id_da2c3a91_fk_api_events_id; Type: FK CONSTRAINT; Schema: public; Owner: site
--

ALTER TABLE ONLY public.api_all_odds
    ADD CONSTRAINT api_all_odds_event_id_da2c3a91_fk_api_events_id FOREIGN KEY (event_id) REFERENCES public.api_events(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

