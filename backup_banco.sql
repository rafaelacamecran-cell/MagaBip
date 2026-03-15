--
-- PostgreSQL database dump
--

\restrict dbF5MJTBKFqSn6r7pUno4eGrixYqxRsxZNng9RBuuzRO8X7PigmphWVXltLPFhI

-- Dumped from database version 15.17 (Debian 15.17-1.pgdg13+1)
-- Dumped by pg_dump version 15.17 (Debian 15.17-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alertas_ti; Type: TABLE; Schema: public; Owner: magabip_user
--

CREATE TABLE public.alertas_ti (
    id integer NOT NULL,
    data timestamp without time zone,
    tipo character varying(50),
    colaborador character varying(120),
    equipamento character varying(120),
    mensagem text,
    filial_id integer
);


ALTER TABLE public.alertas_ti OWNER TO magabip_user;

--
-- Name: alertas_ti_id_seq; Type: SEQUENCE; Schema: public; Owner: magabip_user
--

CREATE SEQUENCE public.alertas_ti_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.alertas_ti_id_seq OWNER TO magabip_user;

--
-- Name: alertas_ti_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: magabip_user
--

ALTER SEQUENCE public.alertas_ti_id_seq OWNED BY public.alertas_ti.id;


--
-- Name: behavior_logs; Type: TABLE; Schema: public; Owner: magabip_user
--

CREATE TABLE public.behavior_logs (
    id integer NOT NULL,
    user_id integer,
    device_id integer,
    event_type character varying(100),
    description text,
    severity character varying(20),
    created_at timestamp without time zone
);


ALTER TABLE public.behavior_logs OWNER TO magabip_user;

--
-- Name: behavior_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: magabip_user
--

CREATE SEQUENCE public.behavior_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.behavior_logs_id_seq OWNER TO magabip_user;

--
-- Name: behavior_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: magabip_user
--

ALTER SEQUENCE public.behavior_logs_id_seq OWNED BY public.behavior_logs.id;


--
-- Name: checkout_logs; Type: TABLE; Schema: public; Owner: magabip_user
--

CREATE TABLE public.checkout_logs (
    id integer NOT NULL,
    checkout_time timestamp without time zone NOT NULL,
    checkin_time timestamp without time zone,
    device_id integer NOT NULL,
    user_id integer NOT NULL,
    colaborador_name character varying(120),
    colaborador_id integer,
    lider_name character varying(120),
    lider_id integer,
    ti_name character varying(120),
    ti_id integer,
    action_time timestamp without time zone,
    setor character varying(100),
    nivel_bateria character varying(50),
    observacoes text,
    filial_id integer
);


ALTER TABLE public.checkout_logs OWNER TO magabip_user;

--
-- Name: checkout_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: magabip_user
--

CREATE SEQUENCE public.checkout_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.checkout_logs_id_seq OWNER TO magabip_user;

--
-- Name: checkout_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: magabip_user
--

ALTER SEQUENCE public.checkout_logs_id_seq OWNED BY public.checkout_logs.id;


--
-- Name: device_health; Type: TABLE; Schema: public; Owner: magabip_user
--

CREATE TABLE public.device_health (
    id integer NOT NULL,
    device_id integer NOT NULL,
    battery_level double precision,
    battery_voltage double precision,
    rssi integer,
    uptime_seconds integer,
    reset_reason character varying(100),
    created_at timestamp without time zone
);


ALTER TABLE public.device_health OWNER TO magabip_user;

--
-- Name: device_health_id_seq; Type: SEQUENCE; Schema: public; Owner: magabip_user
--

CREATE SEQUENCE public.device_health_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.device_health_id_seq OWNER TO magabip_user;

--
-- Name: device_health_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: magabip_user
--

ALTER SEQUENCE public.device_health_id_seq OWNED BY public.device_health.id;


--
-- Name: devices; Type: TABLE; Schema: public; Owner: magabip_user
--

CREATE TABLE public.devices (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    type character varying(50) NOT NULL,
    status character varying(50) NOT NULL,
    location character varying(50),
    condition character varying(50),
    serial_number character varying(100),
    last_inventory_check timestamp without time zone,
    current_user_id integer,
    updated_at timestamp without time zone,
    zendesk_url character varying(500),
    filial_id integer
);


ALTER TABLE public.devices OWNER TO magabip_user;

--
-- Name: devices_id_seq; Type: SEQUENCE; Schema: public; Owner: magabip_user
--

CREATE SEQUENCE public.devices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.devices_id_seq OWNER TO magabip_user;

--
-- Name: devices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: magabip_user
--

ALTER SEQUENCE public.devices_id_seq OWNED BY public.devices.id;


--
-- Name: faqs; Type: TABLE; Schema: public; Owner: magabip_user
--

CREATE TABLE public.faqs (
    id integer NOT NULL,
    question character varying(500) NOT NULL,
    answer text NOT NULL,
    relevance_count integer
);


ALTER TABLE public.faqs OWNER TO magabip_user;

--
-- Name: faqs_id_seq; Type: SEQUENCE; Schema: public; Owner: magabip_user
--

CREATE SEQUENCE public.faqs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.faqs_id_seq OWNER TO magabip_user;

--
-- Name: faqs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: magabip_user
--

ALTER SEQUENCE public.faqs_id_seq OWNED BY public.faqs.id;


--
-- Name: filiais; Type: TABLE; Schema: public; Owner: magabip_user
--

CREATE TABLE public.filiais (
    id integer NOT NULL,
    nome character varying(120) NOT NULL,
    codigo character varying(50),
    cidade character varying(100)
);


ALTER TABLE public.filiais OWNER TO magabip_user;

--
-- Name: filiais_id_seq; Type: SEQUENCE; Schema: public; Owner: magabip_user
--

CREATE SEQUENCE public.filiais_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.filiais_id_seq OWNER TO magabip_user;

--
-- Name: filiais_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: magabip_user
--

ALTER SEQUENCE public.filiais_id_seq OWNED BY public.filiais.id;


--
-- Name: support_tickets; Type: TABLE; Schema: public; Owner: magabip_user
--

CREATE TABLE public.support_tickets (
    id integer NOT NULL,
    device_id integer NOT NULL,
    problem_description character varying(255),
    solution character varying(500),
    status character varying(20),
    created_at timestamp without time zone,
    resolved_at timestamp without time zone,
    zendesk_link character varying(255),
    reported_by_user_id integer,
    zendesk_added_by_user_id integer,
    resolved_by_user_id integer,
    colaborador_name character varying(120),
    colaborador_id integer,
    lider_name character varying(120),
    lider_id integer,
    ti_name character varying(120),
    ti_id integer,
    action_time timestamp without time zone,
    filial_id integer
);


ALTER TABLE public.support_tickets OWNER TO magabip_user;

--
-- Name: support_tickets_id_seq; Type: SEQUENCE; Schema: public; Owner: magabip_user
--

CREATE SEQUENCE public.support_tickets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.support_tickets_id_seq OWNER TO magabip_user;

--
-- Name: support_tickets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: magabip_user
--

ALTER SEQUENCE public.support_tickets_id_seq OWNED BY public.support_tickets.id;


--
-- Name: technical_docs; Type: TABLE; Schema: public; Owner: magabip_user
--

CREATE TABLE public.technical_docs (
    id integer NOT NULL,
    title character varying(200) NOT NULL,
    content text NOT NULL,
    category character varying(50),
    tags character varying(200),
    created_at timestamp without time zone
);


ALTER TABLE public.technical_docs OWNER TO magabip_user;

--
-- Name: technical_docs_id_seq; Type: SEQUENCE; Schema: public; Owner: magabip_user
--

CREATE SEQUENCE public.technical_docs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.technical_docs_id_seq OWNER TO magabip_user;

--
-- Name: technical_docs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: magabip_user
--

ALTER SEQUENCE public.technical_docs_id_seq OWNED BY public.technical_docs.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: magabip_user
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(80) NOT NULL,
    colaborador_id character varying(50),
    name character varying(120) NOT NULL,
    password_hash character varying(256) NOT NULL,
    email character varying(120),
    role character varying(50) NOT NULL,
    funcao character varying(100),
    turno character varying(50),
    must_change_password boolean,
    filial_id integer
);


