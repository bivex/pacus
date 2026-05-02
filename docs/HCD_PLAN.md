# Human-Centered Design Plan — pacus

**Version**: 1.0  
**Effective Date**: 2026-05-01  
**Standard**: ISO 9241-210:2010 Clause 5  

## 1. Introduction

This document describes the Human-Centered Design (HCD) plan for the pacus HTML artifact generation system. It integrates HCD activities with the overall project plan and defines responsibilities, methods, and milestones for user-centered design.

---

## 2. HCD Responsibilities

### 2.1 HCD Coordinator (Product Owner)
- Overall responsibility for HCD process compliance
- Ensure user involvement throughout design and development
- Allocate resources for HCD activities
- Review and approve HCD outputs
- Make trade-off decisions between conflicting requirements

### 2.2 UX Designer / Human Factors Engineer
- Conduct user research (interviews, surveys)
- Develop context of use description
- Elicit and document user requirements
- Create UI specifications and prototypes
- Conduct usability evaluations

### 2.3 Development Team
- Implement design solutions per UI specification
- Participate in user testing sessions
- Provide feedback on technical constraints
- Iterate on design based on evaluation results

### 2.4 Quality Assurance
- Verify HCD outputs against ISO 9241-210 requirements
- Conduct inspection-based evaluations
- Validate user requirements are met
- Document evaluation results

---

## 3. HCD Activities and Methods

### 3.1 Understand and Specify Context of Use (Clause 6.2)

**Methods**:
- User interviews (5-10 participants from each user group)
- Contextual inquiry (observe users in their work environment)
- Survey on user characteristics and preferences
- Task analysis (document workflow, frequency, duration)

**Outputs**:
- Context of use description (`docs/HCD_CONTEXT_OF_USE.md`)
- User group profiles
- Task list with frequency/duration

**Timeline**: Complete by 2026-06-01  
**Responsible**: UX Designer  
**Resources**: 40 person-hours

---

### 3.2 Specify User Requirements (Clause 6.3)

**Methods**:
- Workshop with stakeholders to prioritize requirements
- Derive requirements from context of use
- Define measurable usability objectives
- Document trade-offs with rationales

**Outputs**:
- User requirements specification (`docs/USER_REQUIREMENTS.md`)
- Usability objectives with metrics
- Trade-off log with rationales

**Timeline**: Complete by 2026-06-15  
**Responsible**: UX Designer, HCD Coordinator  
**Resources**: 30 person-hours

---

### 3.3 Produce Design Solutions (Clause 6.4)

**Methods**:
- Apply ISO 9241-110 dialogue principles
- Create HTML/CSS templates (already implemented in `gen_artifacts.py`)
- Prototype navigation flows
- Review against user requirements

**Outputs**:
- User interaction specification (implicit in code)
- User interface specification (HTML/CSS)
- Design justifications document

**Timeline**: Ongoing (iteration based on evaluation)  
**Responsible**: Development Team, UX Designer  
**Resources**: 20 person-hours per major update

---

### 3.4 Evaluate Design Against Requirements (Clause 6.5)

**User-Based Testing**:
- Recruit 5-8 users from target groups
- Create test scenarios (print project card, navigate audit trail)
- Measure task completion time, success rate, satisfaction
- Collect qualitative feedback (think-aloud, interview)

**Inspection-Based Evaluation**:
- Expert review against ISO 9241-110 dialogue principles
- Checklist-based review (see Annex B of ISO 9241-210)
- Heuristic evaluation (Nielsen's 10 heuristics)

**Long-Term Monitoring** (post-deployment):
- Collect user feedback via form in HTML artifacts
- Monitor help-desk requests related to artifacts
- Track print success rate (if possible)

**Outputs**:
- Evaluation results report
- Conformance test results
- List of identified issues with priorities
- Recommendations for design changes

**Timeline**: 
- Initial evaluation: 2026-07-01
- Ongoing: Every 3 months  
**Responsible**: QA, UX Designer  
**Resources**: 60 person-hours per evaluation cycle

---

## 4. Integration with Project Plan

HCD activities are integrated into the overall pacus project plan:

| Project Phase | HCD Activity | Milestone |
|---------------|---------------|-----------|
| Planning | Context of use, User requirements | Requirements approved |
| Design | Produce design solutions | UI specification complete |
| Development | Implement design, Iterative evaluation | Code complete |
| Testing | User-based testing, Inspection | Evaluation report complete |
| Deployment | Long-term monitoring | User satisfaction > 80% |
| Maintenance | Iterate based on feedback | Continuous improvement |

---

## 5. HCD Milestones and Timescales

| Milestone | Target Date | Deliverable |
|-----------|--------------|-------------|
| Context of use complete | 2026-06-01 | `docs/HCD_CONTEXT_OF_USE.md` |
| User requirements approved | 2026-06-15 | `docs/USER_REQUIREMENTS.md` |
| First usability evaluation | 2026-07-01 | Evaluation report |
| ISO 9241-210 conformance check | 2026-07-15 | Conformance statement |
| Second usability evaluation | 2026-10-01 | Evaluation report (iteration) |
| HCD review & update | 2026-11-01 | Updated context, requirements |

---

## 6. Resources Allocation

### 6.1 Personnel

| Role | Allocation | Hours (Total) |
|------|-------------|----------------|
| HCD Coordinator | 10% | 40 hours |
| UX Designer | 30% | 120 hours |
| Development Team | 5% | 20 hours |
| Quality Assurance | 15% | 60 hours |

### 6.2 Budget (if applicable)

- User testing incentives: $50 per participant × 8 = $400
- Usability tools/licenses: $0 (free tools)
- Documentation tools: $0 (Markdown in repo)

---

## 7. Feedback Mechanisms

### 7.1 User Feedback Collection
- Feedback form link in HTML artifacts (future enhancement)
- User interviews during testing sessions
- Email feedback: pacus-feedback@example.com

### 7.2 HCD Team Feedback
- Weekly HCD coordination meetings
- Issue tracker for HCD-related tasks
- Slack/Teams channel for HCD discussions

### 7.3 Stakeholder Communication
- Monthly HCD progress report to HCD Coordinator
- Evaluation results presented to project stakeholders
- User requirements changes approved by HCD Coordinator

---

## 8. HCD Outputs Management

All HCD outputs are version-controlled in the pacus repository:

| Output | Location | Update Frequency |
|--------|----------|-----------------|
| Context of use | `docs/HCD_CONTEXT_OF_USE.md` | Every 6 months |
| User requirements | `docs/USER_REQUIREMENTS.md` | Every 6 months |
| Evaluation results | `docs/evaluation_reports/` | Every 3 months |
| Conformance statement | `docs/HCD_CONFORMANCE.md` | Every 12 months |

---

## 9. Change Control

Changes to HCD outputs follow the same change control process as code:

1. Propose change (issue tracker)
2. Review by HCD Coordinator
3. Update document (pull request)
4. Approve and merge
5. Communicate to stakeholders

---

## 10. Update History

| Date | Version | Changes |
|------|---------|---------|
| 2026-05-01 | 1.0 | Initial HCD plan |

---

*Next scheduled review: 2026-11-01*
