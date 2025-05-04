const API_BASE = 'http://localhost:5000';

const topics = ['india','technology','sports','health','business'];
let currentTopic = 'world';

window.addEventListener('DOMContentLoaded', () => {
  renderTopics();
  loadArticles(currentTopic);

  document.getElementById('trend-btn')
    .addEventListener('click', () => loadTrend(7));
});

// Sidebar
function renderTopics() {
  const ul = document.getElementById('topics');
  topics.forEach(t => {
    const li = document.createElement('li');
    const btn = document.createElement('button');
    btn.textContent = t.charAt(0).toUpperCase() + t.slice(1);
    btn.addEventListener('click', () => {
      currentTopic = t;
      document.getElementById('current-topic').textContent = `Latest News: ${btn.textContent}`;
      document.getElementById('trend-chart').style.display = 'none';
      loadArticles(t);
    });
    li.appendChild(btn);
    ul.appendChild(li);
  });
}

// Fetch & display articles
async function loadArticles(query) {
  const container = document.getElementById('articles');
  container.innerHTML = '<p>Loading...</p>';
  try {
    const res = await fetch(`${API_BASE}/search`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ query })
    });
    const articles = await res.json();
    if (!Array.isArray(articles) || articles.length === 0) {
      container.innerHTML = '<p>No articles found.</p>';
      return;
    }
    container.innerHTML = '';
    articles.forEach(art => {
      const card = document.createElement('div');
      card.className = 'article-card';

      const a = document.createElement('a');
      a.href = art.url; a.target = '_blank';
      a.textContent = art.title;

      const meta = document.createElement('div');
      meta.className = 'meta';
      meta.textContent = art.published_at;

      const sentiment = document.createElement('div');
      const score = art.sentiment.toFixed(2);
      sentiment.className = 'sentiment ' + (art.sentiment>=0?'text-positive':'text-negative');
      sentiment.textContent = `Sentiment: ${score}`;

      if (art.description) {
        const desc = document.createElement('p');
        desc.textContent = art.description;
        card.append(a, meta, sentiment, desc);
      } else {
        card.append(a, meta, sentiment);
      }

      container.appendChild(card);
    });
  } catch (err) {
    container.innerHTML = '<p>Error loading articles.</p>';
    console.error(err);
  }
}

// Fetch & draw sentiment trend
async function loadTrend(days) {
  try {
    const res = await fetch(`${API_BASE}/sentiment-trend?days=${days}`);
    const data = await res.json();
    const labels = data.map(d => d._id);
    const values = data.map(d => d.avg_sentiment.toFixed(2));

    drawChart(labels, values);
  } catch (err) {
    console.error(err);
  }
}

// Simple line chart using Canvas
function drawChart(labels, values) {
  const canvas = document.getElementById('trend-chart');
  canvas.style.display = 'block';
  const ctx = canvas.getContext('2d');
  const w = canvas.width, h = canvas.height;
  ctx.clearRect(0,0,w,h);

  // margins
  const m = 40, 
        x0 = m, y0 = h - m, 
        plotW = w - 2*m, plotH = h - 2*m;
  // scale
  const minV = Math.min(...values), maxV = Math.max(...values);
  // draw axes
  ctx.strokeStyle = '#333';
  ctx.beginPath();
  ctx.moveTo(x0,y0);
  ctx.lineTo(x0, m);
  ctx.lineTo(w-m, m);
  ctx.stroke();

  // draw points & line
  const dx = plotW / (values.length - 1);
  ctx.beginPath();
  values.forEach((v,i) => {
    const x = x0 + i*dx;
    const y = y0 - ((v - minV)/(maxV - minV))*plotH;
    if (i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
  });
  ctx.strokeStyle = '#0077cc';
  ctx.stroke();

  // draw labels
  ctx.fillStyle = '#000';
  ctx.textAlign = 'center';
  labels.forEach((lab,i) => {
    const x = x0 + i*dx;
    ctx.fillText(lab, x, y0 + 15);
  });
  // y-axis ticks
  ctx.textAlign = 'right';
  [minV, maxV].forEach((v, i) => {
    const y = y0 - i*plotH;
    ctx.fillText(v, x0 - 5, y);
  });
}
