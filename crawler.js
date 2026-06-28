const { createClient } = require('@supabase/supabase-js');
const axios = require('axios');
const cheerio = require('cheerio');
const GoogleNewsDecoder = require('google-news-decoder');
require('dotenv').config();

const SUPABASE_URL = process.env.SUPABASE_URL || "https://jhsvvmpyybyoroxeevqh.supabase.co";
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impoc3Z2bXB5eWJ5b3JveGVldnFoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTc5MjQ4NSwiZXhwIjoyMDk3MzY4NDg1fQ.baEy5mto1xm_QDBZl1bwQ29kY2PmWgCN8k0N7R69p40";
const GROQ_API_KEY = process.env.GROQ_API_KEY;

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

const FEEDS = [
    { name: "Google News", url: "https://news.google.com/rss/search?q=humanoid+robotics&hl=en-US&gl=US&ceid=US:en", category: "global" },
    { name: "IEEE Spectrum", url: "https://spectrum.ieee.org/feeds/robotics.rss", category: "global" },
    { name: "TechCrunch", url: "https://techcrunch.com/category/robotics/feed/", category: "global" }
];

const HEURISTIC_KEYWORDS = [
    'robot', 'humanoid', 'manipulation', 'embodied', 'vla', 'actuator', 'boston dynamics',
    'figure-01', 'figure-02', 'agility', 'digit', 'tesla optimus', 'neural network', 'llm',
    'spatial intelligence', 'world labs', 'physical ai', 'computer vision', 'slam', 'ros2',
    'nvidia', 'groq', 'deepseek', 'ai agent', 'autonomous vehicle', 'robotaxi', 'semiconductor'
];

function getDomain(urlStr) {
    try {
        const parsed = new URL(urlStr);
        return parsed.hostname.replace('www.', '');
    } catch (e) {
        return 'News Feed';
    }
}

async function fetchRSS(feed) {
    console.log(`[*] Fetching RSS feed: ${feed.name} (${feed.url})`);
    try {
        const response = await axios.get(feed.url, { timeout: 10000 });
        const $ = cheerio.load(response.data, { xmlMode: true });
        const items = [];
        $('item').each((i, el) => {
            const title = $(el).find('title').text();
            let link = $(el).find('link').text() || $(el).find('guid').text();
            const pubDate = $(el).find('pubDate').text();
            link = link.trim();
            if (link && title) {
                items.push({ title, link, pubDate, category: feed.category });
            }
        });
        return items;
    } catch (error) {
        console.error(`[!] Error fetching feed ${feed.name}: ${error.message}`);
        return [];
    }
}

async function extractArticleText(url) {
    console.log(`[*] Extracting body text from: ${url}`);
    try {
        const response = await axios.get(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
            timeout: 15000
        });
        
        // Strip out scripts, styles, and iframe blocks using regex to drastically reduce memory usage before parsing
        let cleanHtml = response.data
            .replace(/<script[\s\S]*?<\/script>/gi, '')
            .replace(/<style[\s\S]*?<\/style>/gi, '')
            .replace(/<noscript[\s\S]*?<\/noscript>/gi, '')
            .replace(/<iframe[\s\S]*?<\/iframe>/gi, '');
            
        const bodyMatch = cleanHtml.match(/<body[\s\S]*<\/body>/i);
        if (bodyMatch) {
            cleanHtml = bodyMatch[0];
        }

        const $ = cheerio.load(cleanHtml);
        
        $('header, footer, nav').remove();
        
        let textParts = [];
        const bodyContainers = $('article, .article-content, .post-content, .entry-content, main');
        const target = bodyContainers.length > 0 ? bodyContainers : $('body');
        
        target.find('p').each((i, el) => {
            const pText = $(el).text().trim();
            if (pText.length > 20) {
                textParts.push(pText);
            }
        });
        
        const text = textParts.join('\n');
        return text.substring(0, 10000);
    } catch (error) {
        console.error(`[!] Failed to extract text from ${url}: ${error.message}`);
        return '';
    }
}

