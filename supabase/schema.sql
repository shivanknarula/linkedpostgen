-- 1. Profiles Table
CREATE TABLE IF NOT EXISTS profiles (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    category TEXT CHECK(category IN ('global', 'chinese')) NOT NULL,
    tier INTEGER CHECK(tier IN (1, 2)) NOT NULL DEFAULT 2,
    last_crawled_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- 2. Crawl History Cache
CREATE TABLE IF NOT EXISTS crawl_history (
    url TEXT PRIMARY KEY,
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE
);

-- 3. Posts Table
CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    profile_id INTEGER REFERENCES profiles(id),
    post_text TEXT NOT NULL,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    published_date TEXT,
    category TEXT CHECK(category IN ('global', 'chinese')) NOT NULL,
    status TEXT CHECK(status IN ('discovered', 'extracted', 'filtered', 'scored')) NOT NULL DEFAULT 'discovered',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Quality Scores Table
CREATE TABLE IF NOT EXISTS scores (
    post_id INTEGER PRIMARY KEY REFERENCES posts(id) ON DELETE CASCADE,
    total_score INTEGER NOT NULL,
    novelty INTEGER NOT NULL,
    virality INTEGER NOT NULL,
    technical_depth INTEGER NOT NULL,
    ai_relevance INTEGER NOT NULL,
    robotics_relevance INTEGER NOT NULL,
    china_relevance INTEGER NOT NULL,
    founder_signal INTEGER NOT NULL,
    research_signal INTEGER NOT NULL,
    reasoning TEXT,
    evaluated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. AI Generated Comments Table
CREATE TABLE IF NOT EXISTS generated_comments (
    post_id INTEGER PRIMARY KEY REFERENCES posts(id) ON DELETE CASCADE,
    comment_text TEXT NOT NULL,
    approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Crawl Runs Table (Observability)
CREATE TABLE IF NOT EXISTS crawl_runs (
    id SERIAL PRIMARY KEY,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    status TEXT CHECK(status IN ('running', 'success', 'failed')) NOT NULL,
    posts_discovered INTEGER DEFAULT 0,
    posts_extracted INTEGER DEFAULT 0,
    posts_scored INTEGER DEFAULT 0,
    error_message TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);
CREATE INDEX IF NOT EXISTS idx_scores_total_score ON scores(total_score);
CREATE INDEX IF NOT EXISTS idx_profiles_tier ON profiles(tier);
CREATE INDEX IF NOT EXISTS idx_crawl_history_processed ON crawl_history(processed);

-- Seed Tier 1 and Tier 2 Target Profiles
INSERT INTO profiles (url, name, category, tier, is_active)
VALUES
    -- Tier 1 Global Pioneers (Always Crawled)
    ('https://www.linkedin.com/in/brettadcock/', 'Brett Adcock', 'global', 1, TRUE),
    ('https://www.linkedin.com/in/yann-lecun/', 'Yann LeCun', 'global', 1, TRUE),
    ('https://www.linkedin.com/in/andrewng/', 'Andrew Ng', 'global', 1, TRUE),
    ('https://www.linkedin.com/in/fei-fei-li-66779313/', 'Fei-Fei Li', 'global', 1, TRUE),
    ('https://www.linkedin.com/in/gdbrockman/', 'Greg Brockman', 'global', 1, TRUE),
    ('https://www.linkedin.com/in/linxi-fan-7a242a37/', 'Linxi (Jim) Fan', 'global', 1, TRUE),
    ('https://www.linkedin.com/in/andrej-karpathy-a3a89a19/', 'Andrej Karpathy', 'global', 1, TRUE),
    ('https://www.linkedin.com/in/mustafa-suleyman/', 'Mustafa Suleyman', 'global', 1, TRUE),
    ('https://www.linkedin.com/company/boston-dynamics/', 'Boston Dynamics (Company)', 'global', 1, TRUE),
    ('https://www.linkedin.com/company/figure-ai/', 'Figure AI (Company)', 'global', 1, TRUE),
    
    -- Tier 1 Chinese Pioneers
    ('https://cn.linkedin.com/in/kaifulee/', 'Kai-Fu Lee', 'chinese', 1, TRUE),
    ('https://www.linkedin.com/company/unitree/', 'Unitree Robotics', 'chinese', 1, TRUE),
    ('https://www.linkedin.com/company/ubtech-robotics/', 'UBTECH Robotics', 'chinese', 1, TRUE),
    ('https://www.linkedin.com/company/sensetime/', 'SenseTime', 'chinese', 1, TRUE),
    ('https://www.linkedin.com/company/megvii-technology/', 'Megvii Technology', 'chinese', 1, TRUE),

    -- Tier 2 Global Rotating Pool
    ('https://www.linkedin.com/company/agility-robotics/', 'Agility Robotics', 'global', 2, TRUE),
    ('https://www.linkedin.com/company/apptronik/', 'Apptronik', 'global', 2, TRUE),
    ('https://www.linkedin.com/company/1x-technologies/', '1X Technologies', 'global', 2, TRUE),
    ('https://www.linkedin.com/company/sanctuary-ai/', 'Sanctuary AI', 'global', 2, TRUE),
    ('https://www.linkedin.com/company/physical-intelligence/', 'Physical Intelligence', 'global', 2, TRUE),
    ('https://www.linkedin.com/company/collaborative-robotics/', 'Collaborative Robotics', 'global', 2, TRUE),
    ('https://www.linkedin.com/company/skild-ai/', 'Skild AI', 'global', 2, TRUE),
    ('https://www.linkedin.com/company/covariant-ai/', 'Covariant AI', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/anima-anandkumar-b413008/', 'Anima Anandkumar', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/thrun/', 'Sebastian Thrun', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/jeff-dean-5056/', 'Jeff Dean', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/j%C3%BCrgen-schmidhuber-441634b/', 'Jürgen Schmidhuber', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/ruslan-salakhutdinov-9069a5b/', 'Ruslan Salakhutdinov', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/christopher-manning-02b488b/', 'Christopher Manning', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/kozyrkov/', 'Cassie Kozyrkov', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/aidangomez/', 'Aidan Gomez', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/noam-shazeer-464879/', 'Noam Shazeer', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/socher/', 'Richard Socher', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/daphne-koller-17215/', 'Daphne Koller', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/percy-liang-22a846b/', 'Percy Liang', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/joelle-pineau-1b07297/', 'Joelle Pineau', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/raquel-urtasun-995775b/', 'Raquel Urtasun', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/david-silver-8bb84b/', 'David Silver', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/oriolvinyals/', 'Oriol Vinyals', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/dario-amodei-3a216a4/', 'Dario Amodei', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/geordierose/', 'Geordie Rose', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/meloneewise/', 'Melonee Wise', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/chris-anderson-8958221/', 'Chris Anderson', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/berntbornich/', 'Bernt Børnich', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/jonathan-hurst-385a49b/', 'Jonathan Hurst', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/pathakdeepak/', 'Deepak Pathak', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/sangbae-kim-1122a27/', 'Sangbae Kim', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/rodney-brooks-11488b3/', 'Rodney Brooks', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/gill-pratt-58a478b/', 'Gill Pratt', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/raulbravo/', 'Raul Bravo', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/daniela-rus-637996/', 'Daniela Rus', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/ken-goldberg-8bb657/', 'Ken Goldberg', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/aaron-saunders-b84492/', 'Aaron Saunders', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/jameskuffner/', 'James Kuffner', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/prasv/', 'Pras Velagapudi', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/ayanna-howard/', 'Ayanna Howard', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/raffaello-d-andrea-a745771/', 'Raffaello D''Andrea', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/russ-tedrake-0a4a625/', 'Russ Tedrake', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/drdavidhanson/', 'Dr. David Hanson', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/dennis-hong-b6a6042b/', 'Dennis Hong', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/aude-billard-a447814/', 'Aude Billard', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/sanjivsingh/', 'Sanjiv Singh', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/robplayter/', 'Rob Playter', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/rene-haas-5883261/', 'Rene Haas', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/clementdelangue/', 'Clement Delangue', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/lexfridman/', 'Lex Fridman', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/reidhoffman/', 'Reid Hoffman', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/alexandrwang/', 'Alexandr Wang', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/aravind-srinivas/', 'Aravind Srinivas', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/emadmostaque/', 'Emad Mostaque', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/thomasdohmke/', 'Thomas Dohmke', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/alighodsi/', 'Ali Ghodsi', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/dharmesh/', 'Dharmesh Shah', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/aaronlevie/', 'Aaron Levie', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/tomasztunguz/', 'Tomasz Tunguz', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/vinodkhosla/', 'Vinod Khosla', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/billgross/', 'Bill Gross', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/amitabh-nag-a5b678/', 'Amitabh Nag', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/nandan-nilekani/', 'Nandan Nilekani', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/feldmanandrew/', 'Andrew Feldman', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/tobiaslutke/', 'Tobi Lütke', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/patrickcollison/', 'Patrick Collison', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/satyanadella/', 'Satya Nadella', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/sundarpichai/', 'Sundar Pichai', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/stevenouri/', 'Steve Nouri', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/emollick/', 'Ethan Mollick', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/alliekmiller/', 'Allie K. Miller', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/pascalbornet/', 'Pascal Bornet', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/bernardmarr/', 'Bernard Marr', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/ronald-van-loon-597b38/', 'Ronald van Loon', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/kashyapkompella/', 'Kashyap Kompella', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/noellerussell/', 'Noelle Russell', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/andreaspwelsch/', 'Andreas Welsch', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/markvanrijmenam/', 'Mark van Rijmenam', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/lizasadams/', 'Lisa Adams', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/kateoneill/', 'Kate O''Neill', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/bentaylordata/', 'Ben Taylor', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/azeemazhar/', 'Azeem Azhar', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/nathanbenaich/', 'Nathan Benaich', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/matt-wolfe-ai/', 'Matt Wolfe', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/rowancheung/', 'Rowan Cheung', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/linusekenstam/', 'Linus Ekenstam', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/bentossell/', 'Ben Tossell', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/mattschlicht/', 'Matt Schlicht', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/ganeskesari/', 'Ganes Kesari', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/miteshk/', 'Mitesh Khapra', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/pratyush-kumar-b2b930b/', 'Pratyush Kumar', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/vijay-janapa-reddi-0857997/', 'Vijay Janapa Reddi', 'global', 2, TRUE),
    ('https://www.linkedin.com/in/rama-akkiraju-308119/', 'Rama Akkiraju', 'global', 2, TRUE)
ON CONFLICT (url) DO NOTHING;
