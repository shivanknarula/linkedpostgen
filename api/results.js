import { createClient } from '@supabase/supabase-js';

export default async function handler(req, res) {
    // Disable Vercel edge caching to ensure live data is always fetched
    res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');

    const supabaseUrl = process.env.SUPABASE_URL;
    const supabaseKey = process.env.SUPABASE_ANON_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY;

    if (!supabaseUrl || !supabaseKey) {
        return res.status(500).json({ 
            status: 'error', 
            message: 'Supabase credentials (SUPABASE_URL and SUPABASE_ANON_KEY) are not configured on Vercel environment variables.' 
        });
    }

    try {
        const supabase = createClient(supabaseUrl, supabaseKey);

        // Fetch scored posts joined with scores and comments
        const { data, error } = await supabase
            .from('posts')
            .select(`
                url,
                date:published_date,
                text:post_text,
                likes,
                comments,
                category,
                scores (
                    total_score,
                    reasoning
                ),
                generated_comments (
                    comment_text
                )
            `)
            .eq('status', 'scored')
            .limit(300);

        if (error) throw error;

        // Map database fields to the exact keys expected by the frontend
        const parsedData = (data || []).map(row => {
            const scoreVal = row.scores ? Math.floor(row.scores.total_score / 10) : 0;
            const reasoningVal = row.scores ? row.scores.reasoning : '';
            
            // Support both array and object formats for generated_comments
            let commentVal = '';
            if (row.generated_comments) {
                if (Array.isArray(row.generated_comments)) {
                    if (row.generated_comments.length > 0) {
                        commentVal = row.generated_comments[0].comment_text;
                    }
                } else if (row.generated_comments.comment_text) {
                    commentVal = row.generated_comments.comment_text;
                }
            }

            return {
                url: row.url,
                date: row.date || '',
                score: scoreVal.toString(),
                reasoning: reasoningVal,
                comment: commentVal,
                likes: (row.likes || 0).toString(),
                comments: (row.comments || 0).toString(),
                text: row.text || '',
                category: row.category,
                raw_score: row.scores ? row.scores.total_score : 0 // Keep raw score for sorting
            };
        });

        // Sort by raw_score DESC
        parsedData.sort((a, b) => b.raw_score - a.raw_score);

        return res.status(200).json({ status: 'success', data: parsedData.slice(0, 50) });

    } catch (error) {
        console.error('results handler error:', error);
        return res.status(500).json({ status: 'error', message: error.message });
    }
}
