/* Plotly browser controller. All records come from the archived ACS build. */
(() => {
  'use strict';
  const source = JSON.parse(document.getElementById('dataset').textContent);
  const all = source.rows;
  const el = id => document.getElementById(id);
  const money = x => '$' + Math.round(x).toLocaleString('en-US');
  const integer = x => Math.round(x).toLocaleString('en-US');
  const pct = x => x.toFixed(1) + '%';
  const escape = x => String(x).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const optionRows = [...all].sort((a,b) => a.county.localeCompare(b.county));
  optionRows.forEach(r => el('county').add(new Option(r.county, r.fips)));
  let revision = 0;
  let chartReady = false;

  function eligible(r) {
    return r.monthly_gross_rent <= +el('budget').value && r.computable_households >= +el('minimum').value;
  }
  function profile() {
    const r = all.find(r => r.fips === el('county').value);
    if (!r) {
      el('details').textContent = 'Hover over a dot for details; click it, choose a county above, or activate a county name below to keep its profile visible.';
      return;
    }
    const warning = eligible(r) ? 'Included in the current comparison.' : 'Outside the current filters; its profile remains visible, but its dot and table row are excluded.';
    el('details').innerHTML = `<b>${escape(r.county)} County</b> — ${warning}<br>Median gross rent ${money(r.monthly_gross_rent)} ± ${money(r.rent_moe)} (90% MOE); median renter income ${money(r.annual_renter_income)} ± ${money(r.income_moe)} per year (90% MOE).<br>Burdened households: ${integer(r.burdened_households)} / ${integer(r.computable_households)} = <b>${pct(r.burden_pct)}</b>; ${integer(r.not_computed)} cash-rent households have ratios not computed.`;
  }
  function makeTrace(rows, selected) {
    return {
      type:'scatter',mode:selected?'markers+text':'markers',name:selected?'Inspected county':'Counties',
      showlegend:false,
      x:rows.map(r=>r.monthly_gross_rent), y:rows.map(r=>r.burden_pct),
      text:rows.map(r=>selected?r.county:''),textposition:'top center',
      marker:{size:selected?15:10,color:selected?'#c78327':'#155ab6',opacity:selected?1:.78,line:{color:selected?'#29394a':'white',width:selected?1.5:.8},symbol:selected?'diamond':'circle'},
      error_x:{type:'data',array:rows.map(r=>r.rent_moe),visible:el('errors').checked,color:'#8294a7',thickness:1,width:2},
      customdata:rows.map(r=>[r.county,r.annual_renter_income,r.computable_households,r.rent_moe,r.fips,r.burdened_households,r.not_computed]),
      hovertemplate:'<b>%{customdata[0]} County</b><br>Median gross rent: $%{x:,.0f}/month<br>Rent 90% MOE: ±$%{customdata[3]:,.0f}<br>Rent burden: %{y:.1f}%<br>Median renter income: $%{customdata[1]:,.0f}/year<br>Burdened / computed: %{customdata[5]:,.0f} / %{customdata[2]:,.0f}<br>Ratios not computed: %{customdata[6]:,.0f}<extra></extra>'
    };
  }
  async function render() {
    const selected = el('county').value;
    const rows = all.filter(eligible);
    const n = rows.reduce((s,r)=>s+r.computable_households,0);
    const numerator = rows.reduce((s,r)=>s+r.burdened_households,0);
    el('budget-value').textContent = money(+el('budget').value)+'/month';
    el('summary').innerHTML = `<div class="stat"><b>${rows.length} / 67</b><span>Counties shown</span></div><div class="stat"><b>${integer(n)}</b><span>Households with computed burden</span></div><div class="stat"><b>${n?pct(100*numerator/n):'—'}</b><span>Pooled burden in shown counties</span></div>`;
    el('status').textContent = rows.length ? 'Filter uses point estimates. Compare error bars near the ceiling; counts are households, not survey sample sizes.' : 'No counties meet these filters. Raise the ceiling or reduce the household-size minimum.';
    const sorted = [...rows].sort((a,b)=>a.monthly_gross_rent-b.monthly_gross_rent || a.county.localeCompare(b.county));
    el('rows').innerHTML = sorted.map(r=>`<tr><td><button type="button" data-county="${r.fips}">${escape(r.county)}</button></td><td>${money(r.monthly_gross_rent)} ± ${money(r.rent_moe)}</td><td>${pct(r.burden_pct)}</td><td>${money(r.annual_renter_income)}</td><td>${integer(r.computable_households)}</td></tr>`).join('');
    profile();
    const narrow = document.documentElement.clientWidth < 600;
    const traces=[makeTrace(rows.filter(r=>r.fips!==selected),false),makeTrace(rows.filter(r=>r.fips===selected),true)];
    const layout={
      margin:{l:narrow?53:66,r:18,t:25,b:narrow?90:65},font:{family:'system-ui, sans-serif',size:12,color:'#213547'},
      paper_bgcolor:'white',plot_bgcolor:'white',hovermode:'closest',datarevision:++revision,
      xaxis:{title:{text:narrow?'Median gross rent<br>($/month; 2024 dollars)':'Median monthly gross rent (2024 dollars)',standoff:12},range:[500,1950],tickprefix:'$',tickformat:',.0f',nticks:narrow?4:7,gridcolor:'#e8edf2',zeroline:false,showline:true,linecolor:'#aebcca'},
      yaxis:{title:{text:'Rent-burdened households (%)',standoff:9},range:[20,65],ticksuffix:'%',gridcolor:'#e8edf2',zeroline:false,showline:true,linecolor:'#aebcca'},
      shapes:[{type:'line',x0:500,x1:1950,y0:source.state.burden_pct,y1:source.state.burden_pct,line:{color:'#667789',width:1,dash:'dash'}},{type:'line',x0:+el('budget').value,x1:+el('budget').value,y0:20,y1:65,line:{color:'#a46a22',width:1,dash:'dot'}}],
      annotations:rows.length?[]:[{text:'No counties meet these filters',xref:'paper',yref:'paper',x:.5,y:.5,showarrow:false,font:{size:16}}]
    };
    await Plotly.react(el('chart'),traces,layout,{responsive:true,displaylogo:false,scrollZoom:false,displayModeBar:true,modeBarButtonsToRemove:['lasso2d','select2d','toImage']});
    if (!chartReady) {
      el('chart').on('plotly_click',event=>{const p=event.points[0];if(p.customdata){el('county').value=p.customdata[4];render();}});
      chartReady = true;
    }
  }
  el('budget').addEventListener('input',render);
  for (const id of ['minimum','county','errors']) el(id).addEventListener('change',render);
  el('rows').addEventListener('click',e=>{const b=e.target.closest('[data-county]');if(b){el('county').value=b.dataset.county;render();}});
  el('reset').addEventListener('click',()=>{el('budget').value='1800';el('minimum').value='0';el('county').value='';el('errors').checked=false;render();});
  let resizeTimer;
  window.addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(render,120);});
  if (typeof Plotly === 'undefined') el('status').textContent='The local Plotly library did not load. Use the downloadable CSV below.';
  else render();
})();
// The standalone explorer also fits its same-origin article iframe automatically.
(() => {
  if (window.parent === window) return;
  const report = () => window.parent.postMessage({type:'blog7-height',height:document.body.scrollHeight+24}, window.location.origin);
  new ResizeObserver(report).observe(document.body);
})();
