--
-- Name: pais; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE pais (
    id bigint NOT NULL,
    nome character varying(60),
    nome_pt character varying(60),
    sigla character varying(2),
    bacen integer,
    ddi integer
);


ALTER TABLE pais OWNER TO postgres;

--
-- Name: TABLE pais; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE pais IS 'Países e Nações';


--
-- Name: COLUMN pais.sigla; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN pais.sigla IS 'ISO 3166-1 Alpha2';


--
-- Name: pais_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE pais_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE pais_id_seq OWNER TO postgres;

--
-- Name: pais_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE pais_id_seq OWNED BY pais.id;

--
-- Name: pais id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY pais ALTER COLUMN id SET DEFAULT nextval('pais_id_seq'::regclass);

--
-- Data for Name: pais; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY pais (id, nome, nome_pt, sigla, bacen, ddi) FROM stdin;
2	Afghanistan	Afeganistão	AF	132	\N
3	Albania	Albânia, Republica da	AL	175	\N
4	Algeria	Argélia	DZ	590	\N
5	American Samoa	Samoa Americana	AS	6912	\N
6	Andorra	Andorra	AD	370	\N
7	Angola	Angola	AO	400	\N
9	Antarctica	Antártida	AQ	3596	\N
10	Antigua and Barbuda	Antigua e Barbuda	AG	434	\N
12	Armenia	Armênia, Republica da	AM	647	\N
13	Aruba	Aruba	AW	655	\N
15	Austria	Áustria	AT	728	\N
16	Azerbaijan	Azerbaijão, Republica do	AZ	736	\N
17	Bahamas	Bahamas, Ilhas	BS	779	\N
18	Bahrain	Bahrein, Ilhas	BH	809	\N
19	Bangladesh	Bangladesh	BD	817	\N
20	Barbados	Barbados	BB	833	\N
21	Belarus	Belarus, Republica da	BY	850	\N
22	Belgium	Bélgica	BE	876	\N
23	Belize	Belize	BZ	884	\N
24	Benin	Benin	BJ	2291	\N
25	Bermuda	Bermudas	BM	906	\N
26	Bhutan	Butão	BT	1198	\N
27	Bolivia	Bolívia	BO	973	\N
28	Bosnia and Herzegowina	Bósnia-herzegovina (Republica da)	BA	981	\N
29	Botswana	Botsuana	BW	1015	\N
30	Bouvet Island	Bouvet, Ilha	BV	1023	\N
31	British Indian Ocean Territory	Território Britânico do Oceano Indico	IO	7820	\N
32	Brunei Darussalam	Brunei	BN	1082	\N
33	Bulgaria	Bulgária, Republica da	BG	1112	\N
34	Burkina Faso	Burkina Faso	BF	310	\N
35	Burundi	Burundi	BI	1155	\N
36	Cambodia	Camboja	KH	1414	\N
37	Cameroon	Camarões	CM	1457	\N
39	Cape Verde	Cabo Verde, Republica de	CV	1279	\N
41	Central African Republic	Republica Centro-Africana	CF	6408	\N
42	Chad	Chade	TD	7889	\N
43	Chile	Chile	CL	1589	\N
44	China	China, Republica Popular	CN	1600	\N
45	Christmas Island	Christmas, Ilha (Navidad)	CX	5118	\N
46	Cocos (Keeling) Islands	Cocos (Keeling), Ilhas	CC	1651	\N
47	Colombia	Colômbia	CO	1694	\N
48	Comoros	Comores, Ilhas	KM	1732	\N
49	Congo	Congo	CG	1775	\N
50	Congo, the Democratic Republic of the	Congo, Republica Democrática do	CD	8885	\N
51	Cook Islands	Cook, Ilhas	CK	1830	\N
52	Costa Rica	Costa Rica	CR	1961	\N
53	Cote d`Ivoire	Costa do Marfim	CI	1937	\N
54	Croatia (Hrvatska)	Croácia (Republica da)	HR	1953	\N
55	Cuba	Cuba	CU	1996	\N
56	Cyprus	Chipre	CY	1635	\N
57	Czech Republic	Tcheca, Republica	CZ	7919	\N
58	Denmark	Dinamarca	DK	2321	\N
59	Djibouti	Djibuti	DJ	7838	\N
60	Dominica	Dominica, Ilha	DM	2356	\N
61	Dominican Republic	Republica Dominicana	DO	6475	\N
62	East Timor	Timor Leste	TL	7951	\N
63	Ecuador	Equador	EC	2399	\N
64	Egypt	Egito	EG	2402	\N
65	El Salvador	El Salvador	SV	6874	\N
66	Equatorial Guinea	Guine-Equatorial	GQ	3310	\N
67	Eritrea	Eritreia	ER	2437	\N
68	Estonia	Estônia, Republica da	EE	2518	\N
69	Ethiopia	Etiópia	ET	2534	\N
70	Falkland Islands (Malvinas)	Falkland (Ilhas Malvinas)	FK	2550	\N
71	Faroe Islands	Feroe, Ilhas	FO	2593	\N
72	Fiji	Fiji	FJ	8702	\N
73	Finland	Finlândia	FI	2712	\N
74	France	Franca	FR	2755	\N
76	French Guiana	Guiana francesa	GF	3255	\N
77	French Polynesia	Polinésia Francesa	PF	5991	\N
78	French Southern Territories	Terras Austrais e Antárticas Francesas	TF	3607	\N
79	Gabon	Gabão	GA	2810	\N
80	Gambia	Gambia	GM	2852	\N
81	Georgia	Georgia, Republica da	GE	2917	\N
82	Germany	Alemanha	DE	230	\N
83	Ghana	Gana	GH	2895	\N
84	Gibraltar	Gibraltar	GI	2933	\N
85	Greece	Grécia	GR	3018	\N
86	Greenland	Groenlândia	GL	3050	\N
87	Grenada	Granada	GD	2976	\N
88	Guadeloupe	Guadalupe	GP	3093	\N
89	Guam	Guam	GU	3131	\N
90	Guatemala	Guatemala	GT	3174	\N
91	Guinea	Guine	GN	3298	\N
92	Guinea-Bissau	Guine-Bissau	GW	3344	\N
93	Guyana	Guiana	GY	3379	\N
94	Haiti	Haiti	HT	3417	\N
95	Heard and Mc Donald Islands	Ilha Heard e Ilhas McDonald	HM	3603	\N
96	Holy See (Vatican City State)	Vaticano, Estado da Cidade do	VA	8486	\N
97	Honduras	Honduras	HN	3450	\N
98	Hong Kong	Hong Kong	HK	3514	\N
99	Hungary	Hungria, Republica da	HU	3557	\N
100	Iceland	Islândia	IS	3794	\N
102	Indonesia	Indonésia	ID	3654	\N
103	Iran (Islamic Republic of)	Ira, Republica Islâmica do	IR	3727	\N
104	Iraq	Iraque	IQ	3697	\N
105	Ireland	Irlanda	IE	3751	\N
106	Israel	Israel	IL	3832	\N
108	Jamaica	Jamaica	JM	3913	\N
110	Jordan	Jordânia	JO	4030	\N
111	Kazakhstan	Cazaquistão, Republica do	KZ	1538	\N
112	Kenya	Quênia	KE	6238	\N
113	Kiribati	Kiribati	KI	4111	\N
114	Korea, Democratic People`s Republic of	Coreia, Republica Popular Democrática da	KP	1872	\N
115	Korea, Republic of	Coreia, Republica da	KR	1902	\N
38	Canada	Canadá	CA	1490	1
40	Cayman Islands	Ilhas Caimã	KY	1376	1
107	Italy	Itália	IT	3867	39
1	Brazil	Brasil	BR	1058	55
14	Australia	Austrália	AU	698	61
109	Japan	Japão	JP	3999	81
101	India	Índia	IN	3611	91
116	Kuwait	Kuwait	KW	1988	\N
117	Kyrgyzstan	Quirguiz, Republica	KG	6254	\N
118	Lao People`s Democratic Republic	Laos, Republica Popular Democrática do	LA	4200	\N
119	Latvia	Letônia, Republica da	LV	4278	\N
120	Lebanon	Líbano	LB	4316	\N
121	Lesotho	Lesoto	LS	4260	\N
122	Liberia	Libéria	LR	4340	\N
123	Libyan Arab Jamahiriya	Líbia	LY	4383	\N
124	Liechtenstein	Liechtenstein	LI	4405	\N
125	Lithuania	Lituânia, Republica da	LT	4421	\N
126	Luxembourg	Luxemburgo	LU	4456	\N
127	Macau	Macau	MO	4472	\N
128	North Macedonia	Macedônia do Norte	MK	4499	\N
129	Madagascar	Madagascar	MG	4502	\N
130	Malawi	Malavi	MW	4588	\N
131	Malaysia	Malásia	MY	4553	\N
132	Maldives	Maldivas	MV	4618	\N
133	Mali	Mali	ML	4642	\N
134	Malta	Malta	MT	4677	\N
135	Marshall Islands	Marshall, Ilhas	MH	4766	\N
136	Martinique	Martinica	MQ	4774	\N
137	Mauritania	Mauritânia	MR	4880	\N
138	Mauritius	Mauricio	MU	4855	\N
139	Mayotte	Mayotte (Ilhas Francesas)	YT	4885	\N
140	Mexico	México	MX	4936	\N
141	Micronesia, Federated States of	Micronesia	FM	4995	\N
142	Moldova, Republic of	Moldávia, Republica da	MD	4944	\N
144	Mongolia	Mongólia	MN	4979	\N
145	Montserrat	Montserrat, Ilhas	MS	5010	\N
146	Morocco	Marrocos	MA	4740	\N
147	Mozambique	Moçambique	MZ	5053	\N
148	Myanmar	Mianmar (Birmânia)	MM	930	\N
149	Namibia	Namíbia	NA	5070	\N
150	Nauru	Nauru	NR	5088	\N
151	Nepal	Nepal	NP	5177	\N
152	Netherlands	Países Baixos (Holanda)	NL	5738	\N
154	New Caledonia	Nova Caledonia	NC	5428	\N
155	New Zealand	Nova Zelândia	NZ	5487	\N
156	Nicaragua	Nicarágua	NI	5215	\N
157	Niger	Níger	NE	5258	\N
158	Nigeria	Nigéria	NG	5282	\N
159	Niue	Niue, Ilha	NU	5312	\N
160	Norfolk Island	Norfolk, Ilha	NF	5355	\N
161	Northern Mariana Islands	Marianas do Norte	MP	4723	\N
162	Norway	Noruega	NO	5380	\N
163	Oman	Oma	OM	5568	\N
164	Pakistan	Paquistão	PK	5762	\N
165	Palau	Palau	PW	5754	\N
166	Panama	Panamá	PA	5800	\N
167	Papua New Guinea	Papua Nova Guine	PG	5452	\N
168	Paraguay	Paraguai	PY	5860	\N
169	Peru	Peru	PE	5894	\N
170	Philippines	Filipinas	PH	2674	\N
171	Pitcairn	Pitcairn, Ilha	PN	5932	\N
172	Poland	Polônia, Republica da	PL	6033	\N
173	Portugal	Portugal	PT	6076	\N
174	Puerto Rico	Porto Rico	PR	6114	\N
175	Qatar	Catar	QA	1546	\N
176	Reunion	Reunião, Ilha	RE	6602	\N
177	Romania	Romênia	RO	6700	\N
179	Rwanda	Ruanda	RW	6750	\N
180	Saint Kitts and Nevis	São Cristovão e Neves, Ilhas	KN	6955	\N
181	Saint LUCIA	Santa Lucia	LC	7153	\N
182	Saint Vincent and the Grenadines	São Vicente e Granadinas	VC	7056	\N
183	Samoa	Samoa	WS	6904	\N
184	San Marino	San Marino	SM	6971	\N
185	Sao Tome and Principe	São Tome e Príncipe, Ilhas	ST	7200	\N
186	Saudi Arabia	Arábia Saudita	SA	531	\N
187	Senegal	Senegal	SN	7285	\N
188	Seychelles	Seychelles	SC	7315	\N
189	Sierra Leone	Serra Leoa	SL	7358	\N
190	Singapore	Cingapura	SG	7412	\N
191	Slovakia (Slovak Republic)	Eslovaca, Republica	SK	2470	\N
192	Slovenia	Eslovênia, Republica da	SI	2461	\N
193	Solomon Islands	Salomão, Ilhas	SB	6777	\N
194	Somalia	Somalia	SO	7480	\N
196	South Georgia and the South Sandwich Islands	Ilhas Geórgia do Sul e Sandwich do Sul	GS	2925	\N
197	Spain	Espanha	ES	2453	\N
198	Sri Lanka	Sri Lanka	LK	7501	\N
199	St. Helena	Santa Helena	SH	7102	\N
200	St. Pierre and Miquelon	São Pedro e Miquelon	PM	7005	\N
201	Sudan	Sudão	SD	7595	\N
202	Suriname	Suriname	SR	7706	\N
203	Svalbard and Jan Mayen Islands	Svalbard e Jan Mayen	SJ	7552	\N
204	Swaziland	Eswatini	SZ	7544	\N
205	Sweden	Suécia	SE	7641	\N
206	Switzerland	Suíça	CH	7676	\N
207	Syrian Arab Republic	Síria, Republica Árabe da	SY	7447	\N
208	Taiwan, Province of China	Formosa (Taiwan)	TW	1619	\N
209	Tajikistan	Tadjiquistao, Republica do	TJ	7722	\N
210	Tanzania, United Republic of	Tanzânia, Republica Unida da	TZ	7803	\N
211	Thailand	Tailândia	TH	7765	\N
212	Togo	Togo	TG	8001	\N
213	Tokelau	Toquelau, Ilhas	TK	8052	\N
214	Tonga	Tonga	TO	8109	\N
215	Trinidad and Tobago	Trinidad e Tobago	TT	8150	\N
216	Tunisia	Tunísia	TN	8206	\N
217	Turkey	Turquia	TR	8273	\N
218	Turkmenistan	Turcomenistão, Republica do	TM	8249	\N
219	Turks and Caicos Islands	Turcas e Caicos, Ilhas	TC	8230	\N
220	Tuvalu	Tuvalu	TV	8281	\N
221	Uganda	Uganda	UG	8338	\N
222	Ukraine	Ucrânia	UA	8311	\N
223	United Arab Emirates	Emirados Árabes Unidos	AE	2445	\N
224	United Kingdom	Reino Unido	GB	6289	\N
225	United States	Estados Unidos	US	2496	\N
226	United States Minor Outlying Islands	Ilhas Menores Distantes dos Estados Unidos	UM	18664	\N
227	Uruguay	Uruguai	UY	8451	\N
195	South Africa	África do Sul	ZA	7560	27
143	Monaco	Mônaco	MC	4952	377
228	Uzbekistan	Uzbequistão, Republica do	UZ	8478	\N
229	Vanuatu	Vanuatu	VU	5517	\N
230	Venezuela	Venezuela	VE	8508	\N
231	Viet Nam	Vietnã	VN	8583	\N
232	Virgin Islands (British)	Virgens, Ilhas (Britânicas)	VG	8630	\N
233	Virgin Islands (U.S.)	Virgens, Ilhas (E.U.A.)	VI	8664	\N
234	Wallis and Futuna Islands	Wallis e Futuna, Ilhas	WF	8753	\N
235	Western Sahara	Saara Ocidental	EH	6858	\N
236	Yemen	Iémen	YE	3573	\N
237	Yugoslavia	Iugoslávia, República Fed. da	YU	3883	\N
238	Zambia	Zâmbia	ZM	8907	\N
239	Zimbabwe	Zimbabue	ZW	6653	\N
240	Bailiwick of Guernsey	Guernsey, Ilha do Canal (Inclui Alderney e Sark)	GG	1504	\N
241	Bailiwick of Jersey	Jersey, Ilha do Canal	JE	1508	\N
243	Isle of Man	Man, Ilha de	IM	3595	\N
246	Crna Gora (Montenegro)	Montenegro	ME	4985	\N
247	SÉRVIA	Republika Srbija	RS	7370	\N
248	Republic of South Sudan	Sudao do Sul	SS	7600	\N
249	Zona del Canal de Panamá	Zona do Canal do Panamá	\N	8958	\N
252	Dawlat Filasṭīn	Palestina	PS	5780	\N
253	Åland Islands	Aland, Ilhas	AX	153	\N
254	Saint Barthélemy	Coletividade de São Bartolomeu	BL	3598	\N
255	Curaçao	Curaçao	CW	200	\N
256	Saint Martin	São Martinho, Ilha de (Parte Francesa)	SM	6980	\N
258	Bonaire	Bonaire	AN	990	\N
259	Antartica	Antartica	AQ	420	\N
260	Heard Island and McDonald Islands	Ilha Herad e Ilhas Macdonald	AU	3433	\N
261	Saint-Barthélemy	São Bartolomeu	FR	6939	\N
262	Saint Martin	São Martinho, Ilha de (Parte Holandesa)	SM	6998	\N
263	Terres Australes et Antarctiques Françaises	Terras Austrais e Antárcticas Francesas	TF	7811	\N
8	Anguilla	Anguila	AI	418	1
11	Argentina	Argentina	AR	639	54
178	Russian Federation	Rússia, Federação da	RU	6769	7
\.

--
-- Name: pais_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('pais_id_seq', 1, false);


--
-- Name: pais pais_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY pais
    ADD CONSTRAINT pais_pkey PRIMARY KEY (id);
