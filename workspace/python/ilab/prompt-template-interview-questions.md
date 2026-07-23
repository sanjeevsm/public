# Prompt Template: Interview Question Generation

**Date:** 2026-06-24
**Author:** [Sanjeev — Lead Software Engineer]
**Project:** [iLab+]
**Model:** [Model used — e.g., Claude via DIAL, GitHub Copilot Chat]
**DIAL location:** [DIAL shared link or folder path]
**Committed location:** [iLab+]

---

## Purpose

[this prompt should be able to provide user with a list of interview questions with multiple choice
  where user can select correct answers from the 4 choices for each question this should be used by
  users of this application who will use it as a reference for interview preparation and this comes
  in the implementation stage]

---

## Variable Placeholders

| Placeholder | Description | Example value |
|---|---|---|
| `{{number_of_questions}}` | [number of questions that you be generated based on prompt given] | [3] |
| `{{experience_level}}` | [experience level for this the question generation shoulld align with] | [java senior developer] |
| `{{job_description}}` | [relevance and context by which questions should be generated] | [integration developer] |
| `{{skill_set}}` | [tech skills based on which questions are to be generated] | [java, micro services] |

---

## Output Format Instruction

[Return a list of interview questions. Each question should have 4 answers to choose from]

---

## Prompt Body

[Generate {{number_of_questions}} interview questions for a {{experience_level}} for this specific
  {{job_description}}. Skill set should have {{skill_set}}]

---

## Test Run (Author)

**Input values used:**
- `{{number_of_questions}}` = [3]
- `{{experience_level}}` = [java senior developer ]
- `{{job_description}}` = [integration developer]
- `{{skill_set}}` = [java, micro services]

**Output quality:** [Outout was usable as-is and did not require any revision]

---

## Peer Review

**Reviewer:** [Name — Akash]
**Date reviewed:** 2026-06-24
**Model used by reviewer:** [Claude]

**Reviewer input values used:**
- `{{number_of_questions}}` = [5]
- `{{experience_level}}` = [unix senior developer ]
- `{{job_description}}` = [environment specialist]
- `{{skill_set}}` = [unix, sed, awk]

| Review question | Reviewer answer |
|---|---|
| Could you run the template without asking the author anything? | Yes / No — [was able to execute the template without asking] |
| Was the output format what you expected? | Yes / No — [output was in the format i expected] |
| Would you use this template on your own work? | Yes / No — [yes the template could be used at work] |
| One concrete improvement suggestion | [retrieval could be a bit faster] |

---

## Revision History

| Version | Date | Change | Author |
|---|---|---|---|
| 1.0 | 2026-06-24 | Initial commit | [Sanjeev] |
| 1.1 | 2026-06-24 | Post-review update | [Akash] |
