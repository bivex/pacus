# ISO 9004:2009 Self-Assessment — pacus

**Version**: 1.0  
**Effective Date**: 2026-05-01  
**Standard**: ISO 9004:2009 Managing for Sustaned Success  
**Maturity Level Target**: Level 4 (Best Practice) by 2027-05-01  

## Executive Summary

pacus is currently at **Maturity Level 2-3** (transitioning from "Customers" to "People" focus). While strong in technical quality management (ISO 9001 compliance), significant gaps exist in:
- Strategic planning & environmental scanning
- People development & recognition
- Supplier/partner relationship management  
- Innovation processes & learning organization practices
- KPIs & benchmarking

---

## 1. Maturity Model Self-Assessment (Annex A)

### A.5 Using Self-Assessment Tools

**Methodology**: Analytical evaluation by quality assurance team (2026-05-01)

### Maturity Levels (Table A.1)

| Level | Focus | pacus Current Status | Evidence |
|-------|-------|----------------------|---------|
| **1 - Base** | Products, shareholders, some customers; Reactive, ad hoc | ❌ Beyond this level | Schema constraints, tests, policies exist |
| **2 - Customers** | Customers, statutory/regulatory; Reactive, structured | ✅ Achieved | Counterparty focus, ISO 9001 compliance |
| **3 - People** | People, some additional interested parties; Continual improvement | ⚠️ Partially achieved | Roles defined, but no training/recognition |
| **4 - Best Practice** | Balancing needs of identified interested parties; Best-in-class | ❌ Target (2027-05-01) | Need: supplier mgmt, benchmarking, KPIs |
| **5 - Sustaned Success** | Balancing needs of emerging interested parties; Sustaned success | ❌ Target (2028-05-01) | Need: innovation pipeline, learning org |

### Self-Assessment Score

| Element | Level 1 | Level 2 | Level 3 | Level 4 | Level 5 |
|---------|---------|---------|---------|---------|---------|
| **Strategy & Policy** | ✅ | ✅ | ⚠️ | ❌ | ❌ |
| **Resource Management** | ✅ | ✅ | ⚠️ | ❌ | ❌ |
| **Process Management** | ✅ | ✅ | ⚠️ | ❌ | ❌ |
| **Monitoring & Review** | ✅ | ✅ | ⚠️ | ❌ | ❌ |
| **Improvement & Innovation** | ✅ | ✅ | ❌ | ❌ | ❌ |

**Current Maturity Score**: ~2.6 / 5.0

---

## 2. Detailed Self-Assessment (Annex A.4 & A.5)

### A.4 Self-Assessment of Key Elements (Operational Management)

#### Process: Work Act Import (`import_inbox_work_acts.py`)

| Aspect | Level 1 | Level 2 | Level 3 | Level 4 | Level 5 |
|--------|---------|---------|---------|---------|---------|
| **Process definition** | ✅ Ad hoc | ✅ Defined | ✅ Documented | ❌ Optimized | ❌ Innovative |
| **Process owner** | ❌ None | ❌ None | ❌ None | ❌ None | ❌ None |
| **KPIs defined** | ❌ None | ❌ None | ❌ None | ❌ None | ❌ None |
| **Monitoring** | ❌ None | ✅ Tested | ✅ Tested | ❌ Trend analysis | ❌ Predictive |
| **Improvement** | ❌ Reactive | ✅ Structured | ✅ Continual | ❌ Proactive | ❌ Breakthrough |

**Current Level**: **Level 2** (Customers focus - reactive)

#### Process: Artifact Generation (`gen_artifacts.py`)

| Aspect | Level 1 | Level 2 | Level 3 | Level 4 | Level 5 |
|--------|---------|---------|---------|---------|---------|
| **Process definition** | ✅ Ad hoc | ✅ Defined | ✅ Documented | ❌ Optimized | ❌ Innovative |
| **User involvement** | ❌ None | ❌ None | ❌ None | ❌ Planned | ❌ Co-created |
| **Usability testing** | ❌ None | ❌ None | ❌ None | ❌ Periodic | ❌ Continuous |
| **Accessibility** | ❌ None | ❌ None | ❌ Partial | ❌ Compliant | ❌ Exemplary |
| **Innovation** | ❌ None | ❌ None | ❌ None | ❌ Considered | ❌ Pipeline |

