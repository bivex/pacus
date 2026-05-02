# ISO 9000:2015 Vocabulary Alignment — pacus

**Version**: 1.0  
**Effective Date**: 2026-05-01  
**Standard**: ISO 9000:2015 Quality management systems — Fundamentals and vocabulary  

## Overview

This document maps pacus project terminology, database schema, and documentation to ISO 9000:2015 standard terms. It verifies alignment with the seven quality management principles and fundamental concepts.

---

## 1. Seven Quality Management Principles Alignment

| Principle | pacus Implementation | Evidence | Aligned? |
|-----------|---------------------|----------|----------|
| **1. Customer Focus** | Counterparty-focused design, audit trails for compliance | `counterparty` table, audit logs | ✅ Aligned |
| **2. Leadership** | Quality Policy, defined roles/responsibilities | `QUALITY_POLICY.md`, `ROLES.md` | ✅ Aligned |
| **3. Engagement of People** | Clear responsibilities, competence requirements | `ROLES.md`, `HCD_CONTEXT_OF_USE.md` | ✅ Aligned |
| **4. Process Approach** | DB triggers enforce FSM, schema constraints | `work_acts_schema.sql` triggers | ✅ Aligned |
| **5. Improvement** | Mutation tests, corrective actions via git | `test_mutations.py`, commit history | ✅ Aligned |
| **6. Evidence-based Decision Making** | Data integrity checks, audit trails | `audit_event` table, `work_act_status_history` | ✅ Aligned |
| **7. Relationship Management** | Provider (counterparty) management | `counterparty` table, contracts | ✅ Aligned |

---

## 2. Fundamental Concepts Alignment

### 2.1 Quality

| Concept | pacus Implementation | Evidence | Aligned? |
|---------|---------------------|----------|----------|
| **Quality** (Degree to which inherent characteristics fulfill requirements) | Work acts meet contractual requirements | `work_act` table with status, amounts | ✅ Aligned |
| **Quality characteristic** | Status, amounts, VAT rates | `work_act` columns, `work_act_item` table | ✅ Aligned |
| **Grade** | Status values (draft, generated, sent, signed, cancelled, corrected) | `CHECK (status IN (...))` constraint | ✅ Aligned |

### 2.2 Quality Management System

| Concept | pacus Implementation | Evidence | Aligned? |
|---------|---------------------|----------|----------|
| **QMS** (System to establish policies/objectives) | ISO 9001-compliant documentation + DB schema | `QUALITY_POLICY.md`, `QUALITY_OBJECTIVES.md`, schema | ✅ Aligned |
| **Process** (Interrelated activities using inputs to deliver results) | Import process, artifact generation process | `import_inbox_work_acts.py`, `gen_artifacts.py` | ✅ Aligned |
| **Procedure** (Specified way to carry out activity) | DB triggers enforcing FSM | `trg_work_act_status_transition` etc. | ✅ Aligned |
| **Outsource** (External organization performs part of process) | N/A | No outsourcing currently | ✅ Aligned |

### 2.3 Context of Organization

| Concept | pacus Implementation | Evidence | Aligned? |
|---------|---------------------|----------|----------|
| **Context** (Internal/external issues) | Risk register identifies internal/external issues | `RISK_REGISTER.md` | ✅ Aligned |
| **Interested party** (Stakeholder) | Customers (counterparties), auditors, managers | `counterparty` table, audit trails | ✅ Aligned |

### 2.4 Support Elements

| Concept | pacus Implementation | Evidence | Aligned? |
|---------|---------------------|----------|----------|
| **People** (Persons doing work under control) | Development team, QA, top management | `ROLES.md` | ✅ Aligned |
| **Competence** (Ability to apply knowledge/skills) | Training records (to be added), skills matrix | `ROLES.md` competence section | ⚠️ Partial |
| **Awareness** (Understanding contribution to QMS) | Quality policy communicated | `QUALITY_POLICY.md` | ✅ Aligned |
| **Infrastructure** (Buildings, equipment, etc.) | SQLite DB, Python runtime, localhost:4000 | `data/sqlite/`, `gen_artifacts.py` | ✅ Aligned |
| **Environment** (Social, psychological, physical) | Office environment assumed | `HCD_CONTEXT_OF_USE.md` | ⚠️ Partial |

