from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, List

from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.functional import cached_property


def forTemplate(cls):
    # Enum class call in template raises error and abort with empty string
    # setting do_not_call_in_templates = True skips the call portion
    cls.do_not_call_in_templates = True
    return cls


@forTemplate
class BucketKeys(StrEnum):
    COMMUNITY = "community"
    TNA = "tna"
    NONTNA = "nonTna"


@forTemplate
class SearchTabs(StrEnum):
    ALL = "All results"
    CATALOGUE = "Catalogue results"
    WEBSITE = "Our website results"


class Aggregation(StrEnum):
    """Aggregated counts to include with response.

    Supported by /search endpoints.
    """

    TOPIC = "topic"
    COLLECTION = "collection"
    GROUP = "group"
    LEVEL = "level"
    CLOSURE = "closure"
    CATALOGUE_SOURCE = "catalogueSource"
    HELD_BY = "heldBy"
    TYPE = "type"
    COUNTRY = "country"
    LOCATION = "location"
    COMMUNITY = "community"
    ENRICHMENT_LOC = "enrichmentLoc"
    ENRICHMENT_ORG = "enrichmentOrg"
    ENRICHMENT_PER = "enrichmentPer"
    ENRICHMENT_MISC = "enrichmentMisc"


DEFAULT_AGGREGATIONS = [
    # Aggregation.GROUP # TODO: Keep, not in scope for Ohos-Etna at this time
    # TODO:Rosetta + ":30",  # Fetch more 'groups' so that we receive counts for any bucket/tab options we might be showing.
]

TAG_VIEW_AGGREGATIONS = [
    Aggregation.COMMUNITY.value,
    Aggregation.ENRICHMENT_LOC.value,
    Aggregation.ENRICHMENT_PER.value,
    Aggregation.ENRICHMENT_ORG.value,
    Aggregation.ENRICHMENT_MISC.value,
]


@dataclass
class Bucket:
    key: str
    label: str
    description: str = None
    result_count: int = None
    is_current: bool = False
    results: List[Any] = None

    # By default, 10 items of each aggregation are requested from the API. This can be overridden by using a string in the format '{name}:{number_of_items}'
    aggregations: List[str] = field(default_factory=lambda: DEFAULT_AGGREGATIONS)

    @cached_property
    def aggregations_normalised(self) -> List[str]:
        """
        Returns a list of strings to include as the 'aggregations' option value when assembling
        an API request for this bucket. Each string must be in the format "filter-name:item-count".
        """
        values = []
        for aggregation in self.aggregations:
            bits = aggregation.split(":")
            # TODO: Keep, not in scope for Ohos-Etna at this time
            values.append(bits[0])
            # if len(bits) == 2:
            #     values.append(bits[0] + ":" + bits[1])
            # else:
            #     values.append(bits[0] + ":10")
        return values

    def __post_init__(self):
        self.aggregations = self.aggregations_normalised

    @property
    def label_with_count(self):
        if self.result_count is None:
            return self.label
        return self.label + f" ({intcomma(self.result_count)})"


@dataclass
class BucketList:
    buckets: List[Bucket]

    @property
    def current(self):
        for bucket in self.buckets:
            if bucket.is_current:
                return bucket

    def as_choices(self):
        for bucket in self.buckets:
            yield (bucket.key, bucket.label)

    def get_bucket(self, key):
        for bucket in self.buckets:
            if bucket.key == key:
                return bucket
        raise KeyError(f"Bucket matching the key '{key}' could not be found")

    def __iter__(self):
        yield from self.buckets


CATALOGUE_BUCKETS = BucketList(
    [
        Bucket(
            key=BucketKeys.COMMUNITY,
            label="Results from community collections",
            description="Results for records held at The National Archives that match your search term.",
            # TODO: Keep, not in scope for Ohos-Etna at this time
            # aggregations=DEFAULT_AGGREGATIONS + [Aggregation.COLLECTION],
            aggregations=[Aggregation.COMMUNITY],
        ),
        Bucket(
            key=BucketKeys.TNA,
            label="Results from The National Archives",
            description="Results for records held at The National Archives that match your search term.",
            # TODO: Keep, not in scope for Ohos-Etna at this time
            # aggregations=DEFAULT_AGGREGATIONS
            # + [Aggregation.COLLECTION, Aggregation.LEVEL, Aggregation.CLOSURE],
            aggregations=[Aggregation.COLLECTION],
        ),
        Bucket(
            key=BucketKeys.NONTNA,
            label="Results from other archives",
            description="Results for records held at other archives in the UK (and not at The National Archives) that match your search term.",
            # TODO: Keep, not in scope for Ohos-Etna at this time
            # aggregations=DEFAULT_AGGREGATIONS
            # + [
            #     Aggregation.COLLECTION,
            #     Aggregation.CLOSURE,
            #     Aggregation.HELD_BY,
            #     Aggregation.CATALOGUE_SOURCE,
            # ],
            aggregations=[Aggregation.COLLECTION],
        ),
    ]
)