async function evaluateArticle(title, text, category, groqKey) {
    if (!groqKey) {
        console.warn("[!] GROQ_API_KEY not configured. Skipping AI evaluation.");
        return null;
    }
    
    const prompt = `
You are an expert evaluator for a high-value global AI and Robotics Intelligence Platform.
Analyze the following news article (Title: "${title}", Category: ${category}) and rate it against our quality parameters.
Each metric score MUST be an integer between 0 and 10.

Quality Matrix:
1. Novelty: Is it presenting a new breakthrough, project, code, or perspective?
2. Virality: Does it have strong engagement signals or potential for high reach?
3. Technical Depth: Does it contain implementation details, code links, metrics, or architectural concepts?
4. AI Relevance: Is it directly relevant to Artificial Intelligence, LLMs, or agents?
5. Robotics Relevance: Is it directly relevant to physical/embodied robotics or humanoid control?
6. China Relevance: For Chinese ecosystem articles, is it highlighting breakthroughs or key developments in the Chinese AI/robotics landscape?
7. Founder Signal: Is it written by or directly discussing a high-signal founder or CEO?
8. Research Signal: Does it discuss academic papers, researchers, labs, or training methodologies?

Write a professional, detailed summary/insight (1-3 sentences) in the persona of an expert Robotics Engineer and Startup Founder only if the total score is 65 or higher. The comment should validate the article, add a deep technical insight or contrarian perspective, and end with an open-ended question. If the total score is less than 65, leave the comment blank.

You MUST respond in strict JSON format. Do not write any conversational text.

Response Schema:
{
    "total_score": <integer 0-100 indicating overall platform value>,
    "novelty": <0-10>,
    "virality": <0-10>,
    "technical_depth": <0-10>,
    "ai_relevance": <0-10>,
    "robotics_relevance": <0-10>,
    "china_relevance": <0-10>,
    "founder_signal": <0-10>,
    "research_signal": <0-10>,
    "reasoning": "<short description explaining score>",
    "comment": "<comment or empty string>"
}

Article Content:
${text.substring(0, 4000)}
`;

    const maxRetries = 5;
    let backoff = 2;
    for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
            const response = await axios.post("https://api.groq.com/openai/v1/chat/completions", {
                messages: [{ role: "user", content: prompt }],
                model: "llama-3.3-70b-versatile",
                response_format: { type: "json_object" },
                max_tokens: 350,
                temperature: 0.2
            }, {
                headers: {
                    "Authorization": `Bearer ${groqKey}`,
                    "Content-Type": "application/json"
                },
                timeout: 20000
            });
            
            const resultText = response.data.choices[0].message.content;
            return JSON.parse(resultText);
        } catch (error) {
            console.warn(`[!] Groq call failed on attempt ${attempt + 1}: ${error.message}`);
            if (error.response && error.response.status === 429) {
                const retryAfter = 5;
                console.log(`[!] Groq 429 Rate Limit hit. Retrying in ${retryAfter} seconds...`);
                await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
            } else {
                await new Promise(resolve => setTimeout(resolve, backoff * 1000));
                backoff *= 2;
            }
        }
    }
    return null;
}

