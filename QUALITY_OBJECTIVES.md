# Quality Objectives — pacus

**Version**: 1.0  
**Effective Date**: 2026-05-01  
**Review Date**: 2026-11-01  

## Objective 1: Achieve 100% Schema Guard Coverage

**Description**: Ensure every database constraint (CHECK, UNIQUE, trigger) is verified by automated mutation tests.

**Measurable Target**:
- 100% of schema guards have corresponding mutation tests in `tests/test_mutations.py`
- Zero untested triggers or constraints

**Relevant to**:
- Customer satisfaction (data integrity)
- Conformity to requirements (ISO 9001 Clause 8.5.1)

**Monitoring**:
- Metric: `mutation_test_count / schema_guard_count * 100%`
- Method: Review `test_mutations.py` MUTATIONS list vs. schema triggers
- Frequency: Every sprint (2 weeks)

**Responsible**: Development Team  
**Timeline**: Ongoing — maintain 100% coverage  
**Evaluation Method**: Automated test run with coverage report

---

## Objective 2: Maintain < 5% Test Failure Rate

**Description**: Keep the automated test suite passing with minimal flakiness or regressions.

**Measurable Target**:
- < 5% test failure rate on `main`/`f/std` branches
- Zero tolerated failures on critical path (schema, import, audit)

**Relevant to**:
- QMS effectiveness
- Continual improvement (Clause 10.3)

**Monitoring**:
- Metric: `(failed_tests / total_tests) * 100%`
- Method: CI/CD pipeline test results
- Frequency: Every commit (automated)

**Responsible**: Development Team, QA  
**Timeline**: Ongoing  
**Evaluation Method**: CI/CD dashboard review

---

## Objective 3: Resolve Nonconformities Within 5 Business Days

**Description**: Identify, correct, and prevent recurrence of nonconformities in code, schema, or processes.

**Measurable Target**:
- 95% of nonconformities resolved within 5 business days
- 100% of critical nonconformities resolved within 2 business days

**Relevant to**:
- Corrective action (Clause 10.2)
- Customer satisfaction

**Monitoring**:
- Metric: `nonconformities_resolved_within_SLA / total_nonconformities * 100%`
- Method: Issue tracker SLA compliance report
- Frequency: Monthly

**Responsible**: Development Team, QA  
**Timeline**: Ongoing  
**Evaluation Method**: Monthly review of issue tracker metrics

---

## Objective 4: Achieve ISO 9001:2015 Compliance Rating of "Conformant"

**Description**: Close all identified gaps in ISO 9001:2015 clause compliance.

**Measurable Target**:
- Zero 🔴 Gap ratings in ISO 9001 audit checklist
- Zero 🟡 Partial ratings — all clauses rated ✅ Conformant
- Complete documented information per Clause 7.5

**Relevant to**:
- Certification readiness
- QMS conformity (Clause 4.4)

**Monitoring**:
- Metric: Self-audit checklist completion (see `iso-software-skills/skills/iso-9001/ISO-9001_SKILL.md`)
- Method: Quarterly self-audit using ISO 9001 verification checklist
- Frequency: Every 3 months

**Responsible**: Top Management, QA  
**Timeline**: Complete by 2026-08-01  
**Evaluation Method**: Quarterly internal audit with documented results

---

## Objective 5: Maintain 100% Audit Trail Integrity

**Description**: Ensure all status changes, audit events, and critical operations are recorded in append-only logs.

**Measurable Target**:
- 100% of `work_act` status changes recorded in `work_act_status_history`
- 100% of `project` status changes recorded in `project_status_history`
- 100% of critical operations recorded in `audit_event`
- Zero successful UPDATE or DELETE operations on history/audit tables

**Relevant to**:
- Traceability (Clause 8.5.2)
- Control of nonconforming outputs (Clause 8.7)

**Monitoring**:
- Metric: `append_only_violations_detected`
- Method: Automated tests in `test_db_schema.py` (TestAppendOnlyHistory, TestProjectStatusHistoryAppendOnly)
- Frequency: Every test run

**Responsible**: DBA, Development Team  
**Timeline**: Ongoing  
**Evaluation Method**: Test suite execution + manual review of audit tables

---

## Communication & Updates

- Objectives are communicated to all team members via this document
- Progress is reviewed during management review (Clause 9.3)
- Objectives are updated as appropriate based on:
  - Changes in organizational context
  - Customer feedback
  - Audit results
  - Performance evaluation outcomes

---

*Next scheduled review: 2026-11-01*
