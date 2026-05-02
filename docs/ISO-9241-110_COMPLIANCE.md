# ISO 9241-110:2006 Compliance Checklist — pacus HTML Artifacts

**Version**: 1.0  
**Effective Date**: 2026-05-01  
**Standard**: ISO 9241-110:2006 Ergonomics of human-system interaction — Dialogue principles  

## Overview

This document provides a compliance checklist for pacus HTML artifacts (project cards, work act documents, audit trails, journal entries) against the seven dialogue principles defined in ISO 9241-110:2006.

---

## 1. Suitability for the Task (Clause 4.3)

**Definition**: Interactive system supports user in completing the task (functionality & dialogue based on task characteristics, not technology).

### Recommendations Checklist

| # | Recommandation | Status | Evidence/Location |
|---|-------------------|--------|----------------------|
| 1.1 | Present information related to successful task completion | ✅ Pass | Project cards show acts, status, audit links |
| 1.2 | Avoid presenting unnecessary information | ✅ Pass | Clean layout, no clutter in generated HTML |
| 1.3 | Format input/output appropriate to task | ✅ Pass | Tables for structured data, A4 CSS for printing |
| 1.4 | Include necessary steps, avoid unnecessary steps | ✅ Pass | Navigate → view → print (2-3 clicks) |
| 1.5 | Compatible with source document characteristics | ✅ Pass | HTML generated from SQLite data via `gen_artifacts.py` |
| 1.6 | Channels for inputs/outputs appropriate to task | ⚠️ Partial | Visual display only (accessibility alternatives needed) |
| 1.7 | Design so interaction is apparent to user | ✅ Pass | Clear links (blue), print button styled |

### Examples from pacus

- **Time-critical**: Print button responds instantly (`window.print()`)
- **Currency**: Display precision suitable for currency (2 decimal digits via `fmt_amount()`)
- **Context**: "Печать" button clearly visible in `.topbar`

---

## 2. Self-descriptiveness (Clause 4.4)

**Definition**: At any time, obvious which dialogue user is in, where they are, what actions can be taken, how they can be performed.

### Recommendations Checklist

| # | Recommandation | Status | Evidence/Location |
|---|-------------------|--------|----------------------|
| 2.1 | Guide user through dialogue at each step | ✅ Pass | Clear h1/h2 headings, table structures |
| 2.2 | Minimize need to consult manuals/external info | ✅ Pass | Intuitive layout, standard web patterns |
| 2.3 | Keep informed about system status changes | ✅ Pass | Status badges displayed (draft, sent, signed) |
| 2.4 | Provide info on expected input format | N/A | Static HTML, no user input |
| 2.5 | Design so interaction is apparent | ✅ Pass | Links underlined, button styled with `.no-print` |
| 2.6 | Provide info on required formats/units | ⚠️ Partial | Currency symbol shown, but no explanation of units |

### Examples from pacus

- **Hotel reservation pattern**: "К списку" & "Печать" buttons guide through navigation
- **Clear labelling**: Project card titled "Проект {code} — {name}"
- **Status info**: Current status displayed prominently (e.g., "Статус: active")

---

## 3. Conformity with User Expectations (Clause 4.5)

**Definition**: Corresponds to predictable contextual needs of user and commonly accepted conventions.

### Recommendations Checklist

| # | Recommandation | Status | Evidence/Location |
|---|-------------------|--------|----------------------|
| 3.1 | Use vocabulary familiar to user / based on existing knowledge | ✅ Pass | Russian terms (Акт, Проект, Аудит, Статус) |
| 3.2 | Provide immediate & suitable feedback | ✅ Pass | Print button responds instantly |
| 3.3 | Reflect data structures/organization perceived as natural | ✅ Pass | Tables for lists, grid for details |
| 3.4 | Follow cultural & linguistic conventions | ✅ Pass | Russian date format (dd.mm.yyyy) |
| 3.5 | Format, length of feedback/explanation based on user needs | N/A | Static content |
| 3.6 | Behaviour & appearance consistent within/across similar tasks | ✅ Pass | Same layout across all artifacts |

### Examples from pacus

- **Banking app pattern**: Use "Акт" & "Проект" (not "Work Act" & "Project" for Russian users)
- **International users**: Date displayed as "01.03.2026" (Russian format)
- **E-commerce pattern**: Steps clearly indicated (project → acts → audit trail)
- **Department store pattern**: Information organized similar to physical documents

---