async function run() {
    const startTime = new Date();
    
    // 1. Initialize Crawl Run in Supabase
    const { data: runData, error: runError } = await supabase
        .from('crawl_runs')
        .insert({ status: 'running' })
        .select('id')
        .single();
        
    if (runError) {
        console.error("[!] Failed to log run initialization:", runError);
        return;
    }
    const runId = runData.id;
    console.log(`[*] Started Crawl Run ID: ${runId}`);
    
    let postsDiscovered = 0;
    let postsExtracted = 0;
    let postsScored = 0;
    let errorMessage = null;
    
    try {
        // 2. Fetch all feeds
        let candidates = [];
        for (const feed of FEEDS) {
            const items = await fetchRSS(feed);
            candidates = candidates.concat(items);
        }
        
        postsDiscovered = candidates.length;
        console.log(`[*] Discovered ${postsDiscovered} total articles across feeds.`);
        
        // 3. Deduplicate against Supabase crawl_history
        const { data: historyData, error: histError } = await supabase
            .from('crawl_history')
            .select('url');
            
        if (histError) throw histError;
        const historySet = new Set((historyData || []).map(h => h.url));
        
        const newArticles = candidates.filter(item => !historySet.has(item.link));
        console.log(`[*] ${newArticles.length} articles are new and require processing.`);
        
        // Limit processing to 15 articles to avoid API limits and keep GHA fast
        const articlesToProcess = newArticles.slice(0, 15);
        
        // Fetch all profiles from Supabase to resolve authorship
        const { data: profiles, error: profError } = await supabase
            .from('profiles')
            .select('id, url');
        if (profError) throw profError;
        
        // Find max profile ID to avoid sequence issues
        const { data: maxProfileData, error: maxProfileErr } = await supabase
            .from('profiles')
            .select('id')
            .order('id', { ascending: false })
            .limit(1);
        let nextProfileId = 1;
        if (!maxProfileErr && maxProfileData && maxProfileData.length > 0) {
            nextProfileId = maxProfileData[0].id + 1;
        }

        // Find max post ID to avoid sequence issues
        const { data: maxPostData, error: maxPostErr } = await supabase
            .from('posts')
            .select('id')
            .order('id', { ascending: false })
            .limit(1);
        let nextPostId = 1;
        if (!maxPostErr && maxPostData && maxPostData.length > 0) {
            nextPostId = maxPostData[0].id + 1;
        }
        
        for (const article of articlesToProcess) {
            let targetUrl = article.link;
            const decoderInstance = new GoogleNewsDecoder();
            
            if (targetUrl.includes('news.google.com')) {
                console.log(`[*] Google News link detected, decoding: ${targetUrl}`);
                try {
                    const decoded = await decoderInstance.decodeGoogleNewsUrl(targetUrl);
                    if (decoded.status && decoded.decodedUrl) {
                        targetUrl = decoded.decodedUrl;
                        console.log(`[*] Decoded successfully to: ${targetUrl}`);
                    } else {
                        console.warn(`[!] Failed to decode Google News URL: ${decoded.message}`);
                    }
                } catch (err) {
                    console.error(`[!] Error decoding Google News URL: ${err.message}`);
                }
            }
            
            const domain = getDomain(targetUrl);
            
            // Resolve or create profile for source
            let profile = profiles.find(p => p.url.includes(domain));
            let profileId = profile ? profile.id : null;
            
            if (!profileId) {
                const sourceName = domain.split('.')[0].toUpperCase();
                const { data: newProfile, error: newProfErr } = await supabase
                    .from('profiles')
                    .insert({
                        id: nextProfileId,
                        url: `https://${domain}`,
                        name: sourceName,
                        category: article.category,
                        tier: 2
                    })
                    .select('id')
                    .single();
                if (!newProfErr && newProfile) {
                    profileId = newProfile.id;
                    profiles.push({ id: profileId, url: `https://${domain}` });
                    nextProfileId++;
                } else {
                    console.error(`[!] Failed to create profile for ${domain}:`, newProfErr);
                }
            }
            
            // 4. Extract Text Content
            const text = await extractArticleText(targetUrl);
            if (text.length < 150) {
                console.log(`[!] Article text too short (${text.length} chars). Skipping.`);
                continue;
            }
            
            // Check heuristic keywords
            const textLower = text.toLowerCase();
            const hasKeyword = HEURISTIC_KEYWORDS.some(kw => textLower.includes(kw));
            if (!hasKeyword) {
                console.log(`[!] Article does not match heuristic keywords. Skipping.`);
                continue;
            }
            
            postsExtracted++;
            
            // Save to posts table
            const { data: insertedPost, error: postErr } = await supabase
                .from('posts')
                .insert({
                    id: nextPostId,
                    url: targetUrl,
                    profile_id: profileId,
                    post_text: text.substring(0, 3000),
                    likes: 0,
                    comments: 0,
                    published_date: article.pubDate || new Date().toISOString(),
                    category: article.category,
                    status: 'extracted'
                })
                .select('id')
                .single();
                
            if (postErr) {
                console.error(`[!] Failed to save post ${targetUrl}:`, postErr);
                continue;
            }
            nextPostId++;
            
            // Save to crawl_history
            await supabase
                .from('crawl_history')
                .insert({ url: article.link, processed: true });
                
            // 5. Evaluate and Score via Groq
            if (GROQ_API_KEY) {
                console.log(`[*] Evaluating post via Groq: ${article.link}`);
                const scoreData = await evaluateArticle(article.title, text, article.category, GROQ_API_KEY);
                
                if (scoreData) {
                    // Save scores
                    const { error: scoreErr } = await supabase
                        .from('scores')
                        .insert({
                            post_id: insertedPost.id,
                            total_score: scoreData.total_score,
                            novelty: scoreData.novelty,
                            virality: scoreData.virality,
                            technical_depth: scoreData.technical_depth,
                            ai_relevance: scoreData.ai_relevance,
                            robotics_relevance: scoreData.robotics_relevance,
                            china_relevance: scoreData.china_relevance,
                            founder_signal: scoreData.founder_signal,
                            research_signal: scoreData.research_signal,
                            reasoning: scoreData.reasoning
                        });
                        
                    if (scoreErr) {
                        console.error(`[!] Failed to save scores for post_id ${insertedPost.id}:`, scoreErr);
                    } else {
                        postsScored++;
                        // Update status to scored
                        await supabase
                            .from('posts')
                            .update({ status: 'scored' })
                            .eq('id', insertedPost.id);
                    }
                    
                    // Save generated summaries/comments
                    if (scoreData.comment && scoreData.total_score >= 65) {
                        await supabase
                            .from('generated_comments')
                            .insert({
                                post_id: insertedPost.id,
                                comment_text: scoreData.comment
                            });
                    }
                }
            }
        }
    } catch (e) {
        errorMessage = e.message;
        console.error("[!] Scraper Error occurred:", e);
    } finally {
        const endTime = new Date();
        const durationMs = endTime.getTime() - startTime.getTime();
        const status = errorMessage ? 'failed' : 'success';
        
        await supabase
            .from('crawl_runs')
            .update({
                status,
                end_time: endTime.toISOString(),
                duration_ms: durationMs,
                posts_discovered: postsDiscovered,
                posts_extracted: postsExtracted,
                posts_scored: postsScored,
                error_message: errorMessage
            })
            .eq('id', runId);
            
        console.log(`[*] Finished Crawl Run ID: ${runId}. Status: ${status} in ${durationMs / 1000}s`);
        
        if (errorMessage) {
            process.exit(1);
        }
    }
}

run();