ALTER TABLE public.users OWNER TO magabip_user;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: magabip_user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO magabip_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: magabip_user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: alertas_ti id; Type: DEFAULT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.alertas_ti ALTER COLUMN id SET DEFAULT nextval('public.alertas_ti_id_seq'::regclass);


--
-- Name: behavior_logs id; Type: DEFAULT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.behavior_logs ALTER COLUMN id SET DEFAULT nextval('public.behavior_logs_id_seq'::regclass);


--
-- Name: checkout_logs id; Type: DEFAULT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.checkout_logs ALTER COLUMN id SET DEFAULT nextval('public.checkout_logs_id_seq'::regclass);


--
-- Name: device_health id; Type: DEFAULT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.device_health ALTER COLUMN id SET DEFAULT nextval('public.device_health_id_seq'::regclass);


--
-- Name: devices id; Type: DEFAULT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.devices ALTER COLUMN id SET DEFAULT nextval('public.devices_id_seq'::regclass);


--
-- Name: faqs id; Type: DEFAULT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.faqs ALTER COLUMN id SET DEFAULT nextval('public.faqs_id_seq'::regclass);


--
-- Name: filiais id; Type: DEFAULT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.filiais ALTER COLUMN id SET DEFAULT nextval('public.filiais_id_seq'::regclass);


