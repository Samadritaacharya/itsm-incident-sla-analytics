import assert from 'node:assert/strict'
import test from 'node:test'
import { project,runSimulation } from '../lib/engine.ts'
test('every scenario is deterministic and bounded',()=>{for(const s of project.scenarios){const a=runSimulation(s.id,50,''),b=runSimulation(s.id,50,'');assert.deepEqual(a,b);assert.ok(a.score>=0&&a.score<=100);assert.equal(a.metrics.length,4);assert.ok(a.recommendations.length>=3)}})
test('higher operating pressure lowers the first scenario score',()=>{assert.ok(runSimulation(project.scenarios[0].id,10).score>runSimulation(project.scenarios[0].id,90).score)})
test('unknown scenarios safely fall back',()=>{assert.equal(runSimulation('does-not-exist').scenarioId,project.scenarios[0].id)})