## 4. Suitability for Learning (Clause 4.6)

**Definition**: Supports & guides user in learning to use the system.

### Recommendations Checklist

| # | Recommandation | Status | Evidence/Location |
|---|-------------------|--------|----------------------|
| 4.1 | Make rules & underlying concepts available (tutorials) | ❌ Fail | No tutorial or help system provided |
| 4.2 | Provide appropriate support for infrequent use/relearning | ❌ Fail | No help text or tooltips |
| 4.3 | Feedback/explanations assist in building conceptual understanding | ❌ Fail | Static HTML, no interactive explanations |
| 4.4 | Provide sufficient feedback on intermediary/final results | N/A | No user actions to provide feedback on |
| 4.5 | Allow exploration ("try out") without negative consequences | ✅ Pass | Static HTML, safe to click links |
| 4.6 | Enable minimal learning (system supplies additional info on request) | ❌ Fail | No "?" icons or help triggers |
| 4.7 | Enable familiarization with dialogue | ❌ Fail | No guided tour or first-time hints |

### Examples from pacus

- **Bookkeeping software pattern**: ❌ No help system guides through steps
- **Scanning software pattern**: ❌ No explanation of relationships (project ↔ acts ↔ audit)
- **Menu items**: ❌ No "Help" key support
- **Feedback**: ❌ No patterns explained for memorization
- **Scheduling system**: ❌ No evaluation of potential variations before applying

---

## 5. Controllability (Clause 4.7)

**Definition**: User able to initiate & control direction/pace of interaction until goal met. Pace NOT dictated by system.

### Recommendations Checklist

| # | Recommandation | Status | Evidence/Location |
|---|-------------------|--------|----------------------|
| 5.1 | User controls how to continue dialogue | ✅ Pass | Click links to navigate freely |
| 5.2 | If dialogue interrupted, user determines restart point | ✅ Pass | "К списку" link, browser back button |
| 5.3 | If task operations reversible & context allows, undo at least last step | ✅ Pass | Browser back button works |
| 5.4 | User controls data presentation when volume is large | ✅ Pass | Currency selector (client-side JS) |
| 5.5 | Enable use of any available input/output devices | ✅ Pass | Mouse/keyboard compatible |
| 5.6 | Enable modification of default values (where appropriate) | ⚠️ Partial | Only currency modifiable |
| 5.7 | Original data remains available if modified (where required) | ✅ Pass | Currency resets on page reload |

### Examples from pacus

- **Mobile phone pattern**: Messages (HTML pages) visible & navigable until user closes
- **ERP system pattern**: ✅ Partially entered data preserved (not applicable for static HTML)
- **Database app**: ✅ Currency modification allowed (USD, EUR, RUB, GBP)
- **Text editor**: ✅ Undo via browser back button
- **Calendar app**: ⚠️ No view customization (day/week/month/user criteria)
- **Search form**: ✅ Activate via mouse or keyboard

---

## 6. Error Tolerance (Clause 4.8)

**Definition**: Despite evident errors in input, intended result may be achieved with no/minimal corrective action.

### Recommendations Checklist

| # | Recommandation | Status | Evidence/Location |
|---|-------------------|--------|----------------------|
| 6.1 | Assist user in detecting & avoiding input errors | N/A | Static HTML, no user input |
| 6.2 | Prevent actions causing undefined system states/failures | ✅ Pass | No interactive elements to cause errors |
| 6.3 | When error occurs, provide explanation for correction | N/A | No user input |
| 6.4 | Active support for error recovery where errors typically occur | N/A | No user input |
| 6.5 | Auto-correct where possible, advise user & offer override | N/A | No user input |
| 6.6 | Enable deferring correction or leaving errors uncorrected | N/A | No user input |
| 6.7 | Provide error & correction info upon request | N/A | No user input |

### Error Recovery

- **Minimize steps for correction**: N/A for static HTML
- **Cursor auto-positioned at error**: N/A for static HTML

### Examples from pacus

- **E-commerce pattern**: N/A (no unfilled fields)
- **DVD player pattern**: N/A (no DVD insertion check)
- **Printing**: N/A (no page number validation)
- **E-mail client**: N/A (no syntax checking)

---

## 7. Suitability for Individualization (Clause 4.9)

**Definition**: Users can modify interaction & presentation to suit individual capabilities/needs.

### Recommendations Checklist

