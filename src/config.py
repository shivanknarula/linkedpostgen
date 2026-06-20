import os

# Database Path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "robotics_intelligence.db")

# Playwright Scraper settings
HEADLESS = True
MAX_CONCURRENT_TABS = 3
PAGE_TIMEOUT_MS = 12000
STEADY_STATE_TIMEOUT_MS = 1000

# Groq API limits & settings
GROQ_MODEL = "llama-3.3-70b-versatile"
MAX_CONCURRENT_GROQ_CALLS = 5

# Global Target Profiles (Tier 1: High Priority, Tier 2: Rotating Pool)
# Excludes: Sam Altman, Demis Hassabis, Ilya Sutskever, Jensen Huang, Colette Kress, Jay Puri, Debora Shoquist, Arthur Mensch, Jakub Pachocki, Chris Olah, Jared Kaplan, Tom Brown
GLOBAL_PROFILES = [
    # Tier 1 - Highly Active Global Pioneers & CEOS (Always Crawled)
    {
        "url": "https://www.linkedin.com/in/brettadcock/",
        "name": "Brett Adcock",
        "category": "global",
        "tier": 1
    },
    {
        "url": "https://www.linkedin.com/in/yann-lecun/",
        "name": "Yann LeCun",
        "category": "global",
        "tier": 1
    },
    {
        "url": "https://www.linkedin.com/in/andrewng/",
        "name": "Andrew Ng",
        "category": "global",
        "tier": 1
    },
    {
        "url": "https://www.linkedin.com/in/fei-fei-li-66779313/",
        "name": "Fei-Fei Li",
        "category": "global",
        "tier": 1
    },
    {
        "url": "https://www.linkedin.com/in/gdbrockman/",
        "name": "Greg Brockman",
        "category": "global",
        "tier": 1
    },
    {
        "url": "https://www.linkedin.com/in/linxi-fan-7a242a37/",
        "name": "Linxi (Jim) Fan",
        "category": "global",
        "tier": 1
    },
    {
        "url": "https://www.linkedin.com/in/andrej-karpathy-a3a89a19/",
        "name": "Andrej Karpathy",
        "category": "global",
        "tier": 1
    },
    {
        "url": "https://www.linkedin.com/in/mustafa-suleyman/",
        "name": "Mustafa Suleyman",
        "category": "global",
        "tier": 1
    },
    {
        "url": "https://www.linkedin.com/company/boston-dynamics/",
        "name": "Boston Dynamics (Company)",
        "category": "global",
        "tier": 1
    },
    {
        "url": "https://www.linkedin.com/company/figure-ai/",
        "name": "Figure AI (Company)",
        "category": "global",
        "tier": 1
    },

    # Tier 2 - Rotating Pool (Randomly selected subset crawled each run)
    {
        "url": "https://www.linkedin.com/company/agility-robotics/",
        "name": "Agility Robotics",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/company/apptronik/",
        "name": "Apptronik",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/company/1x-technologies/",
        "name": "1X Technologies",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/company/sanctuary-ai/",
        "name": "Sanctuary AI",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/company/physical-intelligence/",
        "name": "Physical Intelligence",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/company/collaborative-robotics/",
        "name": "Collaborative Robotics",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/company/skild-ai/",
        "name": "Skild AI",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/company/covariant-ai/",
        "name": "Covariant AI",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/anima-anandkumar-b413008/",
        "name": "Anima Anandkumar",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/thrun/",
        "name": "Sebastian Thrun",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/jeff-dean-5056/",
        "name": "Jeff Dean",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/j%C3%BCrgen-schmidhuber-441634b/",
        "name": "Jürgen Schmidhuber",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/ruslan-salakhutdinov-9069a5b/",
        "name": "Ruslan Salakhutdinov",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/christopher-manning-02b488b/",
        "name": "Christopher Manning",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/kozyrkov/",
        "name": "Cassie Kozyrkov",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/aidangomez/",
        "name": "Aidan Gomez",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/noam-shazeer-464879/",
        "name": "Noam Shazeer",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/socher/",
        "name": "Richard Socher",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/daphne-koller-17215/",
        "name": "Daphne Koller",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/percy-liang-22a846b/",
        "name": "Percy Liang",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/joelle-pineau-1b07297/",
        "name": "Joelle Pineau",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/raquel-urtasun-995775b/",
        "name": "Raquel Urtasun",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/david-silver-8bb84b/",
        "name": "David Silver",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/oriolvinyals/",
        "name": "Oriol Vinyals",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/dario-amodei-3a216a4/",
        "name": "Dario Amodei",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/geordierose/",
        "name": "Geordie Rose",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/meloneewise/",
        "name": "Melonee Wise",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/chris-anderson-8958221/",
        "name": "Chris Anderson",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/berntbornich/",
        "name": "Bernt Børnich",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/jonathan-hurst-385a49b/",
        "name": "Jonathan Hurst",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/pathakdeepak/",
        "name": "Deepak Pathak",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/sangbae-kim-1122a27/",
        "name": "Sangbae Kim",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/rodney-brooks-11488b3/",
        "name": "Rodney Brooks",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/gill-pratt-58a478b/",
        "name": "Gill Pratt",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/raulbravo/",
        "name": "Raul Bravo",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/daniela-rus-637996/",
        "name": "Daniela Rus",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/ken-goldberg-8bb657/",
        "name": "Ken Goldberg",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/aaron-saunders-b84492/",
        "name": "Aaron Saunders",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/jameskuffner/",
        "name": "James Kuffner",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/prasv/",
        "name": "Pras Velagapudi",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/ayanna-howard/",
        "name": "Ayanna Howard",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/raffaello-d-andrea-a745771/",
        "name": "Raffaello D'Andrea",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/russ-tedrake-0a4a625/",
        "name": "Russ Tedrake",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/drdavidhanson/",
        "name": "Dr. David Hanson",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/dennis-hong-b6a6042b/",
        "name": "Dennis Hong",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/aude-billard-a447814/",
        "name": "Aude Billard",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/sanjivsingh/",
        "name": "Sanjiv Singh",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/robplayter/",
        "name": "Rob Playter",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/rene-haas-5883261/",
        "name": "Rene Haas",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/clementdelangue/",
        "name": "Clement Delangue",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/lexfridman/",
        "name": "Lex Fridman",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/reidhoffman/",
        "name": "Reid Hoffman",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/alexandrwang/",
        "name": "Alexandr Wang",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/aravind-srinivas/",
        "name": "Aravind Srinivas",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/emadmostaque/",
        "name": "Emad Mostaque",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/thomasdohmke/",
        "name": "Thomas Dohmke",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/alighodsi/",
        "name": "Ali Ghodsi",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/dharmesh/",
        "name": "Dharmesh Shah",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/aaronlevie/",
        "name": "Aaron Levie",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/tomasztunguz/",
        "name": "Tomasz Tunguz",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/vinodkhosla/",
        "name": "Vinod Khosla",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/billgross/",
        "name": "Bill Gross",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/amitabh-nag-a5b678/",
        "name": "Amitabh Nag",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/nandan-nilekani/",
        "name": "Nandan Nilekani",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/feldmanandrew/",
        "name": "Andrew Feldman",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/tobiaslutke/",
        "name": "Tobi Lütke",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/patrickcollison/",
        "name": "Patrick Collison",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/satyanadella/",
        "name": "Satya Nadella",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/sundarpichai/",
        "name": "Sundar Pichai",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/stevenouri/",
        "name": "Steve Nouri",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/emollick/",
        "name": "Ethan Mollick",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/alliekmiller/",
        "name": "Allie K. Miller",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/pascalbornet/",
        "name": "Pascal Bornet",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/bernardmarr/",
        "name": "Bernard Marr",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/ronald-van-loon-597b38/",
        "name": "Ronald van Loon",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/kashyapkompella/",
        "name": "Kashyap Kompella",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/noellerussell/",
        "name": "Noelle Russell",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/andreaspwelsch/",
        "name": "Andreas Welsch",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/markvanrijmenam/",
        "name": "Mark van Rijmenam",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/lizasadams/",
        "name": "Lisa Adams",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/kateoneill/",
        "name": "Kate O'Neill",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/bentaylordata/",
        "name": "Ben Taylor",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/azeemazhar/",
        "name": "Azeem Azhar",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/nathanbenaich/",
        "name": "Nathan Benaich",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/matt-wolfe-ai/",
        "name": "Matt Wolfe",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/rowancheung/",
        "name": "Rowan Cheung",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/linusekenstam/",
        "name": "Linus Ekenstam",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/bentossell/",
        "name": "Ben Tossell",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/mattschlicht/",
        "name": "Matt Schlicht",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/ganeskesari/",
        "name": "Ganes Kesari",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/miteshk/",
        "name": "Mitesh Khapra",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/pratyush-kumar-b2b930b/",
        "name": "Pratyush Kumar",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/vijay-janapa-reddi-0857997/",
        "name": "Vijay Janapa Reddi",
        "category": "global",
        "tier": 2
    },
    {
        "url": "https://www.linkedin.com/in/rama-akkiraju-308119/",
        "name": "Rama Akkiraju",
        "category": "global",
        "tier": 2
    }
]

