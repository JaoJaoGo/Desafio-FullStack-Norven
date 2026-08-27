--
-- Name: estado; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE estado (
    id bigint NOT NULL,
    nome character varying(60),
    uf character varying(2),
    ibge integer,
    pais integer,
    ddd json
);


ALTER TABLE estado OWNER TO postgres;

--
-- Name: TABLE estado; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE estado IS 'Unidades Federativas';


--
-- Name: estado_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE estado_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE estado_id_seq OWNER TO postgres;

--
-- Name: estado_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE estado_id_seq OWNED BY estado.id;


--
-- Name: estado id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY estado ALTER COLUMN id SET DEFAULT nextval('estado_id_seq'::regclass);

--
-- Data for Name: estado; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY estado (id, nome, uf, ibge, pais, ddd) FROM stdin;
1	Acre	AC	12	1	[68]
2	Alagoas	AL	27	1	[82]
3	Amazonas	AM	13	1	[97,92]
4	Amapá	AP	16	1	[96]
5	Bahia	BA	29	1	[77,75,73,74,71]
6	Ceará	CE	23	1	[88,85]
7	Distrito Federal	DF	53	1	[61]
8	Espírito Santo	ES	32	1	[28,27]
9	Goiás	GO	52	1	[62,64,61]
10	Maranhão	MA	21	1	[99,98]
11	Minas Gerais	MG	31	1	[34,37,31,33,35,38,32]
12	Mato Grosso do Sul	MS	50	1	[67]
13	Mato Grosso	MT	51	1	[65,66]
14	Pará	PA	15	1	[91,94,93]
15	Paraíba	PB	25	1	[83]
16	Pernambuco	PE	26	1	[81,87]
17	Piauí	PI	22	1	[89,86]
18	Paraná	PR	41	1	[43,41,42,44,45,46]
19	Rio de Janeiro	RJ	33	1	[24,22,21]
20	Rio Grande do Norte	RN	24	1	[84]
21	Rondônia	RO	11	1	[69]
22	Roraima	RR	14	1	[95]
23	Rio Grande do Sul	RS	43	1	[53,54,55,51]
24	Santa Catarina	SC	42	1	[47,48,49]
25	Sergipe	SE	28	1	[79]
26	São Paulo	SP	35	1	[11,12,13,14,15,16,17,18,19]
27	Tocantins	TO	17	1	[63]
99	Exterior	EX	99	\N	\N
\.

--
-- Name: estado_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('estado_id_seq', 99, false);

--
-- Name: estado estado_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY estado
    ADD CONSTRAINT estado_pkey PRIMARY KEY (id);
