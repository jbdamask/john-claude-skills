"""Turn extract.js JSON into a Substack paste page, a Markdown backup, and local images.
Usage: python3 -I build.py <medium-json> <outdir>"""
import json, re, sys, html, os, urllib.request

src, outdir = sys.argv[1], sys.argv[2]
os.makedirs(os.path.join(outdir, 'images'), exist_ok=True)
d = json.load(open(src))

strip_q = lambda u: re.sub(r'\?.*$', '', u or '')
def clean(h):  # drop Medium tracking params from links
    return re.sub(r'href="([^"]*)"', lambda m: f'href="{strip_q(m.group(1))}"', h or '')
text = lambda h: re.sub('<[^>]+>', '', h or '').strip()

BOILER = {'Listen', 'Share', 'More', 'Follow'}
items = [o for o in d['out'] if not (o['t'] == 'P' and text(o.get('html')) in BOILER)]

title = next((text(o['html']) for o in items if o.get('title')), None) \
    or next(text(o['html']) for o in items if o['t'] == 'H1')
sub = next((o for o in items if o.get('subtitle')), None)
if sub is None:  # fallback: an H2 before any body paragraph is the subtitle
    for o in items:
        if o['t'] == 'P': break
        if o['t'] == 'H2': sub = o; break
subtitle = text(sub['html']) if sub else ''

body, md, n = [], [], 0
for o in items:
    t = o['t']
    if t == 'H1' or o is sub: continue
    if t == 'FIGURE':
        if o.get('iframe') and not o.get('src'):  # embeds: leave a link to paste as a Substack embed
            u = strip_q(o['iframe'])
            body.append(f'<p><a href="{u}">{u}</a></p>'); md.append(u); continue
        n += 1; url = strip_q(o['src']); fn = f'{n:02d}{os.path.splitext(url)[1] or ".png"}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with open(os.path.join(outdir, 'images', fn), 'wb') as f: f.write(urllib.request.urlopen(req).read())
        cap = clean(o.get('cap')).strip()
        body.append(f'<figure><img src="{url}" alt="{html.escape(text(cap))}">'
                    + (f'<figcaption>{cap}</figcaption>' if cap else '') + '</figure>')
        md.append(f'![{text(cap)}](images/{fn})' + (f'\n*{text(cap)}*' if cap else ''))
    elif t in ('UL', 'OL'):
        tag = t.lower()
        body.append(f'<{tag}>' + ''.join(f'<li>{clean(i)}</li>' for i in o['items']) + f'</{tag}>')
        md.append('\n'.join((f'{k+1}. ' if t == 'OL' else '- ') + clean(i) for k, i in enumerate(o['items'])))
    elif t == 'PRE':
        body.append(f'<pre><code>{html.escape(o["text"])}</code></pre>'); md.append(f'```\n{o["text"]}\n```')
    elif t == 'HR':
        body.append('<hr>'); md.append('---')
    else:
        tag = {'H2': 'h2', 'H3': 'h3', 'H4': 'h4', 'BLOCKQUOTE': 'blockquote'}.get(t, 'p')
        h = clean(o['html']).strip()
        if not h: continue
        if text(h) == 'TL;DR': h = '<strong>TL;DR</strong>'
        body.append(f'<{tag}>{h}</{tag}>')
        md.append({'h2': '## ', 'h3': '### ', 'h4': '### ', 'blockquote': '> '}.get(tag, '') + h)

page = f'''<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(title)} (Substack paste)</title>
<style>body{{max-width:720px;margin:40px auto;padding:0 16px;font:18px/1.6 Georgia,serif;color:#222;background:#fff}}
.note{{font:14px/1.5 -apple-system,sans-serif;background:#fff8e1;border:1px solid #f0d78c;padding:12px 16px;border-radius:6px}}
.note button{{font:inherit;padding:4px 10px;margin-top:8px;cursor:pointer}}
img{{max-width:100%}} figcaption{{text-align:center;font-size:14px;color:#666}} code{{background:#f3f3f3;padding:1px 4px}}</style></head><body>
<div class="note"><b>Substack title:</b> {html.escape(title)}<br><b>Substack subtitle:</b> {html.escape(subtitle)}<br>
Type the title and subtitle into their own fields in Substack. Then click <b>Copy body</b> and paste into the Substack post body.<br>
<button id="copy">Copy body</button> <span id="msg"></span></div>
<hr>
<div id="post">
{chr(10).join(body)}
</div>
<script>
document.getElementById('copy').onclick = async () => {{
  const post = document.getElementById('post'), msg = document.getElementById('msg');
  try {{
    await navigator.clipboard.write([new ClipboardItem({{
      'text/html': new Blob([post.innerHTML], {{type: 'text/html'}}),
      'text/plain': new Blob([post.innerText], {{type: 'text/plain'}}) }})]);
    msg.textContent = 'Copied. Paste into Substack with Cmd+V.';
  }} catch (e) {{  // fall back to selecting the body so Cmd+C works
    const r = document.createRange(); r.selectNodeContents(post);
    const s = getSelection(); s.removeAllRanges(); s.addRange(r);
    msg.textContent = 'Body selected. Press Cmd+C, then paste into Substack.';
  }}
}};
</script></body></html>'''
with open(os.path.join(outdir, 'post-for-substack.html'), 'w') as f: f.write(page)
with open(os.path.join(outdir, 'post.md'), 'w') as f:
    f.write(f'# {title}\n\n' + (f'*{subtitle}*\n\n' if subtitle else '') + '\n\n'.join(md) + '\n')
print(json.dumps({'title': title, 'subtitle': subtitle, 'images': n, 'outdir': outdir}))