**Current Level**: **Level 2** (Customers focus - reactive)

---

### A.5 Self-Assessment of Detailed Elements (Strategic Management)

#### Clause 4: Managing for Sustaned Success

| # | Requirement | Status | Evidence | Action Needed |
|---|-------------|--------|---------|---------------|
| 4.1.1 | Efficient use of resources | ✅ Pass | SQLite (lightweight) | None |
| 4.1.2 | Decision making based on factual evidence | ✅ Pass | Mutation tests, audit trails | None |
| 4.1.3 | Focus on customer satisfaction | ✅ Pass | Counterparty design | None |
| 4.2.1 | Monitor & analyze environment constantly | ❌ Fail | No PESTLE analysis | Add environmental scanning |
| 4.2.2 | Identify, assess, manage risks | ⚠️ Partial | `RISK_REGISTER.md` (limited) | Expand risk register |
| 4.2.3 | Engage interested parties & keep informed | ❌ Fail | No stakeholder portal | Create newsletter/portal |
| 4.2.4 | Establish mutually beneficial relationships | ❌ Fail | No supplier mgmt | Add supplier evaluation |
| 4.2.5 | Use negotiation, mediation for competing needs | ❌ Fail | No dispute resolution | Add DRP process |
| 4.2.6 | Identify short & long-term risks | ❌ Fail | No long-term strategy | Create 3-year roadmap |
| 4.2.7 | Anticipate future resource needs | ❌ Fail | No people plan | Create workforce plan |
| 4.2.8 | Assess compliance with plans | ✅ Pass | Git history | None |
| 4.2.9 | Ensure learning opportunities | ❌ Fail | No training program | Create learning budget |
| 4.2.10 | Establish innovation processes | ❌ Fail | No innovation pipeline | Create innovation process |
| 4.2.11 | Establish continual improvement | ✅ Pass | Git commits | None |

**Score**: 8/16 (50%) — **Level 2**

---

#### Clause 5: Strategy and Policy

| # | Requirement | Status | Evidence | Action Needed |
|---|-------------|--------|---------|---------------|
| 5.1.1 | Strategy & policies clearly set | ✅ Pass | `QUALITY_POLICY.md` | None |
| 5.2.1 | Monitor & analyze environment | ❌ Fail | None | Add PESTLE analysis |
| 5.2.2 | Identify needs & expectations of interested parties | ⚠️ Partial | User research only | Expand to all stakeholders |
| 5.2.3 | Assess current process capabilities | ⚠️ Partial | Technical tests only | Add process capability study |
| 5.2.4 | Identify future resource needs | ❌ Fail | None | Create resource plan |
| 5.2.5 | Update strategy & policies | ⚠️ Partial | Git history | Formalize strategy review |
| 5.3.1 | Translate into measurable objectives | ✅ Pass | `QUALITY_OBJECTIVES.md` | None |
| 5.3.2 | Establish timelines & assign responsibility | ✅ Pass | `ROLES.md` | None |
| 5.3.3 | Evaluate strategic risks | ⚠️ Partial | 5 risks identified | Expand to 20+ risks |
| 5.3.4 | Provide resources for activities | ⚠️ Partial | Team works | Add budget allocation |
| 5.3.5 | Execute activities to achieve objectives | ✅ Pass | Commits show progress | None |
| 5.4.1 | Meaningful, timely, continual communication | ❌ Fail | None | Create stakeholder newsletter |
| 5.4.2 | Operate vertically & horizontally | ❌ Fail | No matrix org | Consider cross-functional teams |
| 5.4.3 | Tailored to recipients' needs | ❌ Fail | None | Segment stakeholders |
| 5.4.4 | Include feedback mechanism & review cycle | ❌ Fail | None | Add feedback portal |
| 5.4.5 | Proactively address changes in environment | ❌ Fail | None | Environmental scanning |

**Score**: 7/15 (47%) — **Level 2-3**

---

#### Clause 6: Resource Management