COLLECTION_NAMES = {
    "A": "Alienation Office",
    "AB": "UK Atomic Energy Authority",
    "ACE": "Records of the Arts Council England",
    "ACT": "Government Actuary's Department",
    "ADM": "Admiralty, Navy, Royal Marines, and Coastguard",
    "AE": "Royal Commission on Historical Monuments (England)",
    "AF": "Parliamentary Boundary Commissions for England and Wales",
    "AH": "Location of Offices Bureau",
    "AHDB": "Agriculture and Horticulture Development Board",
    "AIR": "Air Ministry and Royal Air Force records",
    "AJ": "Consumer Council",
    "AK": "County Courts",
    "AM": "Parliamentary Counsel's Office",
    "AN": "British Transport Commission and the British Railways Board",
    "AO": "National Audit Office and predecessors",
    "AP": "Irish Sailors and Soldiers Land Trust",
    "AR": "The Wallace Collection",
    "ASI": "Inquiry into allegations of human rights abuse of Iraqi nationals by British troops in the aftermath of the'battle of Danny Boy' (The Al-Sweady Inquiry)",
    "ASSI": "Justices of Assize, Gaol Delivery, Oyer and Terminer, and Nisi Prius",
    "AST": "Unemployment Assistance Boards",
    "AT": "Various departments for environment, transport, communities, and local government",
    "AVIA": "Ministry of Aviation",
    "AW": "British European Airways and British Overseas Airways Corporation",
    "AX": "Local Government Boundary Commission for England",
    "AY": "Various Research Institutes and Councils",
    "B": "Bankruptcy and debt relief courts",
    "BA": "Civil Service Department",
    "BC": "Law Commission",
    "BD": "Welsh Office",
    "BE": "Iron and Steel Corporation",
    "BEIS": "Department for Business, Energy and Industrial Strategy",
    "BF": "Pensions Appeal Tribunals",
    "BH": "Hudson's Bay Company Archives",
    "BIS": "Department for Business, Innovation and Skills",
    "BJ": "Meteorological Office",
    "BK": "National Dock Labour Corporation and National Dock Labour Board",
    "BL": "Council on Tribunals and successors",
    "BLK": "Business Link",
    "BM": "Disabled Persons Employment Corporation Ltd and Remploy Ltd",
    "BN": "Department of Health and Social Security",
    "BP": "The Royal Fine Art Commission",
    "BPC": "British Potato Council",
    "BR": "British Transport Docks Board",
    "BS": "Records of defunct temporary bodies",
    "BT": "Board of Trade and successors",
    "BV": "Parole Board",
    "BW": "British Council",
    "BX": "Coal Industry Social Welfare Organisation",
    "BY": "National Portrait Gallery",
    "C": "Chancery, the Wardrobe, Royal Household, Exchequer and various commissions",
    "CA": "Countryside Agency and successors",
    "CAB": "Cabinet Office",
    "CABE": "Commission for Architecture and the Built Environment",
    "CAOG": "Crown Agents for Overseas Governments and Administrations",
    "CB": "National Playing Fields Association",
    "CCW": "Consumer Council for Water",
    "CD": "Cinematograph films",
    "CE": "British Museum",
    "CEF": "Centre for Environment, Fisheries and Aquaculture Science (Cefas)",
    "CES": "UK Commission for Employment and Skills and related bodies",
    "CF": "National Health Service hospitals",
    "CHAR": "Charity Commissioners and Charity Commission",
    "CHES": "Palatinate of Chester, including the county of Flint",
    "CHIL": "The Iraq Inquiry: the Official Records of the Public Inquiry",
    "CJ": "Northern Ireland Office",
    "CK": "Commission for Racial Equality and predecessors",
    "CL": "Certification Office for Trade Unions and Employers' Associations",
    "CLG": "Department of Communities and Local Government",
    "CM": "Property Services Agency",
    "CN": "Photographic prints and negatives extracted from various record series",
    "CO": "Colonial Office, Commonwealth and Foreign and Commonwealth Offices",
    "COAL": "National Coal Board and predecessors, and related bodies",
    "COPY": "Copyright Office and Stationers' Company",
    "COU": "National Parks Commission and the Countryside Commission",
    "CP": "Court of Common Pleas",
    "CPS": "Crown Prosecution Service",
    "CRES": "The Crown Estate and predecessors",
    "CRIM": "Central Criminal Court",
    "CSC": "Civil Service Commission",
    "CSPR": "Civil Service Pay Research Unit",
    "CT": "National Insurance Commissioners and the Social Security Commissioners",
    "CUST": "Boards of Customs, Excise, and Customs and Excise, and HM Revenue and Customs",
    "CV": "Value Added Tax Tribunals",
    "CW": "Advisory, Conciliation and Arbitration Service",
    "CWG": "Commonwealth War Graves Commission",
    "CX": "Price Commission",
    "CY": "Royal Commission on Environmental Pollution",
    "D": "Rural Development Commission and predecessors",
    "DB": "Council for National Academic Awards",
    "DC": "London Museum",
    "DD": "Local Government Boundary Commission for Wales",
    "DEFE": "Ministry of Defence",
    "DEL": "High Court of Delegates",
    "DEX": "Department for Exiting the European Union",
    "DF": "Natural History Museum",
    "DFT": "Department for Transport",
    "DG": "International Organisations",
    "DGOV": "Directgov",
    "DH": "Records of the British Library and the British Museum Library",
    "DIT": "Department for International Trade",
    "DJ": "Post Office Users' National Council",
    "DK": "National Ports Council",
    "DL": "Duchy of Lancaster",
    "DM": "Occupational Pensions Board",
    "DN": "Public Health Laboratory Service Board",
    "DO": "Dominions Office, and Commonwealth Relations and Foreign and Commonwealth Offices",
    "DPP": "Director of Public Prosecutions",
    "DR": "Civil Aviation Authority",
    "DSA": "Driving Standards Agency",
    "DSIR": "Department of Scientific and Industrial Research",
    "DT": "General Nursing Council for England and Wales",
    "DURH": "Palatinate of Durham",
    "DV": "Central Midwives Board",
    "DVLA": "Driver and Vehicle Licensing Agency",
    "DW": "Council for the Training of Health Visitors",
    "DX": "Panel of Assessors for District Nurse Training",
    "DY": "Joint Board of Clinical Nursing Studies",
    "E": "Exchequer, Office of First Fruits and Tenths, and the Court of Augmentations",
    "EA": "National Council, and Council, for Educational Technology",
    "EB": "Commission on Museums and Galleries",
    "EC": "Electoral Commission",
    "ECCL": "Ecclesiastical Commission",
    "ECG": "Export Credit Guarantee Department",
    "ED": "Department of Education and Science",
    "EDG": "Employment Department, Training Agency",
    "EF": "Health and Safety Commission and Executive",
    "EG": "Department of Energy",
    "EH": "Pay Board",
    "EJ": "Schools Council for Curriculum and Examinations",
    "EL": "Council for the Encouragement of Music and the Arts and Arts Council of Great Britain",
    "EM": "Special Commissioners of Income Tax",
    "EN": "Imperial War Museum",
    "EP": "Reviewing Committee on the Export of Works of Art",
    "ER": "Standing Civilian Courts",
    "ES": "Atomic Weapons Establishment",
    "ET": "Manpower Services Commission",
    "EV": "Science and Engineering Research Council",
    "EW": "Department of Economic Affairs",
    "EXT": "Documents and objects extracted from various record series",
    "EY": "Social Science Research Council",
    "F": "Forestry Commission",
    "FA": "Office of Gas Supply (OFGAS)",
    "FB": "Central Bureau for Educational Visits and Exchanges",
    "FCO": "Foreign and Commonwealth Office and predecessors",
    "FD": "Medical Research Council",
    "FEC": "Forfeited Estates Commission",
    "FERA": "Food and Environment Research Agency",
    "FG": "National Economic Development Council and National Economic Development Office",
    "FH": "National Bus Company",
    "FJ": "Commission for the New Towns",
    "FK": "Office of the Secretary of State for Local Government and Regional Planning",
    "FL": "Adult Literacy Resource Agency",
    "FM": "Historic Buildings and Monuments Commission for England (English Heritage)",
    "FN": "Pilotage Commission",
    "FO": "Foreign Office",
    "FP": "Health Education Council and Health Education Authority",
    "FR": "Legal Aid Board, the Legal Services Commission, and predecessors",
    "FS": "Registry of Friendly Societies",
    "FT": "Nature Conservancy, the Nature Conservancy Council and English Nature",
    "FV": "Department of Trade and Industry, 1970-1974",
    "FW": "National Curriculum Council",
    "FY": "Potato Marketing Boards",
    "GCDA": "Government Car and Despatch Agency",
    "GEO": "Government Equalities Office",
    "GFM": "Copies of captured records of the German, Italian and Japanese Governments.",
    "GIRO": "National Girobank and Predecessors",
    "GT": "General Teaching Council for England",
    "GUK": "Records of GOV.UK",
    "HA": "Natural Environment Research Council",
    "HB": "Office of Electricity Regulation",
    "HCA": "High Court of Admiralty and colonial Vice-Admiralty courts",
    "HD": "Secret Intelligence Service",
    "HE": "English National Board for Nursing, Midwifery and Health Visiting",
    "HF": "Ministry of Technology",
    "HK": "Museums Association",
    "HLG": "Ministry of Housing and Local Government",
    "HMC": "Royal Commission on Historical Manuscripts",
    "HN": "Central Computer and Telecommunications Agency",
    "HO": "Home Office",
    "HP": "National Radiological Protection Board",
    "HR": "Marshall Aid Commemoration Commission",
    "HS": "Special Operations Executive",
    "HT": "Commission for Local Administration in England",
    "HV": "Crown Estate Paving Commission",
    "HW": "Government Communications Headquarters (GCHQ)",
    "HWA": "Highways Agency",
    "HX": "Civil Service Occupational Health Service and Civil Service Occupational Health and Safety Agency",
    "HY": "Intervention Board for Agricultural Produce",
    "IBS": "Reserved for forthcoming transfer",
    "ILB": "Coroner's Inquests into the London Bombings of 7 July 2005",
    "IND": "Indexes to various series",
    "INF": "Central Office of Information",
    "IPSA": "Independent Parliamentary Standards Authority",
    "IR": "Boards of Stamps, Taxes, Excise, Stamps and Taxes, and Inland Revenue",
    "J": "Supreme Court of Judicature",
    "JA": "Department of Health",
    "JB": "Department for Work and Pensions",
    "JC": "Office of Water Services (Ofwat) and the Water Services Regulation Authority",
    "JD": "Monopolies and Mergers Commission",
    "JE": "Office of the National Lottery",
    "JF": "Department of Prices and Consumer Protection",
    "JH": "Ministry of Land and Natural Resources",
    "JK": "Office of Her Majesty's Chief Inspector of Schools in Wales",
    "JL": "Curriculum Council for Wales and the Curriculum and Assessment Authority for Wales",
    "JM": "Further Education and Higher Education Funding Councils for Wales",
    "JN": "Committee on Standards in Public Life and related bodies",
    "JP": "The Adjudicators Office",
    "JR": "Office of the Rail Regulator",
    "JS": "Further Education Funding Council for England",
    "JT": "Local Government Commission for England",
    "JUST": "Records of itinerant justices and other court records",
    "JV": "Milk Marketing Board",
    "JW": "Metrication Board",
    "JX": "Data Protection Registrar and Successors",
    "JY": "Civil Service College",
    "KA": "Office of Passenger Rail Franchising",
    "KB": "Court of King's Bench",
    "KC": "School Examinations and Assessment Council",
    "KD": "Coal Authority",
    "KE": "Royal Air Force Museum",
    "KF": "Inquiry into Exports of Defence Equipment to Iraq and Related Prosecutions (Scott Inquiry)",
    "KH": "Special Educational Needs Tribunal",
    "KJ": "Government Property Lawyers",
    "KL": "Funding Agency for Schools",
    "KM": "Food Standards Agency",
    "KN": "United Kingdom Central Council for Nursing, Midwifery and Health Visiting",
    "KP": "Advisory Committee on Legal Education and Conduct",
    "KR": "Joint Nature Conservation Committee",
    "KS": "Radiocommunications Agency",
    "KT": "Office for Standards in Education",
    "KV": "Security Service",
    "KW": "Royal Parks Agency",
    "KX": "Historic Royal Palaces Agency",
    "KY": "National Council for Vocational Qualifications",
    "LAB": "Departments responsible for labour and employment matters",
    "LAR": "Land Registry",
    "LB": "Combined Tax Tribunal",
    "LC": "Lord Chamberlain and other officers of the Royal Household",
    "LCO": "Lord Chancellor's Office",
    "LD": "Office of Fair Trading",
    "LE": "The Court Service and Successors",
    "LEO": "Lyons Inquiry into Local Government",
    "LEV": "Inquiry into the Culture, Practices and Ethics of the Press (Leveson Inquiry)",
    "LF": "Office of Telecommunications (Oftel)",
    "LH": "Women's National Commission",
    "LITV": "Inquiry into the death of Alexander Litvinenko: Evidence, Correspondence and Report",
    "LJ": "Council for the Central Laboratory of the Research Councils",
    "LK": "Police Complaints Authority and Police Complaints Board",
    "LM": "Department of Transport",
    "LN": "Building Societies Commission",
    "LO": "Law Officers' Department",
    "LOC": "London 2012 Organising Committee of the Olympic and Paralympic Games (LOCOG)",
    "LP": "Department of the Environment, Transport and the Regions",
    "LR": "Office of the Auditors of Land Revenue",
    "LRRO": "Land Revenue Records and Enrolments",
    "LS": "Lord Steward, the Board of Green Cloth",
    "LSIS": "Learning and Skills Improvement Service",
    "LT": "Lands Tribunal",
    "LV": "Friendly Societies Commission",
    "LX": "Contributions Agency",
    "LY": "Child Maintenance and Enforcement Commission",
    "MAF": "Agriculture, Fisheries and Food Departments",
    "MCA": "Maritime and Coastguard Agency",
    "MEPO": "Metropolitan Police Office",
    "MF": "Maps and plans extracted to flat storage from various departments",
    "MFC": "Maps and plans extracted to flat storage from various departments formerly held at the Public Record Office, Chancery Lane",
    "MFQ": "Maps and plans extracted to flat storage from various departments held at the Public Record Office, Kew",
    "MH": "Ministry of Health",
    "MHRA": "Medicines and Healthcare Products Regulatory Agency",
    "MINT": "Royal Mint",
    "MJ": "Ministry of Justice",
    "MM": "Millennium Commission",
    "MONW": "Royal Commission on Ancient and Historical Monuments in Wales and Monmouthshire",
    "MPA": "Chancery: maps and plans extracted to flat storage",
    "MPAA": "Chancery: maps and plans extracted to extra large flat storage",
    "MPB": "Exchequer: maps and plans extracted to flat storage",
    "MPBB": "Exchequer: maps and plans extracted to extra large flat storage",
    "MPC": "Duchy of Lancaster: maps and plans extracted to flat storage",
    "MPCC": "Duchy of Lancaster: maps and plans extracted to extra large flat storage",
    "MPD": "Treasury: maps and plans extracted to flat storage",
    "MPDD": "Treasury: maps and plans extracted to extra large flat storage",
    "MPE": "Land Revenue Records and Enrolments: maps and plans extracted to flat storage",
    "MPEE": "Land Revenue Records and Enrolments: maps and plans extracted to extra large flat storage",
    "MPF": "State Paper Office: maps and plans extracted to flat storage",
    "MPFF": "State Paper Office: maps and plans extracted to extra large flat storage",
    "MPG": "Colonial Office: maps and plans extracted to flat storage",
    "MPGG": "Colonial Office: maps and plans extracted to extra large flat storage",
    "MPH": "War Office: maps and plans extracted to flat storage",
    "MPHH": "War Office: maps and plans extracted to extra large flat storage",
    "MPI": "Maps and plans extracted to flat storage from records of departments not assigned an individual map extract prefix",
    "MPII": "Maps and plans extracted to extra large flat storage from records of departments not assigned an individual map prefix",
    "MPK": "Foreign Office: maps and plans extracted to flat storage",
    "MPKK": "Foreign Office: maps and plans extracted to extra large flat storage",
    "MPL": "Court of Common Pleas: maps and plans extracted to flat storage",
    "MPLL": "Court of Common Pleas: maps and plans extracted to extra large flat storage",
    "MPM": "Flat maps and drawings of special interest",
    "MPN": "Court of King's Bench: maps and plans extracted to flat storage",
    "MPNN": "Court of King's Bench: maps and plans extracted to extra large flat storage",
    "MPO": "Forestry Commission maps and plans",
    "MPP": "Cabinet Office flat maps",
    "MPQ": "Privy Council: maps and plans extracted to flat storage",
    "MPQQ": "Privy Council: maps and plans extracted to extra large flat storage",
    "MPR": "RAIL flat maps",
    "MPS": "British Transport Historical Record Office: maps, plans and surveys",
    "MPT": "British Transport Commission: maps and plans extracted to flat storage",
    "MPZ": "Maps and plans extracted from records of various departments",
    "MR": "Maps and plans extracted to rolled storage from various departments",
    "MRC": "Maps and plans extracted to rolled storage from various departments formerly held at the Public Record Office, Chancery Lane",
    "MRQ": "Maps and plans extracted to rolled storage from various departments held at the Public Record Office, Kew",
    "MT": "Ministries of Transport and related bodies",
    "MUN": "Ministry of Munitions and successors",
    "NATS": "Ministry of National Service",
    "NB": "Benefits Agency",
    "NC": "National Lottery Charities Board and the Community Fund",
    "NCC": "National Consumer Council",
    "NDA": "Records of the Nuclear Decommissioning Authority and its predecessors",
    "NDO": "National Debt Office",
    "NE": "Central Council for Education and Training in Social Work",
    "NF": "Registry of Trade Unions and Employers Associations",
    "NG": "National Gallery",
    "NH": "Countryside Council for Wales",
    "NIA": "National Insurance Audit Department",
    "NICO": "National Incomes Commission",
    "NJ": "Office of Manpower Economics",
    "NK": "Department of Trade and Industry (1983-2007)",
    "NL": "Independent Commission on the Voting System",
    "NMM": "National Maritime Museum",
    "NOMS": "National Offender Management Service",
    "NP": "Office of the President of Social Security Appeal Tribunals, Medical Appeal Tribunals and Vaccine Damage Tribunals and Independent Tribunal Service",
    "NPL": "National Physical Laboratory",
    "NR": "Central Rail Users Consultative Committee",
    "NSC": "National Savings Committee, the Post Office Savings Department and the Department for National Savings",
    "NT": "Inquiry into the Matters Arising from the Death of Stephen Lawrence",
    "NV": "Department for Education and Employment",
    "NW": "Interception of Communications Act Commissioner",
    "NX": "Security Service Act Commissioner",
    "NY": "Intelligence Services Act Commissioner",
    "OBS": "Obsolete lists and indexes",
    "OCM": "Ofcom (the Office of Communications)",
    "OD": "Department of Technical Co-operation, and successive Overseas Development bodies",
    "OLD": "Olympic Lottery Distributor",
    "OPG": "Office of the Public Guardian",
    "OS": "Ordnance Survey of Great Britain",
    "OSA": "Office of the Schools Adjudicator",
    "PALA": "Records of the Palace Court",
    "PB": "Teacher Training Agency and Successors",
    "PC": "Privy Council",
    "PCAP": "Judicial Committee of the Privy Council",
    "PCOM": "Prison Commission and Home Office Prison Department",
    "PCGN": "Permanent Committee on Geographic Names",
    "PD": "New Millennium Experience Company",
    "PEV": "Court of the Honour of Peveril",
    "PF": "Department for Culture, Media and Sport",
    "PH": "Central Council for Education and Training in Social Work",
    "PHSO": "Parliamentary and Health Service Ombudsman",
    "PIN": "Ministry of Pensions and National Insurance",
    "PITA": "Inquiry into Human Tissue Analysis in UK Nuclear Facilities (Redfern Inquiry)",
    "PJ": "Department of Trade, 1974-1983",
    "PL": "Palatinate of Lancaster",
    "PMG": "Paymaster General's Office and predecessors",
    "PN": "Inquiry into BSE",
    "POST": "Royal Mail Group plc and predecessors",
    "POWE": "Ministry of Power",
    "PP": "Keeper of the Privy Purse",
    "PREM": "Prime Minister's Office",
    "PRIS": "King's Bench, Fleet, and Marshalsea prisons",
    "PRO": "Domestic Records of the Public Record Office, Gifts, Deposits, Notes and Transcripts",
    "PROB": "Prerogative Court of Canterbury",
    "PSO": "Keeper of the Privy Seal",
    "PT": "Public Trustee Office",
    "PV": "Department of Industry (1974-1983)",
    "PWLB": "Loan Commissioners and the Public Works Loan Board",
    "PX": "Postal Services Commission",
    "PY": "Office of Gas and Electricity Markets (OFGEM)",
    "QAB": "Queen Anne's Bounty",
    "QAPS": "Archive Production Services: material sent off-site for storage",
    "QFA": "Supplementary Finding Aids from The National Archives",
    "QLIB": "Resource Centre and Library stores material sent off-site for storage",
    "QLX": "List and Index Society store material sent off-site for storage",
    "QPR": "Pipe Roll Society stock sent off-site for storage",
    "RAIL": "Pre-nationalisation railway companies, pre-nationalisation canal and related companies",
    "RB": "Adult Learning Inspectorate",
    "RC": "Learning and Skills Council",
    "RD": "Environment Agency",
    "RECO": "Ministry of Reconstruction",
    "REQ": "Court of Requests",
    "RF": "Insolvency Service",
    "RG": "General Register Office, Social Survey Department, and Office of Population Censuses and Surveys",
    "RGO": "Royal Greenwich Observatory",
    "RH": "Department for Children, Schools and Families and Successor",
    "RJ": "Department created in anticipation of records to be transferred",
    "RM": "Royal Botanic Gardens, Kew",
    "RP": "Radio Authority",
    "RS": "Records originally intended for this code are now in JT",
    "RT": "Commission for Africa",
    "RV": "Report of the Committee of Privy Counsellors appointed to consider authorised procedures for the interrogation of persons suspected of terrorism (Parker Inquiry)",
    "RW": "The National Archives",
    "SA": "Commission for Judicial Appointments and Successors",
    "SB": "The Pensions Regulator",
    "SC": "Special Collections: records of various departments, arranged according to type",
    "SCOT": "Scottish Administration",
    "SD": "Zahid Mubarek Inquiry",
    "SE": "Chemical Regulations Directorate",
    "SF": "Statistics Commission",
    "SFO": "Serious Fraud Office",
    "SH": "Equal Opportunities Commission",
    "SJ": "Gas and Electricity Consumer Council (Energywatch)",
    "SK": "Consumer Council for Postal Services (PostWatch)",
    "SL": "Inquests into the deaths of Diana, Princess of Wales, and Emad El-Din Mohamed Abdel Moneim Fayed",
    "SLC": "Student Loans Company Ltd",
    "SO": "Signet Office",
    "SP": "State Paper Office, including papers of the Secretaries of State up to 1782",
    "SR": "Department for Business, Enterprise and Regulatory Reform",
    "ST": "Department for Innovation, Universities and Skills",
    "STAC": "Court of Star Chamber and of other courts",
    "STAT": "Stationery Office",
    "SU": "Department of Energy and Climate Change",
    "SUPP": "Ministry of Supply and successors and the Ordnance Board",
    "SW": "Natural England",
    "T": "HM Treasury",
    "TCB": "Post Office telegraph and telephone service",
    "TCC": "Post Office Corporation (Telecommunications Division)",
    "TCD": "British Telecommunications (public corporation)",
    "TCK": "Private collections of telecommunications related records held by BT Archives",
    "TG": "Tate Gallery",
    "TITH": "Tithe Commission and successors",
    "TR": "Tribunals Service",
    "TS": "Treasury Solicitor and HM Procurator General's Department",
    "TV": "Television Authority and the Independent Broadcasting Authority",
    "UGC": "Higher Education Funding Council for England",
    "UKSC": "The Supreme Court of the United Kingdom",
    "UKTI": "UK Trade & Investment (UKTI)",
    "VC": "The Victoria Climbié Inquiry",
    "VCA": "Vehicle Certification Agency",
    "VL": "Central Veterinary Laboratory and Veterinary Laboratories Agency",
    "VOSA": "Vehicle and Operator Services Agency",
    "WA": "National Assembly for Wales",
    "WALE": "Legal Records Relating to Wales",
    "WARD": "Court of Wards and Liveries",
    "WM": "National Weights and Measures Laboratory",
    "WO": "War Office, Armed Forces, Judge Advocate General, and related bodies",
    "WORK": "Office of Works and successors",
    "ZBOX": "Unfinished and unpublished texts, calendars and finding aids",
    "ZHC": "Publications of the House of Commons",
    "ZHL": "Publications of the House of Lords",
    "ZJ": "London Gazettes",
    "ZLIB": "British Transport Historical Records Office: publications",
    "ZMAP": "Maps and plans formerly held by the Public Record Office Library",
    "ZOS": "Publications of the Ordnance Survey of Great Britain",
    "ZPER": "British Transport Historical Records Office library: periodicals",
    "ZSPC": "British Transport Historical Records Office library: publications",
    "ZWEB": "Regularly Archived Government Websites",
}

