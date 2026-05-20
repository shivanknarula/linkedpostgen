import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
    const csvPath = path.join(process.cwd(), 'robotics_posts.csv');

    if (!fs.existsSync(csvPath)) {
        return res.status(200).json({ status: 'success', data: [] });
    }

    try {
        const csvText = fs.readFileSync(csvPath, 'utf-8');
        const parsedData = parseCSV(csvText);
        return res.status(200).json({ status: 'success', data: parsedData });
    } catch (error) {
        console.error(error);
        return res.status(500).json({ status: 'error', message: error.message });
    }
}

function parseCSV(csvText) {
    const lines = [];
    let row = [""];
    lines.push(row);
    let inQuotes = false;

    for (let i = 0; i < csvText.length; i++) {
        let c = csvText[i];
        let next = csvText[i+1];

        if (c === '"') {
            if (inQuotes && next === '"') {
                row[row.length - 1] += '"';
                i++;
            } else {
                inQuotes = !inQuotes;
            }
        } else if (c === ',' && !inQuotes) {
            row.push("");
        } else if ((c === '\r' || c === '\n') && !inQuotes) {
            if (c === '\r' && next === '\n') {
                i++;
            }
            row = [""];
            lines.push(row);
        } else {
            row[row.length - 1] += c;
        }
    }
    
    const headers = lines[0];
    const result = [];
    for (let i = 1; i < lines.length; i++) {
        const currentLine = lines[i];
        // Ensure the row has the same length as headers (ignoring empty trailing lines)
        if (currentLine.length < headers.length || (currentLine.length === 1 && currentLine[0] === "")) continue;
        const obj = {};
        for (let j = 0; j < headers.length; j++) {
            obj[headers[j]] = currentLine[j] || '';
        }
        result.push(obj);
    }
    return result;
}
