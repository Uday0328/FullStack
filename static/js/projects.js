/* ================================================================
   PROJECTS.JS — Fetch and render projects from Flask API
   ================================================================ */

document.addEventListener('DOMContentLoaded', () => {
  loadProjects();
});

async function loadProjects() {
  const grid = document.getElementById('projects-grid');
  const loadingEl = document.getElementById('projects-loading');

  try {
    const response = await fetch('/api/projects');
    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
    const data = await response.json();

    if (loadingEl) loadingEl.remove();

    if (!data.projects || data.projects.length === 0) {
      grid.innerHTML = `
        <div style="grid-column:1/-1;text-align:center;padding:80px 24px;color:var(--text-muted);">
          <p style="font-size:2rem;margin-bottom:12px;">🛠️</p>
          <p>Projects coming soon...</p>
        </div>`;
      return;
    }

    data.projects.forEach((project, index) => {
      const card = createProjectCard(project, index);
      grid.appendChild(card);
    });

    // Trigger reveal for newly added cards
    if (window.setupRevealObserver) {
      window.setupRevealObserver();
    }

  } catch (err) {
    console.error('Failed to load projects:', err);
    if (loadingEl) loadingEl.remove();
    grid.innerHTML = `
      <div style="grid-column:1/-1;text-align:center;padding:60px 24px;color:var(--text-muted);">
        <p>Unable to load projects. Please try again later.</p>
      </div>`;
  }
}

function getProjectIcon(technologies) {
  const tech = (technologies || '').toLowerCase();
  if (tech.includes('python') || tech.includes('ml') || tech.includes('scikit')) return '🤖';
  if (tech.includes('java')) return '☕';
  if (tech.includes('html') || tech.includes('css') || tech.includes('javascript')) return '🌐';
  if (tech.includes('react') || tech.includes('vue')) return '⚛️';
  if (tech.includes('sql') || tech.includes('database')) return '🗄️';
  return '💡';
}

function createProjectCard(project, index) {
  const wrapper = document.createElement('div');
  wrapper.className = `reveal reveal-delay-${Math.min(index % 4 + 1, 5)}`;

  const techs = (project.technologies || '').split(',').map(t => t.trim()).filter(Boolean);
  const techTags = techs.map(t =>
    `<span class="tag">${escapeHtml(t)}</span>`
  ).join('');

  const featuredBadge = project.is_featured
    ? `<span class="badge-featured">⭐ Featured</span>`
    : '';

  const ongoingBadge = project.status === 'Ongoing'
    ? `<span class="badge-featured badge-ongoing">🔄 Ongoing</span>`
    : '';

  const githubLink = project.github_url && project.github_url !== '#' && project.github_url
    ? `<a href="${escapeHtml(project.github_url)}" target="_blank" rel="noopener" class="project-link" aria-label="View GitHub repository">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/></svg>
        GitHub
      </a>`
    : '';

  const demoLink = project.demo_url
    ? `<a href="${escapeHtml(project.demo_url)}" target="_blank" rel="noopener" class="project-link" aria-label="View live demo">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
        Live
      </a>`
    : '';

  wrapper.innerHTML = `
    <div class="project-card" role="article" aria-label="${escapeHtml(project.title)}">
      <div class="project-card-top">
        <div class="project-icon">${getProjectIcon(project.technologies)}</div>
        <div class="project-badges">
          ${featuredBadge}
          ${ongoingBadge}
        </div>
      </div>
      <h3 class="project-title">${escapeHtml(project.title)}</h3>
      <p class="project-desc">${escapeHtml(project.description)}</p>
      <div class="project-tech">${techTags}</div>
      <div class="project-footer">
        <span class="project-date">${escapeHtml(project.date)}</span>
        <div class="project-links">
          ${githubLink}
          ${demoLink}
        </div>
      </div>
    </div>`;

  return wrapper;
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