COLLECTION_CHOICES = tuple(
    (k, f"{k} - {v}") for k, v in sorted(COLLECTION_NAMES.items(), key=lambda x: x[1])
)


@forTemplate
class LevelKeys(StrEnum):
    LEVEL_1 = "Department"
    LEVEL_2 = "Division"
    LEVEL_3 = "Series"
    LEVEL_4 = "Sub-series"
    LEVEL_5 = "Sub-sub-series"
    LEVEL_6 = "Piece"
    LEVEL_7 = "Item"


@forTemplate
class NonTNALevelKeys(StrEnum):
    LEVEL_1 = "Fonds"
    LEVEL_2 = "Sub-fonds"
    LEVEL_3 = "Sub-sub-fonds"
    LEVEL_4 = "Sub-sub-sub-fonds"
    LEVEL_5 = "Series"
    LEVEL_6 = "Sub-series"
    LEVEL_7 = "Sub-sub-series"
    LEVEL_8 = "Sub-sub-sub-series"
    LEVEL_9 = "File"
    LEVEL_10 = "Item"
    LEVEL_11 = "Sub-item"


LEVELS = (
    "Division",
    "Lettercode",
    "Series",
    "Sub-series",
    "Sub-sub-series",
    "Item",
    "Piece",
)

LEVEL_CHOICES = tuple((level, level) for level in LEVELS)


