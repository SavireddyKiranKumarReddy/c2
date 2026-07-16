"""Small dependency-free dashboard for the local simulation."""

DASHBOARD_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Windows Manager Simulation</title>
  <style>
    :root{color-scheme:dark;font-family:Inter,system-ui,sans-serif;background:#0b1020;color:#e8ecf4}
    body{max-width:1100px;margin:0 auto;padding:32px} h1{margin-bottom:4px}.muted{color:#99a5ba}
    .notice{padding:12px 16px;background:#14352c;border:1px solid #2a7d62;border-radius:10px;margin:24px 0}
    .grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.card{background:#121a2d;border:1px solid #26314a;border-radius:12px;padding:18px}
    table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:8px;border-bottom:1px solid #26314a;font-size:13px}
    input,select,button{padding:9px;border-radius:7px;border:1px solid #34415d;background:#0b1020;color:#e8ecf4}button{cursor:pointer;background:#2758c7}
    pre{white-space:pre-wrap;word-break:break-word}.wide{grid-column:1/-1}@media(max-width:760px){.grid{grid-template-columns:1fr}}
  </style>
</head>
<body>
  <h1>Endpoint Simulation Lab</h1><div class="muted">Consent-based synthetic telemetry</div>
  <div class="notice">This build does not capture keyboard input, install persistence, or run shell commands.</div>
  <label>API token <input id="token" type="password" autocomplete="off"></label>
  <button id="refresh">Refresh</button>
  <div class="grid" style="margin-top:18px">
    <section class="card"><h2>Agents</h2><div id="agents">Enter the token and refresh.</div></section>
    <section class="card"><h2>Safe command</h2>
      <select id="agent"></select><select id="command"><option>ping</option><option>system_info</option><option>echo</option></select>
      <input id="argument" placeholder="Optional echo text"><button id="send">Queue</button><div id="status"></div>
    </section>
    <section class="card wide"><h2>Synthetic telemetry</h2><div id="events"></div></section>
    <section class="card wide"><h2>Command history</h2><div id="commands"></div></section>
  </div>
<script>
const $=id=>document.getElementById(id); const esc=v=>String(v??'').replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c]));
async function api(path,options={}){options.headers={...(options.headers||{}),Authorization:'Bearer '+$('token').value,'Content-Type':'application/json'};let r=await fetch(path,options);if(!r.ok)throw new Error((await r.json()).error||r.statusText);return r.json()}
function table(rows,cols){if(!rows.length)return '<p class="muted">No records.</p>';return '<table><tr>'+cols.map(c=>'<th>'+esc(c)+'</th>').join('')+'</tr>'+rows.map(r=>'<tr>'+cols.map(c=>'<td>'+esc(r[c])+'</td>').join('')+'</tr>').join('')+'</table>'}
async function refresh(){try{let [a,e,c]=await Promise.all([api('/api/agents'),api('/api/telemetry'),api('/api/commands')]);$('agents').innerHTML=table(a,['id','hostname','platform','last_seen']);$('events').innerHTML=table(e,['timestamp','agent_id','category','content']);$('commands').innerHTML=table(c,['created_at','agent_id','name','status','result']);$('agent').innerHTML=a.map(x=>'<option value="'+esc(x.id)+'">'+esc(x.id)+'</option>').join('')}catch(e){$('status').textContent=e.message}}
$('refresh').onclick=refresh;$('send').onclick=async()=>{try{await api('/api/commands',{method:'POST',body:JSON.stringify({agent_id:$('agent').value,name:$('command').value,argument:$('argument').value})});$('status').textContent='Queued';refresh()}catch(e){$('status').textContent=e.message}};
</script></body></html>"""

