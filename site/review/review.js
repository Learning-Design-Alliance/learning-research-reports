// Review drafting: a "Review" action on every paragraph opens a form that builds a learning-wiki review
// record (research layer schema: review.target, review_type, assertion, rationale, author.basis). The
// paragraph's link and an excerpt go in supporting_artifacts, so the record points at the exact text.
// The form speaks plainly and the record keeps the schema's values: TYPE_LABEL and BASIS_LABEL map one
// to the other, and a typed name becomes a human:<slug> author id. Nothing leaves the page until the
// reader chooses Submit on GitHub, which opens a prefilled issue in learning-wiki for them to post.
const RCFG = JSON.parse(document.getElementById('reviewcfg').textContent);
const dlg = document.getElementById('review-dialog');
const form = dlg.querySelector('form');
const WIKI_ISSUES = 'https://github.com/Learning-Design-Alliance/learning-wiki/issues/new';
const TYPE_LABEL = {
  question: ['A question', 'Something you would like the authors to explain or clarify.'],
  methodological_concern: ['A concern about the method', 'The design, data or procedure may not support the conclusion.'],
  statistical_concern: ['A concern about the statistics', 'An estimate, test or interval may be wrong or misleading.'],
  governance_concern: ['A concern about ethics or governance', 'Consent, privacy, licensing or conflicts of interest.'],
  verification: ['I checked it and it holds', 'You checked a number or a step and it is right.'],
  reanalysis: ['I reanalysed the data', 'You ran your own analysis of the same data.'],
  replication: ['I replicated it', 'You repeated the study with new data.'],
  boundary_condition: ['It does not hold everywhere', 'A setting, population or condition where the finding would differ.'],
  practice_report: ['A report from practice', 'What you have seen when this is used in real teaching or learning.'],
  theoretical_alternative: ['Another explanation', 'A different account that fits the same results.'],
  supporting_evidence: ['Evidence that supports it', 'Other work that agrees with this finding.'],
  contradictory_evidence: ['Evidence that contradicts it', 'Other work that disagrees with this finding.'],
  response: ['A response to another review', 'A reply to a review already posted.'],
};
const BASIS_LABEL = {
  'read-the-release': 'I read the release', 'read-the-protocol': 'I read the protocol',
  'read-the-artifacts': 'I read the supporting documents', 'reproduced-the-analysis': 'I re-ran the analysis',
  'reanalysed-the-data': 'I reanalysed the data', 'ran-a-replication': 'I ran a replication',
  'practitioner-in-this-setting': 'I work in this setting', 'participant-in-this-research': 'I took part in this research',
  'domain-expertise-stated': 'I have expertise in the subject', 'methodological-expertise-stated': 'I have expertise in the methods',
  'automated-check': 'An automated check', 'other': 'Something else (say what in your reasoning)',
};
RCFG.types.forEach(t=>{const o=document.createElement('option');o.value=t;o.textContent=(TYPE_LABEL[t]||[t])[0];form.type.appendChild(o);});
const basesBox = form.querySelector('.bases');
RCFG.bases.forEach(b=>{const l=document.createElement('label');l.className='chk';
  const i=document.createElement('input');i.type='checkbox';i.value=b;i.checked=(b==='read-the-release');
  l.append(i,' '+(BASIS_LABEL[b]||b));basesBox.appendChild(l);});
const typeHint=form.querySelector('.rv-type-hint'), status=form.querySelector('.rv-status'), err=form.querySelector('.rv-error');
let current = null;
function yq(s){return JSON.stringify(String(s||''));}
function today(){return new Date().toISOString().slice(0,10);}
function slugify(s){return (s||'review').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,60)||'review';}
function authorId(name){name=(name||'').trim();
  if(!name) return 'human:anonymous';
  return /^(human|agent|org):/.test(name)?name:'human:'+slugify(name);}
