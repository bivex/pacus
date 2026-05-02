# Context of Use Description — pacus HTML Artifacts

**Version**: 1.0  
**Effective Date**: 2026-05-01  
**Standard**: ISO 9241-210:2010 Clause 6.2  

## 1. User Groups and Goals

### 1.1 Primary Users: Project Managers / Accountants

**Description**: Personnel responsible for tracking work acts, projects, and generating printable documents for internal use or client delivery.

**Goals**:
- Generate printable work act documents (HTML → PDF → print)
- View project status and work act history
- Access audit trails for compliance verification
- Navigate between related documents (project ↔ acts ↔ journal)

**Constraints**:
- May have varying levels of technical proficiency
- Need documents in Russian language (localization)
- Require quick access to print functionality

---

### 1.2 Secondary Users: Auditors / Compliance Officers

**Description**: Personnel who verify work act correctness, check audit trails, and ensure regulatory compliance.

**Goals**:
- Review audit trails for work acts and projects
- Verify status transition history
- Confirm document immutability and integrity
- Export/print audit documentation

**Constraints**:
- Need clear, structured information presentation
- Require traceability links between documents
- Must access historical data quickly

---

### 1.3 Tertiary Users: System Administrators

**Description**: Personnel managing the pacus system, configuring print server, and maintaining artifact generation.

**Goals**:
- Verify artifact generation works correctly
- Monitor print server (localhost:4000)
- Troubleshoot artifact rendering issues

**Constraints**:
- Technical proficiency high
- Need system-level diagnostics

---

## 2. User Characteristics

### 2.1 Knowledge & Skills

| Characteristic | Description |
|---------------|-------------|
| Technical skills | Varies from basic (project managers) to advanced (system admins) |
| Domain knowledge | Familiar with work acts, project management, accounting |
| Language | Russian-speaking (interface in Russian) |
| Browser usage | Familiar with standard browsers (Chrome, Firefox, Safari) |
| Printing | Familiar with browser print function |

### 2.2 Capabilities & Limitations

| Capability/Limitation | Details |
|----------------------|---------|
| Visual acuity | Assumed normal; high-contrast UI provided |
| Motor skills | Standard mouse/keyboard interaction |
| Cognitive load | Information structured in tables for easy scanning |
| Time constraints | Need quick access to documents (print within 2-3 clicks) |

### 2.3 User Preferences

- Prefer printable formats (A4 paper size)
- Need currency display flexibility (USD, EUR, RUB, GBP)
- Want clear navigation between related documents
- Prefer minimal UI (focus on content, not decoration)

---

## 3. Tasks

### 3.1 Primary Tasks

| Task | Frequency | Duration | Interdependencies |
|------|-----------|----------|------------------|
| Generate project card HTML | Daily | 1-2 minutes | Requires project in DB |
| Print work act document | Daily | 2-3 minutes | Requires act with HTML revision |
| Review audit trail | Weekly | 5-10 minutes | Requires act with status history |
| Navigate between related docs | Daily | 30 seconds | Links in HTML artifacts |
| Change currency display | Rarely | 10 seconds | Client-side JS |

### 3.2 Task Workflow Example

1. User opens Print Center (index.html)
2. User clicks on project card link
3. User views project card with acts list
4. User clicks on work act HTML link
5. User clicks "Print" button or uses Ctrl+P
6. User optionally views audit trail via "Аудит" link

### 3.3 Health & Safety Risks

| Risk | Mitigation |
|------|-------------|
| Eye strain from prolonged screen use | High-contrast UI, clear typography |
| Repetitive strain from mouse use | Minimal clicks required (2-3 to print) |
| Stress from difficult navigation | Clear breadcrumbs, consistent layout |

---

## 4. Environments

### 4.1 Technical Environment

| Aspect | Description |
|--------|-------------|
| Hardware | Desktop/laptop with monitor (minimum 1024px width) |
| Software | Modern web browser (Chrome, Firefox, Safari, Edge) |
| Network | Localhost:4000 (print server) or static file access |
| Output | Browser print to PDF or physical printer (A4) |

### 4.2 Physical Environment

| Aspect | Description |
|--------|-------------|
| Location | Office environment |
| Lighting | Standard office lighting (no glare on screen assumed) |
| Noise | Standard office noise levels |
| Workspace | Desk with monitor, keyboard, mouse |

### 4.3 Social & Cultural Environment

| Aspect | Description |
|--------|-------------|
| Language | Russian (documents, UI text) |
| Currency | Multiple (USD, EUR, RUB, GBP) depending on contract |
| Business culture | Formal document presentation expected |
| Regulatory | Russian accounting standards, audit compliance |

---

## 5. Equipment (Hardware/Software)

### 5.1 System Components

| Component | Specifications |
|-----------|-----------------|
| Browser | HTML5, CSS3, JavaScript enabled |
| Print server | Python HTTP server on localhost:4000 |
| Artifacts | Static HTML files with embedded CSS/JS |
| Database | SQLite (data source for generation) |

### 5.2 Performance Requirements

- HTML generation: < 1 second per artifact
- Page load: < 2 seconds on localhost
- Print rendering: < 3 seconds in browser

---

## 6. Update History

| Date | Version | Changes |
|------|---------|---------|
| 2026-05-01 | 1.0 | Initial context of use description |

---

*Next review date: 2026-11-01*