@forTemplate
class Display(StrEnum):
    """Display type to support veiw, template."""

    LIST = "list"
    GRID = "grid"


@forTemplate
class VisViews(StrEnum):
    """Data visualisation View types to support django view, template."""

    LIST = "list"
    MAP = "map"
    TIMELINE = "timeline"
    TAG = "tag"


@forTemplate
class TagTypes(StrEnum):
    """Tag types values defined by @template.details.enrichment keys"""

    LOCATION = "loc"
    PERSON = "per"
    ORGANISATION = "org"
    MISCELLANEOUS = "misc"
    DATE = "date"


@forTemplate
class TimelineTypes(StrEnum):
    """The timeline view types that can be displayed"""

    CENTURY = "century"  # for items distributed by century
    DECADE = "decade"  # for items distributed by decade for a century
    YEAR = "year"  # for items distributed by year for a decade


TYPE_NAMES = {
    "business": "Business",
    "family": "Family",
    "manor": "Manor",
    "organisation": "Organisation",
    "person": "Person",
}

TYPE_CHOICES = tuple(
    (k, f"{v}") for k, v in sorted(TYPE_NAMES.items(), key=lambda x: x[1])
)

TNA_URLS = {
    "discovery_browse": "https://discovery.nationalarchives.gov.uk/browse/r/h",
    "tna_accessions": "https://www.nationalarchives.gov.uk/accessions",
    "discovery_rec_default_fmt": "https://discovery.nationalarchives.gov.uk/details/r/{id}",
    "discovery_rec_archon_fmt": "https://discovery.nationalarchives.gov.uk/details/a/{id}",
    "discovery_rec_creators_fmt": "https://discovery.nationalarchives.gov.uk/details/c/{id}",
}