# Chinese Target Profiles & Hubs (Always Crawled if active)
CHINESE_PROFILES = [
    {
        "url": "https://cn.linkedin.com/in/kaifulee/",
        "name": "Kai-Fu Lee",
        "category": "chinese",
        "tier": 1
    },
    {
        "url": "https://www.linkedin.com/company/unitree/",
        "name": "Unitree Robotics",
        "category": "chinese",
        "tier": 1
    },
    {
        "url": "https://www.linkedin.com/company/ubtech-robotics/",
        "name": "UBTECH Robotics",
        "category": "chinese",
        "tier": 1
    },
    {
        "url": "https://www.linkedin.com/company/sensetime/",
        "name": "SenseTime",
        "category": "chinese",
        "tier": 1
    },
    {
        "url": "https://www.linkedin.com/company/megvii-technology/",
        "name": "Megvii Technology",
        "category": "chinese",
        "tier": 1
    }
]

# Search queries for discovery
GLOBAL_QUERIES = [
    'robotics "humanoid" -India -Bangalore -Bengaluru -Delhi -Mumbai -Pune -Chennai -Noida -Hyderabad -IIT -NIT -IISc',
    '"Boston Dynamics" OR "Figure AI" -India -Bangalore -Bengaluru -Delhi -Mumbai',
    'ROS2 "robot learning" -India -Bangalore -Bengaluru -Delhi -Mumbai -Pune -IIT -NIT',
    '"industrial automation" robotics -India -Bangalore -Bengaluru -Delhi -Mumbai -Pune -Chennai',
    '"AI agents" OR "autonomous systems" -India -Bangalore -Bengaluru -Delhi -Mumbai'
]

