# Model Selection Note

**Date:** 2026-06-24
**Author:** [Sanjeev — Lead Software Engineer]
**Project:** [iLab+]
**Task:** [Generate interview questions from a job description]
**Committed location:** iLab+

---

## Evaluation Criteria

| # | Criterion | Why it matters for this task |
|---|-----------|------------------------------|
| 1 | Accuracy |questions must be technically correct so a developer using them for
    interview prep isn't misled |
| 2 | Relevance |if the questions are not relevant the developer using the application will not get the desired
  output |
| 3 | Difficulty level |difficulty level is selected by the user based on the his experience and the expectation is to have
   the output aligned to this expectation |
| 4 | Format compliance | Format will defintely matter because use should not be able tom guess that answer just because one
  particular answer is formatted in a different way|

---

## Prompt Used

[Generate 5 interview questions for Senior Java Developer. Skill set should have Springboot, Apache
  camel, sql]

---

## Output Comparison

### Model A: [Claude]
> [1. Integration Architecture: Spring Boot & Apache Camel
  Question: "Imagine we are building a microservice that ingests large JSON payloads from a Kafka
  topic, processes and transforms them using Apache Camel, and persists the structured data into a
  relational database using Spring Boot. If the database experiences transient network failures or
  database locks, how would you design the Camel route to ensure zero data loss, proper error
  handling, and transaction boundaries across Kafka, Camel, and the database?"

  What to look for in the candidate's response:
  Camel Error Handling: Use of Camel's error handling strategies like Dead Letter Channel (DLC),
  redelivery policies with exponential backoff, and circuit breakers.
  Transaction Management: Knowledge of distributed transactions or compensating transactions. A
  senior candidate should mention SpringTransactionPolicy in Camel or transactional delivery
  guarantees (at-least-once processing) with Kafka offsets being committed only after database
  persistence.
  Idempotency: How to handle duplicate messages using Camel's Idempotent Consumer pattern (e.g.,
  using a unique message ID stored in a database or Redis cache).]

### Model B: [GPT-4o]
> [Question 1In a high-throughput Spring Boot application using Apache Camel, how do you prevent
  database bottlenecks when processing a massive influx of messages destined for a SQL
  database?]

---

## Scorecard

| Criterion | Model A score (1–3) | Model A evidence | Model B score (1–3) | Model B evidence |
|-----------|---------------------|------------------|---------------------|------------------|
| Accuracy | 3|Model A gets 3 because of more details and clarity in the questions | 2| odel B gets 2 because of
  lesser clarity in the questions|
| Relevance | 3|Claude questions are more relevant and aligned to the skills mentioned | 2|GPT questions are a bit vague |
| Difficulty level | 3| Claude difficulty level alignes with the experience and selection of the user|3 | GPT difficulty level also aligns with the user|
| Format compliance | 3| Claude format is more correct  it gives bullet points in the question|2 |GPT does not list options in bullet points |
| **Total** |12 |selected Claude as the questions were closely alighed with the user and his experience. The
  formatting of questions were also very apt for the user experience | 9|GPT was missing details and options in some cases |

---

## Decision

**Selected model:** [Claude]

**Rationale:** [selected Claude as the questions were closely alighed with the user and his experience. The
  formatting of questions were also very apt for the user experience]

---

## Active Constraint

**What could change this decision within 30 days:**
[Token budget cap should be actively looked at]

---

## Revision history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-06-24 | Initial commit |