| # | Recommandation | Status | Evidence/Location |
|---|-------------------|--------|----------------------|
| 7.1 | Provide mechanisms to modify characteristics for diverse users | ⚠️ Partial | Currency selector only |
| 7.2 | Allow choice from alternative representations | ❌ Fail | No dark mode, font size options |
| 7.3 | Modify amount of explanation (details in error messages, help info) | ❌ Fail | No configurable help/tooltips |
| 7.4 | Incorporate own vocabulary for objects/actions | ❌ Fail | No custom labels |
| 7.5 | Set speed of dynamic inputs/outputs to match needs | N/A | Static HTML |
| 7.6 | Select between different dialogue techniques | ❌ Fail | Fixed HTML format only |
| 7.7 | Select levels/methods of interaction | ❌ Fail | No interaction level selection |
| 7.8 | Select how input/output data represented (format & type) | ❌ Fail | HTML only, no PDF/print preview toggle |
| 7.9 | Add/rearrange dialogue elements/functionality for individual needs | ❌ Fail | Static layout |
| 7.10 | Reversible individualization, return to original settings | ✅ Pass | Currency resets on reload |

### Examples from pacus

- **Text-based app**: ❌ No icons/graphics for limited reading skills
- **Individualization**: ✅ Currency can be reset to default (reload page)
- **Business app**: ❌ No way to turn off system-initiated help (no help shown anyway)
- **Word processor**: ❌ No save via menu, icon, or keyboard shortcut selection
- **Railway ticket machine**: ❌ No choice between direct entry or list selection
- **Toolbar**: ❌ No "Strikethrough" add option for frequently used features

---

## Overall Compliance Summary

| Principle | Rating | Score | Key Actions Needed |
|-----------|--------|-------|---------------------|
| 1. Suitability for Task | ✅ Conformant | 6/7 | Add accessibility alternatives (screen reader support) |
| 2. Self-descriptiveness | ✅ Conformant | 5/6 | Add format/units explanation tooltip |
| 3. Conformity with Expectations | ✅ Conformant | 6/6 | None needed |
| 4. Suitability for Learning | ❌ Gap | 2/7 | Add tutorial, help system, tooltips |
| 5. Controllability | ✅ Conformant | 6/7 | Add more customization options |
| 6. Error Tolerance | ✅ Conformant | 1/7 | N/A for static HTML |
| 7. Suitability for Individualization | ⚠️ Partial | 2/10 | Add dark mode, font size, PDF export |

**Overall Score**: 26/50 (52%) — **Needs Improvement**

---

## Action Plan

### High Priority (Clause 4.6 — Suitability for Learning)

1. **Add help tooltips** to key elements (status badges, currency selector)
2. **Create minimal tutorial** (one-page HTML) explaining navigation flow
3. **Add "?" icons** next to complex elements with inline help

### Medium Priority (Clause 4.9 — Suitability for Individualization)

4. **Add dark mode toggle** (CSS media query + JS toggle)
5. **Add font size selector** (small/medium/large)
6. **Add PDF export option** (in addition to HTML print)

### Low Priority (Clause 4.3, 4.4 — Task & Self-descriptiveness)

7. **Add ARIA labels** for screen reader support
8. **Add format explanation** tooltip for currency amounts

---

## Conformance Statement (Clause 8)

### Requirements Satisfied (Clause 8.1)
- Clause 4.3: Suitability for Task — Partially satisfied (6/7)
- Clause 4.4: Self-descriptiveness — Partially satisfied (5/6)
- Clause 4.5: Conformity with Expectations — Fully satisfied (6/6)
- Clause 4.6: Suitability for Learning — Not satisfied (2/7)
- Clause 4.7: Controllability — Partially satisfied (6/7)
- Clause 4.8: Error Tolerance — N/A for static HTML
- Clause 4.9: Suitability for Individualization — Partially satisfied (2/10)

### Applicable Recommendations Identified (Clause 8.2)
See Section 4 (Suitability for Learning) and Section 7 (Individualization) for full list.

### Explanation of Non-Applicable Recommendations (Clause 8.3)
- Clause 4.8 (Error Tolerance): Not applicable as HTML artifacts are static (no user input).

### Statement of Compliance (Clause 8.4)
- **Current status**: Partially compliant
- **Target date for full compliance**: 2026-08-01
- **Responsible**: UX Designer, Development Team

---

## Update History

| Date | Version | Changes |
|------|---------|---------|
| 2026-05-01 | 1.0 | Initial compliance checklist |

---

*Next scheduled review: 2026-08-01*