CHINESE_QUERIES = [
    '("Kai-Fu Lee" OR "01.AI" OR "Sinovation") -India',
    '("Robin Li" OR "Baidu" OR "Wang Haifeng") -India',
    '("Wang Xingxing" OR "Unitree" OR "Zhou Jian" OR "UBTECH") -India',
    '("He Xiaopeng" OR "XPENG Robotics" OR "Peng Zhihui" OR "AGIBOT") -India',
    '("Xu Li" OR "Tang Xiao\'ou" OR "SenseTime" OR "Yin Qi" OR "Megvii") -India',
    '("Yu Kai" OR "Horizon Robotics" OR "Tony Han" OR "WeRide" OR "James Peng" OR "Pony.ai") -India',
    '("Zhang Peng" OR "Zhipu AI" OR "Liang Wenfeng" OR "DeepSeek" OR "Yang Zhilin" OR "Moonshot AI") -India',
    '("Li Xiang" OR "Li Auto" OR "William Li" OR "NIO" OR "Zhou Hongyi" OR "360 Group") -India',
    '("Richard Liu" OR "JD.com" OR "Xu Zhijun" OR "Meng Wanzhou" OR "Huawei") -India',
    '("Dr. Leo Wang" OR "Geek+" OR "Nicolas Chee" OR "ForwardX" OR "Tiancheng Lou" OR "AUBO") -India'
]

# Heuristics for rule filters and domain matching
HEURISTIC_KEYWORDS = [
    'robot', 'humanoid', 'manipulation', 'embodied', 'vla', 'actuator', 'boston dynamics',
    'figure-01', 'figure-02', 'agility', 'digit', 'tesla optimus', 'neural network', 'llm',
    'spatial intelligence', 'world labs', 'physical ai', 'computer vision', 'slam', 'ros2',
    'nvidia', 'groq', 'deepseek', 'ai agent', 'autonomous vehicle', 'robotaxi', 'semiconductor'
]

BLACK_LIST_PHRASES = [
    'looking for a recruiter', 'we are hiring', 'join our team', 'job opening',
    'apply now', 'careers page', 'positions open'
]
