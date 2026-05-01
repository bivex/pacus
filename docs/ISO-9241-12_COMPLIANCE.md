# ISO 9241-12:1998 Compliance Checklist — pacus HTML Artifacts

**Version**: 1.0  
**Effective Date**: 2026-05-01  
**Standard**: ISO 9241-12:1998 Ergonomic requirements for presentation of information on visual display terminals  

## Overview

This document provides a compliance checklist for pacus HTML artifacts (project cards, work act documents, audit trails, journal entries) against ISO 9241-12:1998 requirements for visual presentation of information.

---

## 1. Organization of Information (Clause 5)

### 5.1 Location of Information

| # | Recommendation | Status | Evidence/Location | Action Needed |
|---|-------------------|--------|----------------------|---------------|
| 5.1.1 | Information meets user expectations & task requirements | ✅ Pass | Tables for data, headings for sections | None |
| 5.1.2 | Minimizes search time | ✅ Pass | Clear h1/h2 headings | None |

### 5.2 Appropriateness of Windows

| # | Recommendation | Status | Evidence/Location | Action Needed |
|---|-------------------|--------|----------------------|---------------|
| 5.2.1 | Unique window identification | ✅ Pass | `<title>` element set | None |
| 5.2.2 | Default sizes/locations minimize operations | ✅ Pass | A4 CSS, max-width: 860px | None |
| 5.2.3 | Consistent window appearance | ✅ Pass | Same layout across all artifacts | None |
| 5.2.4 | Primary/secondary relationships visually apparent | ✅ Pass | "К списку" link returns to index | None |
| 5.2.5 | Control elements consistently placed | ✅ Pass | `.topbar` with consistent buttons | None |
| 5.2.6 | Overlapping/tiled format appropriate | N/A | Single page view, no windows | Not applicable |

### 5.3 Recommendations for Windows

| # | Recommendation | Status | Evidence/Location | Action Needed |
|---|-------------------|--------|----------------------|---------------|
| 5.3.1 | Unique window ID (system, app, function) | ✅ Pass | `<title>` with project/act name | None |
| 5.3.2 | Default sizes minimize operations | ✅ Pass | A4 layout, no resizing needed | None |
| 5.3.3 | Consistent appearance within app | ✅ Pass | Same CSS across pages | None |
| 5.3.4 | Consistent in multi-app environment | ✅ Pass | Same style across all artifacts | None |

### 5.4 Areas

| # | Recommendation | Status | Evidence/Location | Action Needed |
|---|-------------------|--------|----------------------|---------------|
| 5.4.1 | Consistent location of areas | ✅ Pass | `.topbar`, `main`, tables consistent | None |
| 5.4.2 | Density ~40% (not cluttered) | ⚠️ Partial | Tables dense but readable | Reduce if feedback indicates clutter |

### 5.5 Input/Output Area

| # | Recommendation | Status | Evidence/Location | Action Needed |
|---|-------------------|--------|----------------------|---------------|
| 5.5.1 | Required information displayed | ✅ Pass | All relevant data in tables | None |
| 5.5.2 | Scrolling/paging when info exceeds area | N/A | Content fits in page | Not applicable |
| 5.5.3 | Indication of relative position | N/A | Single page view | Not applicable |

### 5.6 Groups

| # | Recommendation | Status | Evidence/Location | Action Needed |
|---|-------------------|--------|----------------------|---------------|
| 5.6.1 | Groups perceptually distinct | ✅ Pass | `<h2>` separators, `.grid` layout | None |
| 5.6.2 | Sequencing supports task order | ✅ Pass | History tables ordered by date | None |
| 5.6.3 | Use of conventions (addresses, etc.) | ✅ Pass | Russian date format (dd.mm.yyyy) | None |
| 5.6.4 | Functional grouping | ✅ Pass | Related data grouped in tables | None |
| 5.6.5 | Visually distinct "chunks" (~5-6 lines) | ⚠️ Partial | Table rows separated by borders | Add zebra striping |

### 5.7 Lists

| # | Recommendation | Status | Evidence/Location | Action Needed |
|---|-------------------|--------|----------------------|---------------|
| 5.7.1 | Logical/natural order | ✅ Pass | History ordered chronologically | None |
| 5.7.2 | Item separation for visual scanning | ✅ Pass | Table rows with borders | None |
| 5.7.3 | Alphabetic: left-justified | ✅ Pass | Text left-justified | None |
| 5.7.4 | Numeric: right-justified | ✅ Pass | `.amount { text-align: right; }` | None |
| 5.7.5 | Fixed font for numeric lists | ⚠️ Partial | Proportional font used | Consider monospace for amounts |
| 5.7.6 | Item numbering begins with "1" | N/A | No numbered lists | Not applicable |
| 5.7.7 | Continuity of item numbering | N/A | No paginated lists | Not applicable |
| 5.7.8 | Indication of list continuation | N/A | Single page view | Not applicable |

### 5.8 Tables

