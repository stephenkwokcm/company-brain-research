import { loadSkillTriggerIndex, entriesToResolverContent } from './gbrain/src/core/skill-trigger-index.ts';
import { loadRoutingFixtures, runRoutingEval, indexResolverTriggers, structuralRouteMatch } from './gbrain/src/core/routing-eval.ts';

const skillsDir = './gbrain/skills';
const entries = loadSkillTriggerIndex(skillsDir);
const resolverContent = entriesToResolverContent(entries);
const { fixtures, malformed } = loadRoutingFixtures(skillsDir);
const rep = runRoutingEval(resolverContent, fixtures);
console.log(JSON.stringify({
  entries: entries.length,
  fromFrontmatter: entries.filter(e=>e.source==='frontmatter').length,
  fromResolverMd: entries.filter(e=>e.source==='resolver_md').length,
  skillsWithTriggers: new Set(entries.filter(e=>!e.isGStack).map(e=>e.skillPath)).size,
  fixtures: fixtures.length,
  malformed: malformed.length,
  totalCases: rep.totalCases, passed: rep.passed, missed: rep.missed,
  ambiguous: rep.ambiguous, falsePositives: rep.falsePositives,
  top1: rep.top1Accuracy,
}, null, 2));
// dump per-case for analysis
const rows = rep.details.map(d=>({intent:d.fixture.intent, expected:d.fixture.expected_skill, outcome:d.outcome, matched:d.matchedSkills, note:d.note}));
await Bun.write('./d3_baseline_cases.json', JSON.stringify(rows, null, 1));