function buildYaml(){
  const f=form, [kind, ref] = f.target.value.split('|');
  const bases=[...basesBox.querySelectorAll('input:checked')].map(x=>x.value);
  const id=`${today()}-${slugify(f.assertion.value)}`;
  typeHint.textContent=(TYPE_LABEL[f.type.value]||['',''])[1];
  const lines=['schema_version: 1','','review:',`  id: ${id}`,`  created_at: ${today()}`,`  review_type: ${f.type.value}`,'',
    '  target:',`    kind: ${kind}`,`    ref: ${ref}`];
  if(kind==='release') lines.push(`    version: ${RCFG.version}`);
  lines.push('',`  assertion: ${yq(f.assertion.value)}`,`  rationale: ${yq(f.rationale.value)}`,'','  supporting_artifacts:',
    '    - kind: document',`      title: ${yq(document.title+', paragraph '+current.id)}`,'      location:','        kind: url',
    `        ref: ${yq(location.href.split('#')[0]+'#'+current.id)}`,`      note: ${yq('Excerpt: '+current.excerpt)}`,'',
    '  author:',`    id: ${authorId(f.author.value)}`,'    basis:');
  (bases.length?bases:['read-the-release']).forEach(b=>lines.push(`      - ${b}`));
  lines.push(`    identity_state: ${f.identity.value}`,`    disclosure: ${yq(f.disclosure.value)}`);
  f.yaml.value=lines.join('\n')+'\n';
  return id;
}
function say(msg){status.textContent=msg; if(msg) setTimeout(()=>{if(status.textContent===msg) status.textContent='';},4000);}
function needPoint(){const ok=form.assertion.value.trim()!=='';err.hidden=ok;if(!ok)form.assertion.focus();return ok;}
function openReview(p){
  const analyses=[...new Set([...p.querySelectorAll('.prov')].map(x=>x.dataset.analysis))];
  const text=p.cloneNode(true); text.querySelectorAll('.prov-pop,.rv-btn,.hanchor').forEach(x=>x.remove());
  current={id:p.id, excerpt:text.textContent.trim().replace(/\s+/g,' ').slice(0,240)};
  form.target.innerHTML='';
  [[`release|${RCFG.release}`,`The whole release (${RCFG.release} ${RCFG.version})`],
   ...analyses.map(a=>[`analysis|${RCFG.release}/${RCFG.version}/${a}`,`The analysis behind this paragraph: ${a}`])]
    .forEach(([v,l])=>{const o=document.createElement('option');o.value=v;o.textContent=l;form.target.appendChild(o);});
  if(analyses.length) form.target.selectedIndex=1;
  err.hidden=true; say(''); buildYaml(); dlg.showModal();
}
form.addEventListener('input', ()=>{buildYaml(); if(!err.hidden && form.assertion.value.trim()) err.hidden=true;});
form.addEventListener('change', buildYaml);
form.querySelector('[data-act=cancel]').addEventListener('click',()=>dlg.close());
form.querySelector('[data-act=copy]').addEventListener('click',()=>{buildYaml();
  if(navigator.clipboard) navigator.clipboard.writeText(form.yaml.value).then(()=>say('Copied to the clipboard.'),()=>say('Could not copy: use Download instead.'));
  else say('Could not copy: use Download instead.');});
form.querySelector('[data-act=download]').addEventListener('click',()=>{const id=buildYaml();
  const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([form.yaml.value],{type:'text/yaml'}));
  a.download=id+'.yaml';a.click();say('Saved as '+id+'.yaml.');});
form.querySelector('[data-act=submit]').addEventListener('click',()=>{if(!needPoint()) return; buildYaml();
  const title=`Review of ${RCFG.release} ${RCFG.version}: ${form.assertion.value.trim()}`.slice(0,240);
  const body=`A review of research release ${RCFG.release} ${RCFG.version}, drafted with the review form in its report.\n\n`+
    '```yaml\n'+form.yaml.value+'```\n';
  window.open(WIKI_ISSUES+'?title='+encodeURIComponent(title)+'&body='+encodeURIComponent(body),'_blank','noopener');
  say('Opened GitHub in a new tab: check your review there and post it.');});
document.querySelectorAll('article p.para').forEach(p=>{
  const b=document.createElement('button');b.type='button';b.className='rv-btn';b.textContent='Review';
  b.setAttribute('aria-label','Review this paragraph');b.addEventListener('click',()=>openReview(p));p.appendChild(b);});
