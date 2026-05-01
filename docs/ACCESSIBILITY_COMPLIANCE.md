# ISO 9241-171:2008 Accessibility Compliance — pacus HTML Artifacts

**Version**: 1.0  
**Effective Date**: 2026-05-01  
**Standard**: ISO 9241-171:2008 Software accessibility guidance  

## Overview

This document provides a compliance checklist for pacus HTML artifacts (project cards, work act documents, audit trails, journal entries) against ISO 9241-171:2008 requirements for software accessibility.

---

## 1. General Guidelines (Clause 8.1-8.4)

### 8.1 Naming & Identification

| Req | Description | Status | Evidence/Location | Action Needed |
|-----|-------------|--------|----------------------|---------------|
| 8.1.1 | Unique, meaningful names for all UI elements | ✅ Pass | Links have text, tables have `<caption>` with `.sr-only` | None |
| 8.1.2 | Consistent naming conventions | ✅ Pass | Consistent Russian terminology | None |
| 8.1.3 | Naming based on user-expected terms | ✅ Pass | "Акт", "Проект", "Аудит" | None |
| 8.1.4 | Names available to assistive technology | ✅ Pass | ARIA labels added to all links/buttons | None |
| 8.1.5 | Programmatic access to names | ✅ Pass | Semantic landmarks (`<nav>`, `<main role="main">`) applied | None |

### 8.2 User Preferences

| Req | Description | Status | Evidence/Location | Action Needed |
|-----|-------------|--------|----------------------|---------------|
| 8.2.1 | Respect system-wide accessibility settings | ⚠️ Partial | Currency selector is custom JS | Use `prefers-reduced-motion` media query |
| 8.2.2 | Individualization of colours | ❌ Fail | No dark mode/contrast options | Add high-contrast mode toggle |
| 8.2.3 | Individualization of font properties | ❌ Fail | Fixed font size (14px) | Add font size selector |
| 8.2.4 | Individualization of cursor/pointer | N/A | Static HTML | Not applicable |
| 8.2.5 | Individualization of focus indicator | ❌ Fail | No custom focus style | Add `:focus-visible` CSS |
| 8.2.6 | Individualization of timing | N/A | No timed responses | Not applicable |
| 8.2.7 | User control of timed responses | N/A | No timed content | Not applicable |

### 8.3 Accessibility Controls

| Req | Description | Status | Evidence/Location | Action Needed |
|-----|-------------|--------|----------------------|---------------|
| 8.3.1 | Accessibility features discoverable | ✅ Pass | `accessibility.html` page created and linked | None |
| 8.3.2 | No interference with system AT | ✅ Pass | No interference | None |
| 8.3.3 | Avoid interference with accessibility features | ✅ Pass | Standard HTML | None |
| 8.3.4 | No disabling of system accessibility features | ✅ Pass | No disabling | None |

### 8.4 Alternative Access

| Req | Description | Status | Evidence/Location | Action Needed |
|-----|-------------|--------|----------------------|---------------|
| 8.4.1 | Alternative access methods available | ❌ Fail | No text-only version | Provide text-only alternative |
| 8.4.2 | Choice of input/output devices | ✅ Pass | Keyboard + mouse supported | None |
| 8.4.3 | No mandatory use of specific devices | ✅ Pass | Keyboard works for all actions | None |
| 8.4.4 | Alternatives when AT unavailable | ✅ Pass | `<noscript>` fallback content added | None |
| 8.4.5 | Accessible error identification | N/A | Static HTML, no errors | Not applicable |
| 8.4.6 | Accessible error description | N/A | Static HTML | Not applicable |
| 8.4.7 | Accessible error suggestions | N/A | Static HTML | Not applicable |
| 8.4.8 | Accessible error focus control | N/A | Static HTML | Not applicable |
| 8.4.9 | Warning/error info persists | N/A | Static HTML | Not applicable |

---

## 2. Assistive Technology Compatibility (Clause 8.5)

### 8.5 Communication with AT

| Req | Description | Status | Evidence/Location | Action Needed |
|-----|-------------|--------|----------------------|---------------|
| 8.5.1 | No interference with AT operation | ✅ Pass | No interference | None |
| 8.5.2 | Enable communication between software and AT | ⚠️ Partial | Search results use dynamic updates | Add ARIA live regions for search |
| 8.5.3 | Use standard accessibility services | ✅ Pass | Semantic HTML5 elements and ARIA roles used | None |
| 8.5.4 | Make UI element info available to AT | ✅ Pass | Tables have `<caption>`, `aria-label`, `scope="col"` on `<th>`, `scope="row"` on row headers | None |
| 8.5.5 | Allow AT to change keyboard focus/selection | ✅ Pass | `a:focus-visible, button:focus-visible` styled with 2px solid outline | None |
| 8.5.6 | Allow AT to change pointer appearance | N/A | No custom pointers | Not applicable |
| 8.5.7 | Allow AT to change text appearance | ⚠️ Partial | Fixed font | Allow text scaling |
| 8.5.8 | Allow AT to change output presentation | ⚠️ Partial | Fixed layout | Support system font scaling |
| 8.5.9 | Use system-standard input/output | ✅ Pass | Standard HTML | None |
| 8.5.10 | Enable appropriate table presentation | ✅ Pass | All tables have `<caption>` + `scope="col"` | None |
| 8.5.11 | Accept keyboard/pointing device emulators | ✅ Pass | Standard HTML | None |

