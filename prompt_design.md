# Prompt Design & Workflow Reasoning

This document explains the prompt engineering strategy, workflow orchestration design, hallucination prevention mechanisms, escalation logic, and conversational reasoning used in the Closira AI Support Workflow System.

The project was built for **Bloom Aesthetics Clinic** and supports four core workflow stages:

1. FAQ Answering
2. Lead Qualification
3. Escalation Detection
4. Conversation Summary Generation

The overall engineering goal was to build a deterministic, explainable, and operationally safe AI workflow system rather than a generic conversational chatbot.

---

# 1. Workflow-Oriented Prompting Philosophy

Instead of relying on one large autonomous system prompt, the project uses multiple narrowly scoped prompts:

| Workflow Stage       | Prompt Purpose                   |
| -------------------- | -------------------------------- |
| FAQ Answering        | SOP-grounded customer support    |
| Escalation Detection | Safety classification            |
| Summary Generation   | Structured operational summaries |

This design was intentionally chosen to improve:

* reliability
* explainability
* debugging simplicity
* output consistency
* hallucination control

The workflow architecture uses deterministic routing instead of autonomous agent loops.

---

# 2. FAQ Answering Prompt

## FAQ System Prompt

```text id="0jlwmu"
You are a professional and friendly customer support assistant for Bloom Aesthetics Clinic.

Your job is to answer customer questions ONLY using the provided SOP information.

Rules:
- Do not invent information.
- Do not assume services, pricing, or policies.
- If information is unavailable in the SOP, clearly state that you cannot confidently answer.
- Escalate if:
  - the question is medical
  - the customer is upset
  - the customer requests a human
  - the customer negotiates pricing
  - information is unavailable in the SOP

You must return ONLY valid raw JSON.

Required format:

{
  "response": "...",
  "confidence": 0.0,
  "sop_supported": true,
  "requires_escalation": false
}
```

---

## FAQ Prompt Design Decisions

The FAQ prompt was intentionally designed to be:

* deterministic
* concise
* operational
* easy to validate programmatically

The workflow prioritizes:

1. factual correctness
2. SOP grounding
3. escalation safety

over conversational creativity.

This reduces hallucination risk and improves reliability.

---

## SOP Context

The FAQ system operates on the following SOP information:

| Category     | SOP Data                |
| ------------ | ----------------------- |
| Business     | Bloom Aesthetics Clinic |
| Hours        | Mon–Sat, 9 am – 7 pm    |
| Botox        | From £200               |
| Fillers      | From £250               |
| Consultation | Free                    |
| Booking      | WhatsApp or website     |
| Cancellation | 24hr notice required    |

---

# 3. Hallucination Prevention

## SOP Grounding Strategy

The assistant is explicitly instructed to answer ONLY from the provided SOP.

The model is prohibited from:

* inventing services
* inventing pricing
* inventing medical guidance
* assuming unavailable policies

---

## Unsupported Question Handling

Example unsupported query:

```text id="5jlwmt"
Do you offer laser treatment?
```

Expected behavior:

1. avoid hallucinating an answer
2. reduce confidence score
3. set `sop_supported=false`
4. trigger escalation

---

## sop_supported Flag

Each FAQ response returns:

```json id="7jlwms"
{
  "sop_supported": true
}
```

or:

```json id="9jlwmd"
{
  "sop_supported": false
}
```

This field is used by the workflow engine to:

* identify unsupported questions
* trigger escalation logic
* improve downstream routing reliability

Structured outputs were intentionally chosen over free-form text because they are:

* easier to validate
* easier to debug
* easier to orchestrate

---

# 4. Confidence-Based Escalation

## Confidence Score Design

Every FAQ response includes:

```json id="1jlwmu"
{
  "confidence": 0.0
}
```

The LLM is explicitly instructed to self-report confidence based on:

* SOP support quality
* certainty of answer
* ambiguity level
* missing information

The confidence score ranges from:

* `0.0` → no confidence
* `1.0` → high confidence

---

## Escalation Threshold

Escalation is triggered when:

```python id="3jlwmt"
confidence < 0.5
```

This prevents unsupported or uncertain responses from being presented confidently to users.

---

## Additional Escalation Triggers

Escalation also occurs for:

* complaints
* angry sentiment
* medical questions
* pricing negotiation
* human handoff requests
* repeated unsupported questions

Examples:

```text id="5jlwms"
Can Botox affect pregnancy?
```

```text id="7jlwmd"
Your service is terrible.
```

```text id="9jlwmu"
Can you lower the Botox price?
```

---

# 5. Escalation Detection Prompt

## Escalation System Prompt

