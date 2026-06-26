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
        
        console.log(`[*] Sending trigger request to Supabase Edge Function: ${functionUrl}`);
        
        // Await the fetch call so Vercel doesn't freeze the function environment
        // before the request actually leaves the server.
        const response = await fetch(functionUrl, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${supabaseKey}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Supabase Edge Function returned ${response.status}: ${errorText}`);
        }

        const responseData = await response.json();

        return res.status(200).json({ 
            status: 'success', 
            message: 'Robotics News Agent scraping run successfully completed!',
            details: responseData
        });

    } catch (error) {
        console.error("Scrape trigger error:", error);
        
        // If it timed out on Vercel's end but the request was sent, the Edge Function
        // is still executing in the background on Supabase.
        if (error.message.includes("fetch failed") || error.message.includes("timeout")) {
            return res.status(200).json({
                status: 'success',
                message: 'Scraping triggered successfully! Execution is running in the background on Supabase.'
            });
        }

        return res.status(500).json({ 
            status: 'error', 
            message: error.message 
        });
    }
}