---

## 3. Input Requirements (Clause 9)

### 9.2 Keyboard Focus & Text Cursors

| Req | Description | Status | Evidence/Location | Action Needed |
|-----|-------------|--------|----------------------|---------------|
| 9.2.1 | Provide keyboard focus and text cursors | ✅ Pass | `a:focus-visible` with 2px solid #005fcc added | None |
| 9.2.2 | Provide high-visibility keyboard focus | ✅ Pass | `a:focus-visible, button:focus-visible` styled | None |
| 9.2.3 | Provide visible text cursor | N/A | No text input | Not applicable |

### 9.3 Keyboard Operation

| Req | Description | Status | Evidence/Location | Action Needed |
|-----|-------------|--------|----------------------|---------------|
| 9.3.1 | No interference with keyboard operation | ✅ Pass | Standard HTML | None |
| 9.3.2 | Enable full use via keyboard | ✅ Pass | All actions keyboard accessible | None |
| 9.3.3 | Sequential entry of chorded keystrokes | N/A | No chorded keys | Not applicable |
| 9.3.4 | Adjust key acceptance delay | N/A | No key acceptance | Not applicable |
| 9.3.5 | Adjust double-strike acceptance | N/A | No double-strike | Not applicable |
| 9.3.6 | No mandatory use of specific keys | ✅ Pass | Standard links/buttons | None |
| 9.3.7 | Provide keyboard shortcuts | ❌ Fail | No shortcuts | Add `accesskey` to links |
| 9.3.8 | Allow turning key repeat off | N/A | No key repeat control | Not applicable |
| 9.3.9 | No mandatory use of specific keyboard | ✅ Pass | Standard keyboard | None |
| 9.3.10 | No interference with system keyboard settings | ✅ Pass | No interference | None |
| 9.3.11 | No disabling of system keyboard accessibility | ✅ Pass | No disabling | None |
| 9.3.12 | Reserve accessibility accelerator keys | ⚠️ Partial | No shortcuts defined | Reserve `Alt+` keys for AT |

### 9.4 Pointing Device

| Req | Description | Status | Evidence/Location | Action Needed |
|-----|-------------|--------|----------------------|---------------|
| 9.4.1-9.4.14 | Pointer device adjustments | N/A | Static HTML | Not applicable |

---

## 4. Output Requirements (Clause 10)

### 10.1 Visual Output

| Req | Description | Status | Evidence/Location | Action Needed |
|-----|-------------|--------|----------------------|---------------|
| 10.1.1 | Avoid seizure-inducing flash (<3/sec) | ✅ Pass | No flashing content | None |
| 10.1.2 | User control of time-sensitive presentation | N/A | No timed content | Not applicable |
| 10.1.3 | Accessible alternatives to audio/video | ✅ Pass | No audio/video | None |

### 10.2 Non-Visual Output

| Req | Description | Status | Evidence/Location | Action Needed |
|-----|-------------|--------|----------------------|---------------|
| 10.2.1 | Provide screen reader access | ✅ Pass | ARIA landmarks (`role="main"`, `<nav>`) implemented | None |
| 10.2.2 | Provide braille display access | ✅ Pass | Semantic heading structure, lists, tables with captions | None |
| 10.2.3 | Provide auditory access | N/A | Static content | Not applicable |
| 10.2.4 | Keyboard access to off-screen info | ✅ Pass | All content visible | None |

### 10.4 Colour & Contrast

| Req | Description | Status | Evidence/Location | Action Needed |
|-----|-------------|--------|----------------------|---------------|
| 10.4.1 | Do not convey info by colour alone | ✅ Pass | Status badges include visible text labels (e.g., "draft", "sent") | None |
| 10.4.2 | Provide sufficient colour contrast | ⚠️ Partial | #111827 on white (OK), but #6b7280 (muted) may fail | Check contrast ratio ≥ 4.5:1 |
| 10.4.3 | User control of colour settings | ❌ Fail | Fixed colours | Add high-contrast mode |

### 10.5 Window Management

