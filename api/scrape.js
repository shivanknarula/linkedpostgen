import { createClient } from '@supabase/supabase-js';

export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method Not Allowed' });
    }

    const supabaseUrl = process.env.SUPABASE_URL;
    const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY;

    if (!supabaseUrl || !supabaseKey) {
        return res.status(500).json({ 
            error: 'Missing required Supabase configurations (SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY) on Vercel Environment Variables.' 
        });
    }

    try {
        const functionUrl = `${supabaseUrl.replace(/\/$/, '')}/functions/v1/linkedin-agent`;
        
        // Fire-and-forget call to the Supabase Edge Function.
        // We do not wait for the response because the scraper run can take up to 2-3 minutes,
        // which exceeds Vercel's free serverless function timeout of 10 seconds.
        fetch(functionUrl, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${supabaseKey}`,
                'Content-Type': 'application/json'
            }
        }).catch(err => {
            console.error("Async trigger of Supabase Edge Function failed:", err);
        });

        return res.status(200).json({ 
            status: 'success', 
            message: 'LinkedIn Agent scraping run successfully triggered in Supabase Edge Functions!' 
        });

    } catch (error) {
        console.error(error);
        return res.status(500).json({ 
            status: 'error', 
            message: error.message 
        });
    }
}