| # | Recommendation | Status | Evidence/Location | Action Needed |
|---|-------------------|--------|----------------------|---------------|
| 5.8.1 | Tabular: leftmost column = highest priority | ✅ Pass | Date/number in left columns | None |
| 5.8.2 | Consistent with paper forms | ✅ Pass | A4 layout matches print format | None |
| 5.8.3 | Maintain column/row headings visible | ❌ Fail | No `<thead>` or `scope` attributes | Add `<thead>`, `scope="col"` |
| 5.8.4 | Facilitate visual scanning | ❌ Fail | No zebra striping or blank lines | Add `nth-child(even)` background |
| 5.8.5 | Column spacing ~3-5 spaces | ✅ Pass | CSS padding 8px 10px | None |

### 5.9 Labels

| # | Recommendation | Status | Evidence/Location | Action Needed |
|---|-------------------|--------|----------------------|---------------|
| 5.9.1 | Screen elements labelled | ✅ Pass | Table headers present | Add ARIA labels |
| 5.9.2 | Labels explain purpose & content | ✅ Pass | "Акты работ по проекту" etc. | None |
| 5.9.3 | Grammatically consistent | ✅ Pass | Consistent noun phrases | None |
| 5.9.4 | Labels consistently positioned | ✅ Pass | Headers in `<th>` top of table | None |
| 5.9.5 | Labels distinguishable from data | ✅ Pass | Bold headers, borders | None |
| 5.9.6 | Consistent format & alignment | ✅ Pass | Left-justified text, right-justified amounts | None |
| 5.9.7 | Units in label or right of field | ✅ Pass | "Итого" headers imply currency | None |

### 5.10 Fields

| # | Recommendation | Status | Evidence/Location | Action Needed |
|---|-------------------|--------|----------------------|---------------|
| 5.10.1 | Entry & read-only fields distinct | N/A | Static HTML, no input fields | Not applicable |
| 5.10.2 | Partitioning long items | N/A | No input fields | Not applicable |
| 5.10.3 | Entry field format clearly indicated | N/A | No input fields | Not applicable |
| 5.10.4 | Entry field length indicated | N/A | No input fields | Not applicable |

---

## 2. Graphical Objects (Clause 6)

### 6.1 General Recommendations

| # | Recommendation | Status | Evidence/Location | Action Needed |
|---|-------------------|--------|----------------------|---------------|
| 6.1.1 | Distinctive states via coding techniques | ⚠️ Partial | Status bold, but colour alone | Add text labels to status |
| 6.1.2 | Differentiating identical graphical objects | N/A | No identical icons | Not applicable |

### 6.2 Cursors and Pointers

| # | Recommendation | Status | Evidence/Location | Action Needed |
|---|-------------------|--------|----------------------|---------------|
| 6.2.1 | Cursor/pointer: distinctive visual features | N/A | Static HTML | Not applicable |
| 6.2.2 | Cursor NOT obscure characters | N/A | Static HTML | Not applicable |
| 6.2.3 | Cursor stationary until user moves | N/A | Static HTML | Not applicable |
| 6.2.4 | Cursor "home" position consistent | N/A | Static HTML | Not applicable |
| 6.2.5 | Initial position in appropriate field | N/A | No input fields | Not applicable |
| 6.2.6 | Point designation accuracy | N/A | No graphics | Not applicable |
| 6.2.7 | Multiple cursors visually distinct | N/A | Single cursor | Not applicable |

---

## 3. Coding Techniques (Clause 7)

### 7.1 General Recommendations for Codes

| # | Recommendation | Status | Evidence/Location | Action Needed |
|---|-------------------|--------|----------------------|---------------|
| 7.1.1 | Codes perceptually distinct | ✅ Pass | Status values distinct | None |
| 7.1.2 | Consistent coding with same meaning | ✅ Pass | Same status = same display | None |
| 7.1.3 | Meaningful codes (mnemonic preferred) | ✅ Pass | "Акт", "Проект" meaningful | None |
| 7.1.4 | Access to meaning of code | ✅ Pass | Status visible in table | None |
| 7.1.5 | Use of standards/conventional meanings | ✅ Pass | Russian conventions followed | None |
| 7.1.6 | Rules of code construction | ✅ Pass | Consistent status values | None |
| 7.1.7 | Removal of codes (indicate absence) | N/A | No removable codes | Not applicable |

### 7.2 Alphanumeric Coding

| # | Recommendation | Status | Evidence/Location | Action Needed |
|---|-------------------|--------|----------------------|---------------|
| 7.2.1 | Short codes (preferably ≤6 characters) | ✅ Pass | Status codes short (e.g., "active") | None |
| 7.2.2 | Alphabetic preferred over numeric | ✅ Pass | Status uses text | None |
| 7.2.3 | Use of upper case (same meaning) | ✅ Pass | Consistent casing | None |

### 7.3 Abbreviations for Alphanumeric Codes

| # | Recommendation | Status | Evidence/Location | Action Needed |
|---|-------------------|--------|----------------------|---------------|
| 7.3.1 | As short as possible | ✅ Pass | Minimal abbreviations | None |
| 7.3.2 | Abbreviations of different length | ✅ Pass | Consistent length | None |
| 7.3.3 | Truncation without ambiguity | ✅ Pass | No truncated codes | None |
| 7.3.4 | Deviation from rules minimized | ✅ Pass | Consistent rules | None |
| 7.3.5 | Conventional/task-related abbreviations | ✅ Pass | "Акт", "Проект" | None |