CLOSURE_CLOSED_STATUS = [
    "Closed Or Retained Document, Closed Description",
    "Closed Or Retained Document, Open Description",
]


# form-checkbox-attr, ciim-aggs-name, ciim-filter-alias-name
COLLECTION_ATTR_FOR_ALL_BUCKETS = "collection"

# re CIIM param: aggs=<aggs-name>
# map {<aggs-name>:<ohos-aggs-name}
OHOS_CHECKBOX_AGGS_NAME_MAP = {COLLECTION_ATTR_FOR_ALL_BUCKETS: "community"}

# re CIIM param: filter=<alias-name>:<value>
# map: {<filter-alias-name>:<ohos-filter-alias-name>}
# <filter-alias-name> => <camel case of form field>[:<tag type of tag view>]
OHOS_FILTER_ALIAS_NAME_MAP = {
    COLLECTION_ATTR_FOR_ALL_BUCKETS: "collectionOhos",
    "chartSelected:{tag_type}".format(
        tag_type=TagTypes.LOCATION.upper()
    ): Aggregation.ENRICHMENT_LOC,
    "chartSelected:{tag_type}".format(
        tag_type=TagTypes.PERSON.upper()
    ): Aggregation.ENRICHMENT_PER,
    "chartSelected:{tag_type}".format(
        tag_type=TagTypes.ORGANISATION.upper()
    ): Aggregation.ENRICHMENT_ORG,
    "chartSelected:{tag_type}".format(
        tag_type=TagTypes.MISCELLANEOUS.upper()
    ): Aggregation.ENRICHMENT_MISC,
}