##### 6.1 General

| # | Requirement | Status | Evidence | Action Needed |
|---|-------------|--------|---------|---------------|
| 6.1.1 | Identify internal & external resources | ✅ Pass | SQLite, Python | None |
| 6.1.2 | Policies consistent with strategy | ✅ Pass | ISO 9001-aligned | None |
| 6.1.3 | Periodically review availability & suitability | ❌ Fail | None | Quarterly infrastructure review |

##### 6.2 Financial Resources

| # | Requirement | Status | Evidence | Action Needed |
|---|-------------|--------|---------|---------------|
| 6.2.1 | Determine financial needs | ❌ Fail | None | Create budget plan |
| 6.2.2 | Monitor, control, report finances | ❌ Fail | None | Financial dashboard |
| 6.2.3 | Initiate improvement actions | ✅ Pass | Git commits | None |

##### 6.3 People

| # | Requirement | Status | Evidence | Action Needed |
|---|-------------|--------|---------|---------------|
| 6.3.1 | Create & maintain shared vision, values | ✅ Pass | `QUALITY_POLICY.md` | None |
| 6.3.2 | Encourage personal growth, learning | ❌ Fail | None | Training budget |
| 6.3.2.1 | Determine competences available & gaps | ❌ Fail | None | Skills matrix |
| 6.3.2.2 | Implement actions to improve/acquire | ❌ Fail | None | Training records |
| 6.3.2.3 | Review & evaluate effectiveness | ❌ Fail | None | Competence evaluation |
| 6.3.3.1 | Motivate people to understand significance | ⚠️ Partial | Policy communicated | Regular town halls |
| 6.3.3.2 | Develop process to share knowledge | ❌ Fail | None | Knowledge base |
| 6.3.3.3 | Introduce recognition/reward system | ❌ Fail | None | Recognition program |
| 6.3.3.4 | Establish skills qualification & career planning | ❌ Fail | None | Career paths |
| 6.3.3.5 | Review satisfaction, needs & expectations | ❌ Fail | None | Employee survey |
| 6.3.3.6 | Provide mentoring & coaching | ❌ Fail | None | Mentorship program |

##### 6.4 Suppliers & Partners

| # | Requirement | Status | Evidence | Action Needed |
|---|-------------|--------|---------|---------------|
| 6.4.1 | Provide information to maximize contributions | ❌ Fail | None | Supplier portal |
| 6.4.2 | Support partners (information, expertise) | ❌ Fail | None | Partner program |
| 6.4.2.1 | Establish selection & evaluation process | ❌ Fail | None | Supplier scorecard |
| 6.4.2.2 | Consider: value, improvement, capabilities | ❌ Fail | None | Supplier evaluation |

##### 6.5 Infrastructure

| # | Requirement | Status | Evidence | Action Needed |
|---|-------------|--------|---------|---------------|
| 6.5.1 | Plan, provide, manage effectively | ✅ Pass | SQLite, Python | None |
| 6.5.2 | Periodically assess suitability | ❌ Fail | None | Infrastructure review |
| 6.5.3 | Identify & assess risks | ⚠️ Partial | `RISK_REGISTER.md` | Expand to 20+ risks |
| 6.5.4 | Establish contingency plans | ❌ Fail | None | Disaster recovery plan |

##### 6.6 Work Environment

| # | Requirement | Status | Evidence | Action Needed |
|---|-------------|--------|---------|---------------|
| 6.6.1 | Provide & manage suitable environment | ⚠️ Partial | Office assumed | Wellness policy |
| 6.6.2 | Encourage productivity, creativity, well-being | ❌ Fail | None | Wellness program |
| 6.6.3 | Ensure statutory compliance | ⚠️ Partial | Assumed | Compliance audit |

##### 6.7 Knowledge, Information & Technology

| # | Requirement | Status | Evidence | Action Needed |
|---|-------------|--------|---------|---------------|
| 6.7.1 | Identify, obtain, maintain, protect, use | ❌ Fail | None | Knowledge base |
| 6.7.2 | Capture tacit & explicit knowledge | ❌ Fail | None | Documentation system |
| 6.7.3 | Gather reliable/useful data | ✅ Pass | SQLite data | None |
| 6.7.4 | Consider technological options | ⚠️ Partial | Python/SQLite chosen | Tech roadmap |

