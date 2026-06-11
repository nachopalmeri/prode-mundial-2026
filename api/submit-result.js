module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { results } = req.body;
  if (!results || typeof results !== 'object' || Object.keys(results).length === 0) {
    return res.status(400).json({ error: 'Missing results object' });
  }

  const token = process.env.GH_PAT;
  if (!token) {
    return res.status(500).json({ error: 'GH_PAT not configured. Set it in Vercel env vars.' });
  }

  const owner = 'nachopalmeri';
  const repo = 'prode-mundial-2026';
  const path = 'data/runtime/results.json';
  const apiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${path}`;

  try {
    const getRes = await fetch(apiUrl, {
      headers: { Authorization: `Bearer ${token}`, Accept: 'application/vnd.github.v3+json' }
    });
    if (!getRes.ok) {
      return res.status(500).json({ error: `GitHub API error: ${getRes.statusText}` });
    }

    const currentData = await getRes.json();
    const sha = currentData.sha;
    const content = JSON.parse(Buffer.from(currentData.content, 'base64').toString('utf-8'));

    Object.entries(results).forEach(([id, score]) => {
      content.results[id] = score;
    });
    content.last_updated = new Date().toISOString().split('T')[0];

    const newContent = Buffer.from(JSON.stringify(content, null, 2)).toString('base64');
    const commitMsg = `Resultados: ${Object.entries(results).map(([id, s]) => `#${id} ${s}`).join(', ')}`;

    const commitRes = await fetch(apiUrl, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: 'application/vnd.github.v3+json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message: commitMsg, content: newContent, sha })
    });

    const commitData = await commitRes.json();
    if (commitRes.ok) {
      return res.status(200).json({ success: true, message: `Guardados: ${Object.keys(results).join(', ')}` });
    }
    return res.status(500).json({ error: commitData.message || 'Commit failed' });
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
};
