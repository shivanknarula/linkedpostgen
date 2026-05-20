export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(450).json({ error: 'Method Not Allowed' });
    }

    const { GITHUB_TOKEN, GITHUB_REPO_OWNER, GITHUB_REPO_NAME } = process.env;

    if (!GITHUB_TOKEN || !GITHUB_REPO_OWNER || !GITHUB_REPO_NAME) {
        return res.status(500).json({ 
            error: 'Missing required GitHub configurations on Vercel Environment Variables.' 
        });
    }

    try {
        // Trigger workflow_dispatch on GitHub Actions
        const response = await fetch(
            `https://api.github.com/repos/${GITHUB_REPO_OWNER}/${GITHUB_REPO_NAME}/actions/workflows/scrape.yml/dispatches`,
            {
                method: 'POST',
                headers: {
                    'Accept': 'application/vnd.github+json',
                    'Authorization': `Bearer ${GITHUB_TOKEN}`,
                    'X-GitHub-Api-Version': '2022-11-28',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ref: 'main' // Trigger on main branch
                })
            }
        );

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`GitHub API returned ${response.status}: ${errorText}`);
        }

        return res.status(200).json({ 
            status: 'success', 
            message: 'Scraping workflow successfully triggered in GitHub Actions!' 
        });

    } catch (error) {
        console.error(error);
        return res.status(500).json({ 
            status: 'error', 
            message: error.message 
        });
    }
}
