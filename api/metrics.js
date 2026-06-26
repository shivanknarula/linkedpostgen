import { createClient } from '@supabase/supabase-js';

export default async function handler(req, res) {
    // Disable Vercel edge caching
    res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');

    const supabaseUrl = process.env.SUPABASE_URL;
    const supabaseKey = process.env.SUPABASE_ANON_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY;

    if (!supabaseUrl || !supabaseKey) {
        return res.status(500).json({ 
            status: 'error', 
            message: 'Supabase credentials are not configured on Vercel environment variables.' 
        });
    }

    try {
        const supabase = createClient(supabaseUrl, supabaseKey);

        // Perform parallel queries to get metrics
        const [profilesRes, totalRunsRes, latestRunsRes] = await Promise.all([
            supabase.from('profiles').select('*', { count: 'exact', head: true }).eq('is_active', true),
            supabase.from('crawl_runs').select('*', { count: 'exact', head: true }),
            supabase.from('crawl_runs').select('duration_ms, status, start_time, error_message, posts_discovered, posts_extracted, posts_scored').order('id', { ascending: false }).limit(5)
        ]);

        if (profilesRes.error) throw profilesRes.error;
        if (totalRunsRes.error) throw totalRunsRes.error;
        if (latestRunsRes.error) throw latestRunsRes.error;

        const metrics = {
            active_profiles: profilesRes.count || 0,
            total_runs: totalRunsRes.count || 0,
            latest_runs: latestRunsRes.data || []
        };

        return res.status(200).json({ status: 'success', metrics });

    } catch (error) {
        console.error('metrics handler error:', error);
        return res.status(500).json({ status: 'error', message: error.message });
    }
}