### 7.4 Graphical Coding

| # | Recommendation | Status | Evidence/Location | Action Needed |
|---|-------------------|--------|----------------------|---------------|
| 7.4.1 | Limited levels of graphical codes | ✅ Pass | ~3 levels (heading, table, text) | None |
| 7.4.2 | Icons: easily discerned & discriminated | N/A | No icons used | Not applicable |
| 7.4.3 | Three-dimensional coding | N/A | No 3D graphics | Not applicable |
| 7.4.4 | Geometric shapes | N/A | No shapes used | Not applicable |
| 7.4.5 | Line coding | N/A | No line graphics | Not applicable |

### 7.5 Colour Coding

| # | Recommendation | Status | Evidence/Location | Action Needed |
|---|-------------------|--------|----------------------|---------------|
| 7.5.1 | Colour should NEVER be ONLY means of coding | ❌ Fail | Status uses colour alone | Add text labels to status badges |
| 7.5.2 | Discriminative use of colours avoided | ⚠️ Partial | Minimal colour use | Avoid "busy" appearance |
| 7.5.3 | Attachment to categories (1 colour = 1 category) | ⚠️ Partial | Status colours not defined | Define colour per status |
| 7.5.4 | Number of colours ≤6 + black & white | ✅ Pass | Minimal palette (black, white, grey) | None |
| 7.5.5 | Saturated blue avoided on dark background | ✅ Pass | Dark text on light background | None |
| 7.5.6 | Selection for non-colour units (monochrome) | ⚠️ Partial | Assumes colour display | Test on monochrome |

### 7.6 Markers

| # | Recommendation | Status | Evidence/Location | Action Needed |
|---|-------------------|--------|----------------------|---------------|
| 7.6.1 | Special symbols for markers | N/A | No markers used | Not applicable |
| 7.6.2 | Markers for selection (single vs. multiple) | N/A | No markers | Not applicable |
| 7.6.3 | Unique use of symbols for markers | N/A | No markers | Not applicable |
| 7.6.4 | Positioning of markers | N/A | No markers | Not applicable |

---

## 4. Compliance Summary

| Category | Compliant | Partial | Non-Compliant | Score |
|----------|-----------|----------|-----------------|-------|
| Organization - Windows (5.2-5.3) | 4 | 0 | 0 | 100% |
| Organization - Areas/Groups (5.4-5.6) | 4 | 1 | 0 | 80% |
| Organization - Lists (5.7) | 4 | 1 | 0 | 80% |
| Organization - Tables (5.8) | 2 | 0 | 2 | 50% |
| Organization - Labels (5.9) | 7 | 0 | 0 | 100% |
| Organization - Fields (5.10) | 0 | 0 | 0 | N/A |
| Graphical Objects (Clause 6) | 1 | 0 | 0 | 100% |
| Coding - General (7.1) | 6 | 0 | 0 | 100% |
| Coding - Alphanumeric (7.2-7.3) | 8 | 0 | 0 | 100% |
| Coding - Graphical (7.4) | 1 | 0 | 0 | N/A |
| Coding - Colour (7.5) | 2 | 2 | 1 | 40% |
| Coding - Markers (7.6) | 0 | 0 | 0 | N/A |

**Overall Score**: ~76% — **Good, needs minor improvements**

---

## 5. Priority Action Plan

### High Priority (Fix by 2026-06-01)

1. **Add `<thead>` to all tables**
   - Wrap header rows in `<thead>` element
   - Add `scope="col"` to `<th>` elements
   - Add `scope="row"` to row headers if applicable

2. **Add visual scanning aids to tables**
   - CSS: `tr:nth-child(even) { background: #f9fafb; }`
   - Improves scannability per ISO 9241-12 5.8.4

3. **Don't use colour as only coding means (7.5.1)**
   - Add text labels to status badges (e.g., "Статус: Активен")
   - Use icons + colour for status indication

### Medium Priority (Fix by 2026-07-01)

4. **Add caption to tables**
   - Add `<caption>` element with table description
   - Helps screen readers and visual scanning

5. **Consider monospace for numeric data (5.7.5)**
   - CSS: `.amount { font-family: monospace; }`
   - Aligns decimal points better

6. **Define status colours explicitly (7.5.3)**
   - Document which colour = which status
   - Ensure 1 colour = 1 category

### Low Priority (Fix by 2026-08-01)

7. **Test on monochrome display (7.5.6)**
   - Verify tables readable without colour
   - Add patterns/textures if needed

8. **Reduce density if clutter reported (5.4.2)**
   - Increase padding or split large tables
   - User feedback needed

---

## 6. Update History

| Date | Version | Changes |
|------|---------|---------|
| 2026-05-01 | 1.0 | Initial compliance checklist |

---

*Next scheduled review: 2026-08-01*