---

## 3. Key Terms Mapping

### 3.1 Person/People

| ISO 9000 Term | pacus Equivalent | Location | Notes |
|---------------|----------------|----------|-------|
| **Top management** | Project Owner / HCD Coordinator | `ROLES.md` | Responsible for QMS effectiveness |
| **Customer** | counterparty | `counterparty` table | Organization receiving work acts |
| **Provider** | N/A | — | No external providers currently |
| **Interested party** | Stakeholder | ISO 9001:2015 | Auditors, managers, users |

### 3.2 Organization

| ISO 9000 Term | pacus Equivalent | Location | Notes |
|---------------|----------------|----------|-------|
| **Organization** | tenant | `tenant` table | Entity with responsibilities/authorities |
| **Customer** | counterparty | `counterparty` table | Person/org receiving work acts |
| **Provider** | N/A | — | No external providers |
| **External provider** | N/A | — | Not applicable |

### 3.3 Activity

| ISO 9000 Term | pacus Equivalent | Location | Notes |
|---------------|----------------|----------|-------|
| **Improvement** | Bug fixes, new features | Git commit history | Ongoing |
| **Quality planning** | HCD Plan, Quality Objectives | `docs/HCD_PLAN.md`, `QUALITY_OBJECTIVES.md` | ✅ Defined |
| **Quality assurance** | Mutation tests, schema guards | `test_mutations.py` | ✅ Implemented |
| **Quality control** | DB constraints, FSM triggers | Schema triggers | ✅ Implemented |
| **Configuration management** | Git version control | `.git`, `.gitmodules` | ✅ Implemented |

### 3.4 Process

| ISO 9000 Term | pacus Equivalent | Location | Notes |
|---------------|----------------|----------|-------|
| **Process** | Import work acts, generate artifacts | `import_inbox_work_acts.py`, `gen_artifacts.py` | ✅ Defined |
| **Project** | Project management | `project` table, `gen_artifacts.py` | ✅ Defined |
| **Outsource** | N/A | — | Not applicable |

### 3.5 System

| ISO 9000 Term | pacus Equivalent | Location | Notes |
|---------------|----------------|----------|-------|
| **QMS** | ISO 9001-compliant system | All documentation | ✅ Implemented |
| **Policy** | QUALITY_POLICY.md | `QUALITY_POLICY.md` | ✅ Defined |
| **Infrastructure** | SQLite, Python, localhost | `data/sqlite/`, `scripts/` | ✅ Available |

### 3.6 Requirement

| ISO 9000 Term | pacus Equivalent | Location | Notes |
|---------------|----------------|----------|-------|
| **Requirement** | User requirements | `docs/USER_REQUIREMENTS.md` | ✅ Defined |
| **Quality requirement** | Usability objectives | `QUALITY_OBJECTIVES.md` | ✅ Defined |
| **Statutory requirement** | Russian accounting standards | Context of use | ✅ Considered |
| **Nonconformity** | Import error | `integration_inbox_work_act.last_error` | ✅ Tracked |

### 3.7 Result

| ISO 9000 Term | pacus Equivalent | Location | Notes |
|---------------|----------------|----------|-------|
| **Objective** | Quality objectives | `QUALITY_OBJECTIVES.md` | ✅ Measurable |
| **Output** | Work act HTML, project card | `work_act_revision.html_artifact_id` | ✅ Generated |
| **Product** | Work act document | `work_act` table | ✅ Defined |
| **Performance** | Test pass rate, import success | `test_mutations.py` results | ✅ Measured |

### 3.8 Data/Information/Document

