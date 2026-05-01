# Risk Register — pacus

**Version**: 1.0  
**Effective Date**: 2026-05-01  
**Review Date**: 2026-08-01  

## Risk Management Approach

pacus uses risk-based thinking (ISO 9001:2015 Clause 6.1) to identify, assess, and address risks and opportunities. This register documents:

- **Risks**: Negative effects that could impact QMS effectiveness or customer satisfaction
- **Opportunities**: Positive effects that could enhance desired outcomes

Actions are proportionate to the potential impact of risks and opportunities.

---

## Risk Matrix

| Likelihood | Impact | Score |
|------------|--------|-------|
| Rare (1)   | Minor (1) | 1 |
| Unlikely (2)| Moderate (2) | 2-4 |
| Possible (3)| Significant (3) | 5-9 |
| Likely (4) | Major (4) | 10-16 |
| Almost Certain (5) | Severe (5) | 17-25 |

**Action Thresholds**:
- **Score 15-25**: Immediate action required
- **Score 8-14**: Action planned within 30 days
- **Score 1-7**: Monitor, no immediate action needed

---

## Identified Risks

### R1: Database Corruption or Data Loss

**Risk ID**: R1  
**Category**: Operational  
**Description**: SQLite database becomes corrupted or data is lost due to hardware failure, software bug, or human error.

**Likelihood**: Unlikely (2)  
**Impact**: Severe (5)  
**Score**: 10 — **Action Required**

**Existing Controls**:
- Append-only audit trails (`work_act_status_history`, `audit_event`)
- Schema-enforced referential integrity (foreign keys, triggers)
- Busy timeout configured (`PRAGMA busy_timeout = 5000`)

**Planned Actions**:
1. Implement automated daily database backups
2. Document recovery procedure
3. Test backup restoration quarterly
4. Consider WAL mode for better crash recovery

**Responsible**: DBA  
**Timeline**: Complete by 2026-06-01  
**Effectiveness Evaluation**: Backup restoration test success rate (target: 100%)

---

### R2: Schema Guard Bypass or Removal

**Risk ID**: R2  
**Category**: Quality  
**Description**: A database constraint (CHECK, UNIQUE, trigger) is accidentally removed or bypassed, allowing invalid data.

**Likelihood**: Possible (3)  
**Impact**: Significant (3)  
**Score**: 9 — **Action Required**

**Existing Controls**:
- Mutation tests (`test_mutations.py`) verify each guard is necessary
- Version control prevents unauthorized schema changes
- Code review process for all schema changes

**Planned Actions**:
1. Maintain 100% mutation test coverage (Quality Objective 1)
2. Add CI/CD check that fails if mutation tests fail
3. Document all schema guards in `db/sqlite/README.md`

**Responsible**: Development Team, QA  
**Timeline**: Ongoing  
**Effectiveness Evaluation**: Mutation test pass rate (target: 100%)

---

### R3: Import Process Failure or Data Corruption

**Risk ID**: R3  
**Category**: Operational  
**Description**: `import_inbox_work_acts.py` fails during processing, corrupts data, or imports invalid records.

**Likelihood**: Possible (3)  
**Impact**: Significant (3)  
**Score**: 9 — **Action Required**

**Existing Controls**:
- Transaction handling (`BEGIN IMMEDIATE`, rollback on error)
- Validation in `normalize_items()` (quantity, price, VAT checks)
- Error recording in `integration_inbox_work_act.last_error`
- Retry mechanism (`--retry-errors` flag)

**Planned Actions**:
1. Add integration tests for import edge cases
2. Implement alerting for repeated import failures
3. Document import troubleshooting guide

**Responsible**: Development Team  
**Timeline**: Complete by 2026-07-01  
**Effectiveness Evaluation**: Import failure rate (target: < 2%)

---

### R4: Unauthorized Changes to Immutable Records

**Risk ID**: R4  
**Category**: Security/Quality  
**Description**: Immutable revisions or their artifacts are modified or deleted, compromising audit trail integrity.

**Likelihood**: Unlikely (2)  
**Impact**: Major (4)  
**Score**: 8 — **Action Planned**

**Existing Controls**:
- Triggers prevent UPDATE/DELETE on immutable revisions (`trg_work_act_revision_no_update_immutable`, etc.)
- Triggers prevent modification of linked artifacts (`trg_document_artifact_no_update_if_immutable`)

**Planned Actions**:
1. Document immutability rules for developers
2. Add automated test to verify immutability after every deploy
3. Consider database user permissions to enforce read-only on history tables

**Responsible**: DBA, Development Team  
**Timeline**: Complete by 2026-06-15  
**Effectiveness Evaluation**: Immutability test pass rate (target: 100%)

---

### R5: Regression Due to Insufficient Testing

**Risk ID**: R5  
**Category**: Quality  
**Description**: Code changes introduce bugs or regressions that aren't caught by existing tests.

**Likelihood**: Possible (3)  
**Impact**: Moderate (2)  
**Score**: 6 — **Monitor**

**Existing Controls**:
- Comprehensive test suite (`test_db_schema.py`, `test_mutations.py`)
- Code review process
- Staged development (draft → generated → sent → signed)

**Planned Actions**:
1. Maintain test coverage above 80%
2. Add E2E tests for artifact generation
3. Consider adding property-based testing for edge cases

**Responsible**: Development Team, QA  
**Timeline**: Ongoing  
**Effectiveness Evaluation**: Test coverage metrics (target: > 80%)

---

## Identified Opportunities

### O1: Automate Artifact Generation in CI/CD

**Opportunity ID**: O1  
**Description**: Generate HTML artifacts automatically on commit, reducing manual effort and ensuring artifacts are always up-to-date.

**Potential Benefit**: Faster delivery, reduced manual errors, always-current documentation.

**Planned Actions**:
1. Add `gen_artifacts.py` execution to CI/CD pipeline
2. Publish artifacts to static hosting or GitHub Pages
3. Validate generated HTML for correctness

**Responsible**: Development Team  
**Timeline**: Evaluate by 2026-07-01  

---

### O2: Enhance Monitoring & Alerting

**Opportunity ID**: O2  
**Description**: Implement proactive monitoring of database health, import success rates, and audit trail completeness.

**Potential Benefit**: Faster detection of issues, improved customer satisfaction, better QMS performance evaluation.

**Planned Actions**:
1. Define key performance indicators (KPIs)
2. Implement automated monitoring dashboard
3. Set up alerts for threshold breaches

**Responsible**: QA, DBA  
**Timeline**: Evaluate by 2026-08-01  

---

## Risk Review & Update

This register is reviewed:
- **Quarterly**: Full review of all risks and opportunities
- **After incidents**: Immediate review if a risk materializes
- **After changes**: When QMS or processes change significantly

Updates are communicated to relevant interested parties and integrated into QMS processes.

---

*Next scheduled review: 2026-08-01*
