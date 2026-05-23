export default async function handler(req, res) {
    // Always fetch the latest CSV directly from GitHub raw content at runtime.
    // This means data is live immediately after GitHub Actions commits — no Vercel redeploy needed.
    const owner = process.env.GITHUB_REPO_OWNER || 'shivanknarula';
    const repo  = process.env.GITHUB_REPO_NAME  || 'linkedpostgen';
    const branch = 'main';
    const rawUrl = `https://raw.githubusercontent.com/${owner}/${repo}/${branch}/robotics_posts.csv?t=${Date.now()}`;

    try {
        const response = await fetch(rawUrl, {
            // Bust any CDN cache so we always get the latest commit
            headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' }
        });

        if (!response.ok) {
            throw new Error(`GitHub raw fetch failed: ${response.status} ${response.statusText}`);
        }

        const csvText = await response.text();
        const parsedData = parseCSV(csvText);

        // Cache the response for 5 minutes on the client side but always revalidate
        res.setHeader('Cache-Control', 's-maxage=300, stale-while-revalidate');
        return res.status(200).json({ status: 'success', data: parsedData });

    } catch (error) {
        console.error('results handler error:', error);
        return res.status(500).json({ status: 'error', message: error.message });
    }
}

function parseCSV(csvText) {
    const lines = [];
    let row = [''];
    lines.push(row);
    let inQuotes = false;

    for (let i = 0; i < csvText.length; i++) {
        const c    = csvText[i];
        const next = csvText[i + 1];

        if (c === '"') {
            if (inQuotes && next === '"') {
                row[row.length - 1] += '"';
                i++;
            } else {
                inQuotes = !inQuotes;
            }
        } else if (c === ',' && !inQuotes) {
            row.push('');
        } else if ((c === '\r' || c === '\n') && !inQuotes) {
            if (c === '\r' && next === '\n') i++;
            row = [''];
            lines.push(row);
        } else {
            row[row.length - 1] += c;
        }
    }

    const headers = lines[0];
    const result  = [];

    for (let i = 1; i < lines.length; i++) {
        const currentLine = lines[i];
        if (currentLine.length < headers.length || (currentLine.length === 1 && currentLine[0] === '')) continue;
        const obj = {};
        for (let j = 0; j < headers.length; j++) {
            obj[headers[j]] = currentLine[j] || '';
        }
        result.push(obj);
    }

    return result;
}