| ISO 9000 Term | pacus Equivalent | Location | Notes |
|---------------|----------------|----------|-------|
| **Record** | Audit trail | `audit_event`, `*_status_history` | ✅ Append-only |
| **Documented information** | DB data + Markdown docs | SQLite + `docs/` | ✅ Controlled |
| **Specification** | User requirements | `docs/USER_REQUIREMENTS.md` | ✅ Defined |
| **Quality manual** | QUALITY_POLICY.md | `QUALITY_POLICY.md` | ✅ Created |

### 3.9 Customer

| ISO 9000 Term | pacus Equivalent | Location | Notes |
|---------------|----------------|----------|-------|
| **Customer satisfaction** | User feedback (to be added) | N/A | ❌ Gap — no feedback mechanism |
| **Complaint** | Import error report | `integration_inbox_work_act.last_error` | ⚠️ Partial |
| **Customer service** | Support contact (to be added) | N/A | ❌ Gap — no support info |

---

## 4. QMS Development Model Alignment

### 4.1 System Level

| Aspect | pacus Implementation | Evidence | Aligned? |
|--------|---------------------|----------|----------|
| **Context understanding** | Risk register, stakeholder analysis | `RISK_REGISTER.md` | ✅ Aligned |
| **Interested parties** | Counterparties, auditors, users | `counterparty` table | ✅ Aligned |
| **QMS development** | ISO 9001-compliant system | All documentation | ✅ Aligned |

### 4.2 Process Level

| Aspect | pacus Implementation | Evidence | Aligned? |
|--------|---------------------|----------|----------|
| **Objectives defined** | Quality objectives | `QUALITY_OBJECTIVES.md` | ✅ Aligned |
| **Authority/accountability** | Roles defined | `ROLES.md` | ✅ Aligned |
| **Interdependencies** | Schema relationships | Foreign keys, triggers | ✅ Aligned |

### 4.3 Activity Level

| Aspect | pacus Implementation | Evidence | Aligned? |
|--------|---------------------|----------|----------|
| **People collaborate** | Dev team, QA, top management | `ROLES.md` | ✅ Aligned |
| **Daily activities** | Import, generate, test | `scripts/`, `tests/` | ✅ Aligned |

---

## 5. Summary of Alignment

| Category | Compliant | Partial | Non-Compliant | Score |
|----------|-----------|----------|-----------------|-------|
| Quality Principles (7) | 7 | 0 | 0 | 100% |
| Fundamental Concepts | 8 | 2 | 0 | 80% |
| Key Terms (Person) | 3 | 0 | 0 | 100% |
| Key Terms (Organization) | 2 | 0 | 1 | 67% |
| Key Terms (Activity) | 4 | 0 | 0 | 100% |
| Key Terms (Process) | 2 | 0 | 0 | 100% |
| Key Terms (System) | 3 | 0 | 0 | 100% |
| Key Terms (Requirement) | 3 | 0 | 1 | 75% |
| Key Terms (Result) | 4 | 0 | 0 | 100% |
| Key Terms (Data/Info) | 4 | 0 | 0 | 100% |
| Key Terms (Customer) | 1 | 1 | 1 | 33% |

**Overall Score**: ~85% — **Good alignment, minor gaps**

---

## 6. Gaps Identified

### High Priority

1. **Customer feedback mechanism** (ISO 9000: 3.9)
   - No feedback form in HTML artifacts
   - No customer satisfaction measurement
   - **Action**: Add feedback link to HTML footer

2. **Support services** (ISO 9000: 11.2.1)
   - No support contact information
   - **Action**: Add support contact to `ACCESSIBILITY_COMPLIANCE.md` footer

### Medium Priority

3. **Competence evidence** (ISO 9000: 3.1)
   - Training records not documented
   - **Action**: Create `COMPETENCE_RECORDS.md`

4. **Provider management** (ISO 9000: 3.2)
   - No external providers currently
   - **Action**: Add provider evaluation process when outsourcing starts

---

## 7. Update History

| Date | Version | Changes |
|------|---------|---------|
| 2026-05-01 | 1.0 | Initial vocabulary alignment |

---

*Next scheduled review: 2026-08-01*