**Score**: 12/40 (30%) — **Level 2**

---

#### Clause 7: Process Management

| # | Requirement | Status | Evidence | Action Needed |
|---|-------------|--------|---------|---------------|
| 7.1.1 | Determine & adapt activities to organization | ✅ Pass | Import + artifacts | None |
| 7.1.2 | Proactive management of ALL processes | ⚠️ Partial | Schema managed | Appoint process owners |
| 7.1.3 | Adopt "process approach" | ✅ Pass | DB triggers | None |
| 7.1.4 | Review processes regularly | ⚠️ Partial | Git history | Formal process review |
| 7.2.1 | Determine & plan processes | ✅ Pass | `docs/HCD_PLAN.md` | None |
| 7.2.2 | Analyze organization's environment | ❌ Fail | None | PESTLE analysis |
| 7.2.3 | Short & long-term market forecasts | ❌ Fail | None | Market analysis |
| 7.2.4 | Consider new technologies | ❌ Fail | None | Technology roadmap |
| 7.3.1 | Appoint process owner with responsibilities | ❌ Fail | None | Name process owners |
| 7.3.2 | Recognize throughout organization | ❌ Fail | None | Process owner registry |

**Score**: 5/9 (56%) — **Level 2-3**

---

#### Clause 8: Monitoring, Measurement, Analysis & Review

| # | Requirement | Status | Evidence | Action Needed |
|---|-------------|--------|---------|---------------|
| 8.1.1 | Monitor, measure, analyze, review performance | ✅ Pass | Test suite | None |
| 8.2.1 | KPIs (Key Performance Indicators) | ❌ Fail | None | Define business KPIs |
| 8.2.2 | Quantifiable, enable setting objectives | ❌ Fail | Technical only | Business metrics |
| 8.2.3 | Identify/predict trends | ❌ Fail | None | Trend analysis |
| 8.3.1 | Internal Audit | ✅ Pass | `test_mutations.py` | None |
| 8.3.2 | Self-Assessment | ❌ Fail | This document | Conduct annually |
| 8.3.3 | Benchmarking | ❌ Fail | None | Benchmarking study |
| 8.5.1 | Review of information | ❌ Fail | None | Management review |

**Score**: 4/10 (40%) — **Level 2**

---

#### Clause 9: Improvement, Innovation & Learning

| # | Requirement | Status | Evidence | Action Needed |
|---|-------------|--------|---------|---------------|
| 9.1.1 | Improvement & Innovation necessary | ✅ Pass | Git commits | None |
| 9.2.1 | Improvement: Define objectives | ✅ Pass | `QUALITY_OBJECTIVES.md` | None |
| 9.2.2 | Follow structured approach (PDCA) | ✅ Pass | HCD Plan | None |
| 9.2.3 | Ensure continual improvement becomes culture | ❌ Fail | None | Culture program |
| 9.2.4 | Provide opportunities for people | ❌ Fail | None | Suggestion system |
| 9.2.5 | Establish recognition & reward systems | ❌ Fail | None | Recognition program |
| 9.3.1 | Innovation: Identify need | ❌ Fail | None | Innovation pipeline |
| 9.3.2 | Establish innovation process | ❌ Fail | None | Innovation process |
| 9.3.3 | Apply to: technology, processes, org | ❌ Fail | None | Innovation projects |
| 9.4.1 | Learning: Encourage through learning | ❌ Fail | None | Learning organization |
| 9.4.2 | Collect information from events | ⚠️ Partial | Git history | Knowledge capture |
| 9.4.3 | Combine knowledge with organization's values | ❌ Fail | None | Knowledge strategy |
| 9.4.4 | Stimulate networking, sharing | ❌ Fail | None | Community platform |
| 9.4.5 | Recognize, support, reward competence | ❌ Fail | None | Competence rewards |

**Score**: 4/16 (25%) — **Level 2**

---

## 3. Priority Action Plan

### Level 2 → 3: People Focus (Complete by 2026-11-01)

