// Run in the Medium post tab (javascript_tool). Collects the article as JSON and
// saves it to ~/Downloads/medium-<postid>.json. Returns a summary for the author check.
(() => {
  const a = document.querySelector('article');
  if (!a) return { error: 'no <article> on page' };
  const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
  const inl = el => { let h = ''; el.childNodes.forEach(n => {
    if (n.nodeType === 3) { h += esc(n.textContent); return; }
    if (n.nodeType !== 1) return;
    const t = n.tagName, inner = inl(n);
    if (t === 'STRONG' || t === 'B') h += `<strong>${inner}</strong>`;
    else if (t === 'EM' || t === 'I') h += `<em>${inner}</em>`;
    else if (t === 'A') h += `<a href="${n.href}">${inner}</a>`;
    else if (t === 'CODE') h += `<code>${inner}</code>`;
    else if (t === 'BR') h += '<br>';
    else h += inner; }); return h; };
  const out = [];
  a.querySelectorAll('h1,h2,h3,h4,p,pre,blockquote,figure,ul,ol,hr').forEach(el => {
    if (el.closest('figure') && el.tagName !== 'FIGURE') return;
    if (el.parentElement.closest('blockquote,ul,ol,pre')) return;
    const t = el.tagName;
    if (t === 'FIGURE') {
      const img = el.querySelector('img'); const cap = el.querySelector('figcaption');
      out.push({ t, src: img?.src, alt: img?.alt, cap: cap ? inl(cap) : '', iframe: el.querySelector('iframe')?.src });
    } else if (t === 'UL' || t === 'OL') out.push({ t, items: [...el.querySelectorAll(':scope>li')].map(inl) });
    else if (t === 'PRE') out.push({ t, text: el.innerText });
    else if (t === 'HR') out.push({ t });
    else out.push({ t, html: inl(el),
      title: el.classList.contains('pw-post-title') || undefined,
      subtitle: el.classList.contains('pw-subtitle-paragraph') || undefined });
  });
  const author = document.querySelector('[data-testid="authorName"]')?.innerText
    || document.querySelector('meta[name="author"]')?.content || '';
  const id = (location.pathname.match(/([0-9a-f]{10,12})$/) || [, 'post'])[1];
  const data = { url: location.origin + location.pathname, author, title: document.querySelector('h1')?.innerText, out };
  const l = document.createElement('a');
  l.href = URL.createObjectURL(new Blob([JSON.stringify(data, null, 1)], { type: 'application/json' }));
  l.download = `medium-${id}.json`; document.body.appendChild(l); l.click(); l.remove();
  return { file: `medium-${id}.json`, author, title: data.title, blocks: out.length,
           images: out.filter(o => o.t === 'FIGURE').length };
})()