```text id="1jlwmt"
You are an escalation detection system.

Determine whether the customer message should be escalated.

Escalate for:
- complaints
- angry sentiment
- pricing negotiation
- medical questions
- requests for a human
- unsafe or uncertain situations

You must return ONLY raw JSON.

Format:

{
  "escalate": true,
  "reason": "medical_question",
  "confidence": 0.95
}
```

---

## Hybrid Escalation Architecture

The escalation workflow combines:

### Rule-Based Detection

Deterministic keyword detection for:

* medical terms
* complaints
* negotiation attempts
* human handoff requests

### Semantic LLM Classification

If no rule matches, the LLM performs semantic escalation analysis.

This hybrid architecture improves:

* reliability
* operational safety
* conversational flexibility

---

## Post-Escalation Customer Handling

When escalation occurs, the assistant responds politely and safely.

Example:

```text id="3jlwmp"
I’m escalating this conversation to a human support agent.
```

This avoids:

* unsafe autonomous handling
* speculative responses
* unsupported medical or operational advice

---

## Escalation Logging

Escalation reasons are stored in SQLite and logs.

Examples:

* medical_question
* complaint
* pricing_negotiation
* human_request

This improves:

* observability
* debugging
* future analytics support

---

# 6. Lead Qualification Design

## Qualification Workflow Philosophy

The qualification workflow was intentionally designed to feel conversational rather than aggressive.

The assistant does NOT immediately begin lead qualification after the first FAQ response.

Instead:

* users can ask multiple FAQ questions naturally
* qualification begins only after:

  * repeated engagement
  * consultation interest
  * booking intent

---

## Qualification Questions

The workflow collects:

* business type
* team size
* current tools/systems

Example flow:

```text id="4jlwmt"
Would you like to book a free consultation?
```

↓

```text id="6jlwms"
What type of business do you run?
```

↓

```text id="8jlwmd"
How large is your team?
```

---

## Why Qualification Is Deterministic

Qualification uses deterministic workflow state instead of autonomous reasoning because it improves:

* explainability
* state tracking
* conversational consistency
* debugging simplicity

---

# 7. Conversation Summary Prompt

## Summary System Prompt

```text id="0jlwmu"
You are a conversation summarization system.

Generate a structured summary of the customer support session.

You must return ONLY raw JSON.

Required format:

{
  "customer_intent": "...",
  "key_details_collected": {},
  "sop_gaps_identified": [],
  "escalation_reason": "...",
  "recommended_next_action": "..."
}

STRICT RULES:
- Include only factual information explicitly present in the conversation
- Do not analyze assistant behavior
- Do not critique workflow design
- Do not infer hidden intent
- Do not invent SOP gaps

Keep summaries concise and operational.
```

---

## Summary Design Goals

The summary workflow was designed to produce:

* operationally useful summaries
* structured outputs
* concise CRM-style session records

The summaries intentionally avoid:

* behavioral analysis
* speculative reasoning
* workflow critique

This keeps summaries practical and production-oriented.

---

# 8. Tone & Persona Design

## Communication Style

The assistant uses:

* professional language
* concise responses
* polite phrasing
* calm operational tone

The assistant avoids:

* overly casual language
* excessive empathy
* unsupported reassurance
* speculative medical advice

---

## Why This Tone Was Chosen

Bloom Aesthetics Clinic operates in a healthcare-adjacent aesthetics environment where customers expect:

* professionalism
* clarity
* trustworthiness
* calm communication

The tone was intentionally designed to reflect how a real SMB clinic support assistant would communicate.

---

# 9. Stage Transition Logic

## FAQ → Qualification Transition

The workflow does NOT force qualification immediately after the first FAQ response.

Instead:

* multiple FAQ interactions are allowed
* consultation offers appear contextually
* qualification begins only after customer engagement signals

Example:

```text id="5jlwmt"
What are your Botox prices?
```

↓

```text id="7jlwms"
What are your clinic hours?
```

↓

```text id="9jlwmd"
Would you like to book a free consultation?
```

This creates a more natural conversational experience.

---

## Continuous Escalation Monitoring

Escalation is NOT treated as a sequential stage.

Instead, escalation detection runs continuously on every user message.

This design was chosen because:

* complaints may occur at any point
* medical questions can appear unexpectedly
* human handoff requests are always high priority

This mirrors how production support systems handle safety monitoring.

---

# 10. Engineering Philosophy

This project intentionally avoids:

* autonomous agent loops
* unconstrained reasoning
* overly dynamic planning systems

Instead, it focuses on:

* deterministic orchestration
* structured outputs
* explainable workflow transitions
* operational safety
* conversational reliability

The final workflow architecture was designed to be:

* explainable
* testable
* production-oriented
* appropriate for real SMB customer support operations.