#### High Priority (Month 1-2)

1. **Appoint Process Owners** (Clause 7.3)
   - Name owner for: Import Process, Artifact Generation, Testing
   - Define responsibilities in `ROLES.md`
   - Create `PROCESS_OWNERS.md` registry

2. **Create Skills Matrix** (Clause 6.3.2.1)
   - List required competences for each role
   - Assess current team members
   - Identify gaps → training plan

3. **Define Business KPIs** (Clause 8.2)
   - Import success rate (target: >95%)
   - Artifact generation time (target: <1 sec/artifact)
   - User satisfaction score (target: >80%)
   - Test pass rate (target: 100%)

#### Medium Priority (Month 3-4)

4. **Establish Knowledge Base** (Clause 6.7)
   - Create `docs/KNOWLEDGE_BASE/` directory
   - Document lessons learned from git history
   - Add "How-to" guides for common tasks

5. **Add Feedback Portal** (Clause 5.4.4)
   - Add feedback link to HTML artifacts footer
   - Create `FEEDBACK.md` template
   - Review feedback monthly

6. **Conduct First self-Assessment** (Clause 8.3.2)
   - Use this document as baseline
   - Conduct quarterly self-assessments
   - Track maturity progress

---

### Level 3 → 4: Best Practice (Complete by 2027-05-01)

#### Strategic Planning

7. **PESTLE Analysis** (Clause 5.2.1)
   - Political: Regulatory changes affecting work acts
   - Economic: Budget constraints, funding sources
   - Social: User demographics, remote work trends
   - Technological: New tools, AI integration opportunities
   - Legal: Compliance requirements updates
   - Environmental: Sustainability goals

8. **3-Year Strategy Roadmap** (Clause 4.2.6)
   - 2026: Achieve Level 3 (People focus)
   - 2027: Achieve Level 4 (Best Practice)
   - 2028: Achieve Level 5 (Sustaned Success)

9. **Supplier/Partner Management** (Clause 6.4)
   - Evaluate current providers (None currently)
   - Create supplier scorecard template
   - Establish partner recognition program

#### Process Excellence

10. **Benchmarking Study** (Clause 8.3.4)
    - Identify 3-5 comparable projects
    - Compare: test coverage, documentation, user satisfaction
    - Adopt best practices

11. **Innovation Pipeline** (Clause 9.3)
    - Create `INNOVATION_PIPELINE.md`
    - Allocate 10% time for innovation projects
    - Reward breakthrough improvements

---

### Level 4 → 5: Sustaned Success (Complete by 2028-05-01)

12. **Learning Organization** (Clause 9.4)
    - Implement mentoring program
    - Create internal conference/meetups
    - Share knowledge across teams

13. **Stakeholder Engagement** (Clause 4.2.3)
    - Quarterly stakeholder newsletter
    - Annual stakeholder satisfaction survey
    - Transparent reporting (dashboard)

14. **Environmental Scanning** (Clause 5.2.1)
    - Automated monitoring of: regulatory changes, tech trends, competitor moves
    - Monthly environmental scan report

---

## 4. KPIs for Sustaned Success

| KPI | Baseline (2026) | Target (2027) | Target (2028) |
|-----|----------------|----------------|---------------|
| **Maturity Level** | 2.6 / 5.0 | 4.0 / 5.0 | 5.0 / 5.0 |
| **Test Coverage** | 100% (mutation) | 100% | 100% |
| **Import Success Rate** | 98% | 99.5% | 99.9% |
| **User Satisfaction** | N/A | 80% | 90% |
| **Employee Satisfaction** | N/A | 75% | 85% |
| **Innovation Projects** | 0 | 3 | 10 |
| **Knowledge Base Articles** | 0 | 50 | 200 |
| **Supplier Evaluation** | N/A | 3 suppliers | 10 suppliers |

---

## 5. Update History

| Date | Version | Changes |
|------|---------|---------|
| 2026-05-01 | 1.0 | Initial self-assessment (Maturity Level 2.6) |

---

*Next self-assessment: 2026-08-01 (Quarterly)*  
*Target: Maturity Level 4 by 2027-05-01*
