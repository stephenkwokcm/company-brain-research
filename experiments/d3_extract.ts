import { readdirSync, readFileSync, existsSync, statSync } from 'fs';
import { join } from 'path';
import { parseSkillFrontmatter } from './gbrain/src/core/skill-frontmatter.ts';
const dir='./gbrain/skills';
const out:any[]=[];
for (const n of readdirSync(dir)) {
  if (n.startsWith('_')||n.startsWith('.')) continue;
  const p=join(dir,n); if(!statSync(p).isDirectory()) continue;
  const f=join(p,'SKILL.md'); if(!existsSync(f)) continue;
  const c=readFileSync(f,'utf-8');
  const fm=parseSkillFrontmatter(c);
  const body=c.replace(/^---[\s\S]*?\n---\n/,'');
  out.push({slug:n, name:fm?.name??n, description:fm?.description??'', triggers:fm?.triggers??[],
    bodyBytes:body.length, body:body.slice(0,4000), skillMdBytes:c.length});
}
await Bun.write('./d3_skills.json', JSON.stringify(out,null,1));
console.log('skills:',out.length,'withDesc:',out.filter(s=>s.description).length,'triggers:',out.reduce((a,s)=>a+s.triggers.length,0));
console.log('desc bytes total:',out.reduce((a,s)=>a+s.description.length,0));
console.log('name+desc bytes:',out.reduce((a,s)=>a+s.name.length+s.description.length,0));
console.log('skillmd bytes total:',out.reduce((a,s)=>a+s.skillMdBytes,0));