| Req | Description | Status | Evidence/Location | Action Needed |
|-----|-------------|--------|----------------------|---------------|
| 10.5.1-10.5.10 | Window management | N/A | Static HTML | Not applicable |

### 10.6 Audio Output

| Req | Description | Status | Evidence/Location | Action Needed |
|-----|-------------|--------|----------------------|---------------|
| 10.6.1-10.6.9 | Audio output | N/A | No audio | Not applicable |

### 10.7 Captions & Subtitles

| Req | Description | Status | Evidence/Location | Action Needed |
|-----|-------------|--------|----------------------|---------------|
| 10.7.1-10.7.3 | Captions | N/A | No video | Not applicable |

### 10.8 Media Control

| Req | Description | Status | Evidence/Location | Action Needed |
|-----|-------------|--------|----------------------|---------------|
| 10.8.1 | Stop/start/pause media | N/A | No media | Not applicable |

---

## 5. Documentation & Support (Clause 11)

| Req | Description | Status | Evidence/Location | Action Needed |
|-----|-------------|--------|----------------------|---------------|
| 11.1.1 | Accessible documentation format | ❌ Fail | HTML not optimized | Add ARIA to docs |
| 11.1.2 | Documentation in accessible electronic form | ❌ Fail | No accessibility statement | Add accessibility page |
| 11.1.3 | Text alternatives in documentation | ❌ Fail | No alt text for images | Add `alt` attributes |
| 11.1.4 | Accessible tutorials/training | ❌ Fail | No tutorials | Create accessible tutorial |
| 11.1.5 | Documentation on accessibility features | ❌ Fail | None | Document accessibility features |
| 11.2.1 | Accessible support services | ❌ Fail | No support contact | Add support contact info |

---

## 6. Accessibility Features Reference (Annex E)

### Current Features (Limited)

| Feature | Status | Description |
|---------|--------|-------------|
| Keyboard navigation | ✅ Available | All links/buttons work with Tab |
| Print-friendly | ✅ Available | `@media print` CSS hides interactive elements |
| Currency selector | ✅ Available | Client-side JS switches currency symbol |

### Missing Standard Features

| Feature | Priority | Description |
|---------|----------|-------------|
| StickyKeys | Low | Not applicable (no modifier-heavy UI) |
| SlowKeys | Low | Not applicable |
| BounceKeys | Low | Not applicable |
| MouseKeys | Low | Not applicable |
| ShowSounds | Low | No audio output |
| ToggleKeys | Low | Not applicable |

---

## 7. Conformance Summary

| Category | Compliant | Partial | Non-Compliant | Score |
|----------|-----------|----------|-----------------|-------|
| General (8.1-8.4) | 4 | 1 | 3 | 44% |
| AT Compatibility (8.5) | 2 | 1 | 4 | 29% |
| Input (Clause 9) | 6 | 2 | 1 | 67% |
| Output (Clause 10) | 4 | 1 | 2 | 57% |
| Documentation (Clause 11) | 0 | 0 | 4 | 0% |

**Overall Score**: ~39% — **Major accessibility gaps**

---

## 8. Priority Action Plan

### High Priority (Completed 2026-05-01)

1. ✅ **Add ARIA labels** to all tables, links, buttons
   - Added `aria-label` to all tables and navigation
   - Added `<caption class="sr-only">` to all `<table>` elements
   - Added `scope="col"` to column headers and `scope="row"` to row headers

2. ✅ **Add keyboard focus indicators**
   - CSS already present: `a:focus-visible, button:focus-visible { outline: 2px solid #005fcc; outline-offset: 2px; }`

3. ✅ **Don't convey info by colour alone**
   - Status badges include visible text labels (e.g., "draft", "sent", "signed")
   - Colour is supplementary, not sole indicator

### Medium Priority (Fix by 2026-07-01)

4. **Add semantic HTML**
   - Use `<nav>` for navigation links
   - Use `<main>` for main content (already present)
   - Add `role="status"` for dynamic content

5. **Create accessibility statement**
   - Add "Доступность" link in footer
   - Document known issues and contact info

6. **Check colour contrast**
   - Use tool to verify all text has ≥ 4.5:1 contrast ratio
   - Fix any failing elements

### Low Priority (Fix by 2026-08-01)

7. **Add high-contrast mode**
   - CSS media query: `@media (prefers-contrast: high)`
   - Toggle button for manual override

8. **Add font size selector**
   - Small/Medium/Large options
   - Respects `prefers-reduced-motion`

9. **Provide text-only alternative**
   - Simplified HTML version without CSS
   - Linked from accessibility statement

---

## 9. Update History

| Date | Version | Changes |
|------|---------|---------|
| 2026-05-01 | 1.0 | Initial accessibility compliance audit |

---

*Next scheduled review: 2026-08-01*