--
-- Name: support_tickets id; Type: DEFAULT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.support_tickets ALTER COLUMN id SET DEFAULT nextval('public.support_tickets_id_seq'::regclass);


--
-- Name: technical_docs id; Type: DEFAULT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.technical_docs ALTER COLUMN id SET DEFAULT nextval('public.technical_docs_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alertas_ti; Type: TABLE DATA; Schema: public; Owner: magabip_user
--

COPY public.alertas_ti (id, data, tipo, colaborador, equipamento, mensagem, filial_id) FROM stdin;
\.


--
-- Data for Name: behavior_logs; Type: TABLE DATA; Schema: public; Owner: magabip_user
--

COPY public.behavior_logs (id, user_id, device_id, event_type, description, severity, created_at) FROM stdin;
\.


--
-- Data for Name: checkout_logs; Type: TABLE DATA; Schema: public; Owner: magabip_user
--

COPY public.checkout_logs (id, checkout_time, checkin_time, device_id, user_id, colaborador_name, colaborador_id, lider_name, lider_id, ti_name, ti_id, action_time, setor, nivel_bateria, observacoes, filial_id) FROM stdin;
\.


--
-- Data for Name: device_health; Type: TABLE DATA; Schema: public; Owner: magabip_user
--

COPY public.device_health (id, device_id, battery_level, battery_voltage, rssi, uptime_seconds, reset_reason, created_at) FROM stdin;
\.


--
-- Data for Name: devices; Type: TABLE DATA; Schema: public; Owner: magabip_user
--

COPY public.devices (id, name, type, status, location, condition, serial_number, last_inventory_check, current_user_id, updated_at, zendesk_url, filial_id) FROM stdin;
\.


--
-- Data for Name: faqs; Type: TABLE DATA; Schema: public; Owner: magabip_user
--

COPY public.faqs (id, question, answer, relevance_count) FROM stdin;
\.


--
-- Data for Name: filiais; Type: TABLE DATA; Schema: public; Owner: magabip_user
--

COPY public.filiais (id, nome, codigo, cidade) FROM stdin;
\.


--
-- Data for Name: support_tickets; Type: TABLE DATA; Schema: public; Owner: magabip_user
--

COPY public.support_tickets (id, device_id, problem_description, solution, status, created_at, resolved_at, zendesk_link, reported_by_user_id, zendesk_added_by_user_id, resolved_by_user_id, colaborador_name, colaborador_id, lider_name, lider_id, ti_name, ti_id, action_time, filial_id) FROM stdin;
\.


--
-- Data for Name: technical_docs; Type: TABLE DATA; Schema: public; Owner: magabip_user
--

COPY public.technical_docs (id, title, content, category, tags, created_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: magabip_user
--

COPY public.users (id, username, colaborador_id, name, password_hash, email, role, funcao, turno, must_change_password, filial_id) FROM stdin;
\.


--
-- Name: alertas_ti_id_seq; Type: SEQUENCE SET; Schema: public; Owner: magabip_user
--

SELECT pg_catalog.setval('public.alertas_ti_id_seq', 1, false);


--
-- Name: behavior_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: magabip_user
--

SELECT pg_catalog.setval('public.behavior_logs_id_seq', 1, false);


--
-- Name: checkout_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: magabip_user
--

SELECT pg_catalog.setval('public.checkout_logs_id_seq', 1, false);


--
-- Name: device_health_id_seq; Type: SEQUENCE SET; Schema: public; Owner: magabip_user
--

SELECT pg_catalog.setval('public.device_health_id_seq', 1, false);


--
-- Name: devices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: magabip_user
--

SELECT pg_catalog.setval('public.devices_id_seq', 1, false);


--
-- Name: faqs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: magabip_user
--

SELECT pg_catalog.setval('public.faqs_id_seq', 1, false);


--
-- Name: filiais_id_seq; Type: SEQUENCE SET; Schema: public; Owner: magabip_user
--

SELECT pg_catalog.setval('public.filiais_id_seq', 1, false);


--
-- Name: support_tickets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: magabip_user
--

SELECT pg_catalog.setval('public.support_tickets_id_seq', 1, false);


--
-- Name: technical_docs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: magabip_user
--

SELECT pg_catalog.setval('public.technical_docs_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: magabip_user
--

SELECT pg_catalog.setval('public.users_id_seq', 1, false);


--
-- Name: alertas_ti alertas_ti_pkey; Type: CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.alertas_ti
    ADD CONSTRAINT alertas_ti_pkey PRIMARY KEY (id);


--
-- Name: behavior_logs behavior_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.behavior_logs
    ADD CONSTRAINT behavior_logs_pkey PRIMARY KEY (id);


--
-- Name: checkout_logs checkout_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.checkout_logs
    ADD CONSTRAINT checkout_logs_pkey PRIMARY KEY (id);


--
-- Name: device_health device_health_pkey; Type: CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.device_health
    ADD CONSTRAINT device_health_pkey PRIMARY KEY (id);


--
-- Name: devices devices_name_key; Type: CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_name_key UNIQUE (name);


--
-- Name: devices devices_pkey; Type: CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_pkey PRIMARY KEY (id);


--
-- Name: devices devices_serial_number_key; Type: CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_serial_number_key UNIQUE (serial_number);


--
-- Name: faqs faqs_pkey; Type: CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.faqs
    ADD CONSTRAINT faqs_pkey PRIMARY KEY (id);


--
-- Name: filiais filiais_codigo_key; Type: CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.filiais
    ADD CONSTRAINT filiais_codigo_key UNIQUE (codigo);


--
-- Name: filiais filiais_nome_key; Type: CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.filiais
    ADD CONSTRAINT filiais_nome_key UNIQUE (nome);


--
-- Name: filiais filiais_pkey; Type: CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.filiais
    ADD CONSTRAINT filiais_pkey PRIMARY KEY (id);


--
-- Name: support_tickets support_tickets_pkey; Type: CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.support_tickets
    ADD CONSTRAINT support_tickets_pkey PRIMARY KEY (id);


--
-- Name: technical_docs technical_docs_pkey; Type: CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.technical_docs
    ADD CONSTRAINT technical_docs_pkey PRIMARY KEY (id);


--
-- Name: users users_colaborador_id_key; Type: CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_colaborador_id_key UNIQUE (colaborador_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: alertas_ti alertas_ti_filial_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.alertas_ti
    ADD CONSTRAINT alertas_ti_filial_id_fkey FOREIGN KEY (filial_id) REFERENCES public.filiais(id);


--
-- Name: behavior_logs behavior_logs_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.behavior_logs
    ADD CONSTRAINT behavior_logs_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(id);


--
-- Name: behavior_logs behavior_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.behavior_logs
    ADD CONSTRAINT behavior_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: checkout_logs checkout_logs_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.checkout_logs
    ADD CONSTRAINT checkout_logs_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(id);


--
-- Name: checkout_logs checkout_logs_filial_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.checkout_logs
    ADD CONSTRAINT checkout_logs_filial_id_fkey FOREIGN KEY (filial_id) REFERENCES public.filiais(id);


--
-- Name: checkout_logs checkout_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.checkout_logs
    ADD CONSTRAINT checkout_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: device_health device_health_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.device_health
    ADD CONSTRAINT device_health_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(id);


--
-- Name: devices devices_current_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_current_user_id_fkey FOREIGN KEY (current_user_id) REFERENCES public.users(id);


--
-- Name: devices devices_filial_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_filial_id_fkey FOREIGN KEY (filial_id) REFERENCES public.filiais(id);


--
-- Name: support_tickets support_tickets_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.support_tickets
    ADD CONSTRAINT support_tickets_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(id);


--
-- Name: support_tickets support_tickets_filial_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.support_tickets
    ADD CONSTRAINT support_tickets_filial_id_fkey FOREIGN KEY (filial_id) REFERENCES public.filiais(id);


--
-- Name: support_tickets support_tickets_reported_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.support_tickets
    ADD CONSTRAINT support_tickets_reported_by_user_id_fkey FOREIGN KEY (reported_by_user_id) REFERENCES public.users(id);


--
-- Name: support_tickets support_tickets_resolved_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.support_tickets
    ADD CONSTRAINT support_tickets_resolved_by_user_id_fkey FOREIGN KEY (resolved_by_user_id) REFERENCES public.users(id);


--
-- Name: support_tickets support_tickets_zendesk_added_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.support_tickets
    ADD CONSTRAINT support_tickets_zendesk_added_by_user_id_fkey FOREIGN KEY (zendesk_added_by_user_id) REFERENCES public.users(id);


--
-- Name: users users_filial_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: magabip_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_filial_id_fkey FOREIGN KEY (filial_id) REFERENCES public.filiais(id);


--
-- PostgreSQL database dump complete
--

\unrestrict dbF5MJTBKFqSn6r7pUno4eGrixYqxRsxZNng9RBuuzRO8X7PigmphWVXltLPFhI

