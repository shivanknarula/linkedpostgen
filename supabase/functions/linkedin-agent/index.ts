import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.0";

const HEURISTIC_KEYWORDS = [
  'robot', 'humanoid', 'manipulation', 'embodied', 'vla', 'actuator', 'boston dynamics',
  'figure-01', 'figure-02', 'agility', 'digit', 'tesla optimus', 'neural network', 'llm',
  'spatial intelligence', 'world labs', 'physical ai', 'computer vision', 'slam', 'ros2',
  'nvidia', 'groq', 'deepseek', 'ai agent', 'autonomous vehicle', 'robotaxi', 'semiconductor'
];

const BLACK_LIST_PHRASES = [
  'looking for a recruiter', 'we are hiring', 'join our team', 'job opening',
  'apply now', 'careers page', 'positions open'
];

interface Profile {
  id: number;
  url: string;
  category: 'global' | 'chinese';
  tier: number;
}

interface ScrapedPost {
  url: string;
  profile_url?: string;
  text: string;
  likes: number;
  comments: number;
  date: string;
  category: 'global' | 'chinese';
}

serve(async (req) => {
  // Handle CORS
  if (req.method === 'OPTIONS') {
    return new Response('ok', {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
      }
    });
  }

  const startCrawlTime = new Date();
  
  // Initialize Supabase Client
  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const supabaseServiceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const supabase = createClient(supabaseUrl, supabaseServiceRoleKey);

  let runId: number | null = null;
  let postsDiscovered = 0;
  let postsExtracted = 0;
  let postsScored = 0;

  try {
    // 1. Log Start of Run
    const { data: runData, error: runError } = await supabase
      .from('crawl_runs')
      .insert({ status: 'running' })
      .select('id')
      .single();

    if (runError) throw runError;
    runId = runData.id;

    console.log(`[*] Started Crawl Run ID: ${runId}`);

    // 2. Fetch active profiles
    // Tier 1 always
    const { data: tier1Profiles, error: t1Err } = await supabase
      .from('profiles')
      .select('id, url, category, tier')
      .eq('tier', 1)
      .eq('is_active', true);
    if (t1Err) throw t1Err;

    // Tier 2 rotating (random 12)
    const { data: allTier2Profiles, error: t2Err } = await supabase
      .from('profiles')
      .select('id, url, category, tier')
      .eq('tier', 2)
      .eq('is_active', true);
    if (t2Err) throw t2Err;

    // Shuffle and pick 12
    const shuffledTier2 = (allTier2Profiles || []).sort(() => 0.5 - Math.random());
    const selectedTier2 = shuffledTier2.slice(0, Math.min(shuffledTier2.length, 12));
    
    const targetProfiles: Profile[] = [...(tier1Profiles || []), ...selectedTier2];
    console.log(`[*] Target profiles count: ${targetProfiles.length}`);

    if (targetProfiles.length === 0) {
      throw new Error("No active profiles to crawl.");
    }

    // 3. Trigger Scraping (Apify or ScrapingBee configuration)
    // For Option B, we default to Apify LinkedIn Post Scraper or a general scraper proxy api.
    const apifyToken = Deno.env.get("APIFY_API_KEY");
    const scrapingBeeKey = Deno.env.get("SCRAPINGBEE_API_KEY");

    let scrapedPosts: ScrapedPost[] = [];

    if (apifyToken) {
      console.log("[*] Using Apify LinkedIn Scraper Integration...");
      // Trigger Apify actor (apify/linkedin-post-scraper or similar)
      // We pass the profile URLs
      const profileUrls = targetProfiles.map(p => p.url);
      
      const actorRunResponse = await fetch(`https://api.apify.com/v2/acts/apify~linkedin-post-scraper/run-sync?token=${apifyToken}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          urls: profileUrls,
          limitPerProfile: 5,
          deepScrape: false
        })
      });

      if (!actorRunResponse.ok) {
        const errText = await actorRunResponse.text();
        throw new Error(`Apify Run failed: ${errText}`);
      }

      const runResults = await actorRunResponse.json();
      const datasetId = runResults.data.defaultDatasetId;

      // Fetch the dataset
      const datasetResponse = await fetch(`https://api.apify.com/v2/datasets/${datasetId}/items?token=${apifyToken}`);
      const datasetItems = await datasetResponse.json();

      for (const item of datasetItems) {
        const text = item.text || item.postText || "";
        const postUrl = item.url || item.postUrl || "";
        const profileUrl = item.profileUrl || "";
        const profile = targetProfiles.find(p => p.url === profileUrl);
        const category = profile ? profile.category : 'global';

        if (postUrl && text) {
          scrapedPosts.push({
            url: postUrl,
            profile_url: profileUrl,
            text: text,
            likes: item.likesCount || item.likes || 0,
            comments: item.commentsCount || item.comments || 0,
            date: item.postedAt || item.date || new Date().toISOString(),
            category: category
          });
        }
      }
    } else if (scrapingBeeKey) {
      console.log("[*] Using ScrapingBee Scraping Proxy...");
      // Fetch each profile page and extract links / details (mocked or custom parsing)
      // For ScrapingBee, we scrape the LinkedIn pages directly using CSS selectors
      // Due to the complexity of parsing LinkedIn HTML on-the-fly, Apify is heavily recommended.
      // Below is a general proxy template structure:
      throw new Error("ScrapingBee parser not implemented. Please configure APIFY_API_KEY for robust scraping.");
    } else {
      console.log("[*] No Scraping API Keys found. Running demo/mock mode...");
      // Return some seed mock posts for testing
      scrapedPosts = [
        {
          url: "https://www.linkedin.com/posts/brettadcock_figure-02-humanoid-robotics-activity-1234567890",
          profile_url: "https://www.linkedin.com/in/brettadcock/",
          text: "We just launched Figure 02, the world's most advanced humanoid robot. It features spatial intelligence, deep neural network control, and custom actuators. The hardware is beautiful, and the software runs fully end-to-end on neural net policies.",
          likes: 3450,
          comments: 280,
          date: new Date().toISOString(),
          category: 'global'
        },
        {
          url: "https://www.linkedin.com/posts/yann-lecun_world-models-ai-activity-2345678901",
          profile_url: "https://www.linkedin.com/in/yann-lecun/",
          text: "Autoregressive LLMs cannot achieve human-level intelligence. We need world models, self-supervised learning, and joint-embedding predictive architectures (JEPA). True AI agent control requires planning in representation space, not just token generation.",
          likes: 2150,
          comments: 190,
          date: new Date().toISOString(),
          category: 'global'
        }
      ];
    }

    postsDiscovered = scrapedPosts.length;
    console.log(`[*] Discovered ${postsDiscovered} candidate posts.`);

    // 4. Load crawl history for deduplication
    const { data: historyData, error: histErr } = await supabase
      .from('crawl_history')
      .select('url');
    if (histErr) throw histErr;

    const historySet = new Set((historyData || []).map(h => h.url));

    // Filter posts
    const newPosts = scrapedPosts.filter(p => !historySet.has(p.url));
    console.log(`[*] ${newPosts.length} posts are new and require scoring.`);

    const groqKey = Deno.env.get("GROQ_API_KEY");
    if (!groqKey) {
      console.warn("[!] GROQ_API_KEY is not configured. Saving posts unscored.");
    }

    // 5. Evaluate and Score each post
    for (const post of newPosts) {
      // Stage 1 filter: length and blacklist
      if (post.text.length < 70) continue;
      const textLower = post.text.toLowerCase();
      if (BLACK_LIST_PHRASES.some(phrase => textLower.includes(phrase))) continue;

      // Stage 2 filter: heuristic keywords
      if (!HEURISTIC_KEYWORDS.some(kw => textLower.includes(kw))) continue;

      postsExtracted++;

      // Insert post into `posts` table
      const profile = targetProfiles.find(p => p.url === post.profile_url);
      const { data: insertedPost, error: postErr } = await supabase
        .from('posts')
        .insert({
          url: post.url,
          profile_id: profile ? profile.id : null,
          post_text: post.text,
          likes: post.likes,
          comments: post.comments,
          published_date: post.date,
          category: post.category,
          status: 'extracted'
        })
        .select('id')
        .single();

      if (postErr) {
        console.error(`[!] Failed to insert post ${post.url}:`, postErr);
        continue;
      }

      // Add to crawl_history
      await supabase
        .from('crawl_history')
        .insert({ url: post.url, processed: true });

      // Stage 3: LLM Scoring
      if (groqKey && insertedPost) {
        console.log(`[*] Scoring post: ${post.url}`);
        const scoreData = await getGroqScore(post.text, post.category, groqKey);
        
        if (scoreData) {
          // Save score
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
            // Update post status to 'scored'
            await supabase
              .from('posts')
              .update({ status: 'scored' })
              .eq('id', insertedPost.id);
          }

          // Save comment if generated and approved threshold met (total_score >= 65)
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

    // 6. Complete Crawl Run Log
    const endCrawlTime = new Date();
    const durationMs = endCrawlTime.getTime() - startCrawlTime.getTime();

    await supabase
      .from('crawl_runs')
      .update({
        status: 'success',
        end_time: endCrawlTime.toISOString(),
        duration_ms: durationMs,
        posts_discovered: postsDiscovered,
        posts_extracted: postsExtracted,
        posts_scored: postsScored
      })
      .eq('id', runId);

    return new Response(JSON.stringify({
      status: 'success',
      run_id: runId,
      posts_discovered: postsDiscovered,
      posts_extracted: postsExtracted,
      posts_scored: postsScored,
      duration_ms: durationMs
    }), {
      headers: { 'Content-Type': 'application/json' },
      status: 200
    });

  } catch (error: any) {
    console.error("[!] Pipeline Execution Failed:", error);
    
    if (runId !== null) {
      const endCrawlTime = new Date();
      const durationMs = endCrawlTime.getTime() - startCrawlTime.getTime();
      await supabase
        .from('crawl_runs')
        .update({
          status: 'failed',
          end_time: endCrawlTime.toISOString(),
          duration_ms: durationMs,
          error_message: error.message
        })
        .eq('id', runId);
    }

    return new Response(JSON.stringify({
      status: 'error',
      message: error.message
    }), {
      headers: { 'Content-Type': 'application/json' },
      status: 500
    });
  }
});

async function getGroqScore(postText: string, category: string, groqKey: string) {
  const prompt = `
  You are an expert evaluator for a high-value global AI and Robotics Intelligence Platform.
  Analyze the following LinkedIn post (Category: ${category}) and rate it against our quality parameters.
  Each metric score MUST be an integer between 0 and 10.
  
  Quality Matrix:
  1. Novelty: Is it presenting a new breakthrough, project, code, or perspective?
  2. Virality: Does it have strong engagement signals or potential for high reach?
  3. Technical Depth: Does it contain implementation details, code links, metrics, or architectural concepts?
  4. AI Relevance: Is it directly relevant to Artificial Intelligence, LLMs, or agents?
  5. Robotics Relevance: Is it directly relevant to physical/embodied robotics or humanoid control?
  6. China Relevance: For Chinese posts, is it highlighting breakthroughs or key developments in the Chinese AI ecosystem?
  7. Founder Signal: Is it written by or directly discussing a high-signal founder or CEO?
  8. Research Signal: Does it discuss academic papers, researchers, labs, or training methodologies?

  Write a professional, detailed comment (1-3 sentences) in the persona of an expert Robotics Engineer and Startup Founder only if the total score is 65 or higher. The comment should validate the poster, add a deep technical insight or contrarian perspective, and end with an open-ended question. If the total score is less than 65, leave the comment blank.

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

  Post text:
  ${postText.substring(0, 3000)}
  `;

  try {
    const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${groqKey}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        messages: [{ role: "user", content: prompt }],
        model: "llama-3.3-70b-versatile",
        response_format: { type: "json_object" },
        max_tokens: 350,
        temperature: 0.2
      })
    });

    if (!response.ok) {
      const errText = await response.text();
      console.error(`[!] Groq API request failed: ${errText}`);
      return null;
    }

    const resJson = await response.json();
    const rawJson = resJson.choices[0].message.content.trim();
    return JSON.parse(rawJson);
  } catch (e) {
    console.error("[!] Error in getGroqScore:", e);
    return null;
  }
}