"""
CONFIG:
Nested/Hierarchy checkboxes
Nesting of one level i.e. "parent" -> "child/children", others are "orphan"
collections are checkboxes on the form.
Nested collections - collections within a collection

For the nested filter: <collection-name/ciim-value>:(<ciim-aggs-name:at-pos-1>,<long-filter-ciim-aggs-name:at-pos-2>)
"""
NESTED_CHECKBOX_VALUES_AGGS_NAMES_MAP = {
    "Surrey History Centre": ("collectionSurrey", "collectionSurreyAll"),
    "Morrab Photo Archive": ("collectionMorrab", "collectionMorrabAll"),
}

# prefix ends with "-"
PARENT_AGGS_PREFIX = "parent-"
CHILD_AGGS_PREFIX = "child-"
LONG_AGGS_PREFIX = "long-"

NESTED_CHILDREN_KEY = "children"
AGGS_LOOKUP_KEY = "key"

PARENT_PARAM_VALUES = [
    f"{PARENT_AGGS_PREFIX}{aggs[0]}:{value}"
    for value, aggs in NESTED_CHECKBOX_VALUES_AGGS_NAMES_MAP.items()
]

LONG_FILTER_PARAM_VALUES = [
    f"{LONG_AGGS_PREFIX+aggs[1]}:{value}"
    for value, aggs in NESTED_CHECKBOX_VALUES_AGGS_NAMES_MAP.items()
]

PREFIX_AGGS_PARENT_CHILD_KV = {}
for aggs in NESTED_CHECKBOX_VALUES_AGGS_NAMES_MAP.values():
    PREFIX_AGGS_PARENT_CHILD_KV.update(
        {PARENT_AGGS_PREFIX + aggs[0]: CHILD_AGGS_PREFIX + aggs[0]}
    )

PREFIX_FILTER_AGGS = [
    PARENT_AGGS_PREFIX + aggs[0]
    for aggs in NESTED_CHECKBOX_VALUES_AGGS_NAMES_MAP.values()
] + [
    CHILD_AGGS_PREFIX + aggs[0]
    for aggs in NESTED_CHECKBOX_VALUES_AGGS_NAMES_MAP.values()
]

SEE_MORE_LABEL = "See more collections"
SEE_MORE_PREFIX = "SEE-MORE"
SEPERATOR = "::SEP::"  # value seperator
SEE_MORE_VALUE_FMT = (
    f"{SEE_MORE_PREFIX}{SEPERATOR}{SEE_MORE_LABEL}{SEPERATOR}" + "{url}"
)
