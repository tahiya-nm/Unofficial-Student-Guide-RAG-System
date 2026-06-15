# The Unofficial UIUC CS Professor Guide 

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

UIUC CS professor reviews collected from Rate My Professors, covering 10 professors across 8 courses including CS126, CS128, CS173, CS225, CS233, CS361, CS374, CS411, CS425, and STAT107. This knowledge is valuable because RMP data is not queryable — a student cannot ask "which CS professor is most exam-heavy" or "does Evans respond to students outside class" and get a direct answer. Official university channels provide no student opinion data at all, making this kind of peer knowledge effectively invisible unless you manually read hundreds of individual reviews.

---

## Demo Video

https://github.com/user-attachments/assets/c6033564-3b48-480d-8570-a2c2937a3a1b

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Rate My Professors — Graham Evans | Plain text | ratemyprofessors.com/professor/2254924 / Documents/prof_1_review.txt |
| 2 | Rate My Professors — Craig Zilles | Plain text | ratemyprofessors.com/professor/877830 / Documents/prof_2_review.txt |
| 3 | Rate My Professors — Michael Nowak | Plain text | ratemyprofessors.com/professor/2685082 / Documents/prof_3_review.txt |
| 4 | Rate My Professors — Jeff Erickson | Plain text | ratemyprofessors.com/professor/180296 / Documents/prof_4_review.txt |
| 5 | Rate My Professors — Indranil Gupta | Plain text | ratemyprofessors.com/professor/831224 / Documents/prof_5_review.txt |
| 6 | Rate My Professors — Abdussalam Alawini | Plain text | ratemyprofessors.com/professor/2442487 / Documents/prof_6_review.txt |
| 7 | Rate My Professors — Hongye Liu | Plain text | ratemyprofessors.com/professor/2527253 / Documents/prof_7_review.txt |
| 8 | Rate My Professors — Kevin Chang | Plain text | ratemyprofessors.com/professor/1867625 / Documents/prof_8_review.txt |
| 9 | Rate My Professors — Lawrence Angrave | Plain text | ratemyprofessors.com/professor/1117293 / Documents/prof_9_review.txt |
| 10 | Rate My Professors — Wade Fagen | Plain text | ratemyprofessors.com/professor/1815742 / Documents/prof_10_review.txt |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** One review per chunk (approximately 100–400 characters of review text)

**Overlap:** None

**Why these choices fit your documents:** RMP reviews are already self-contained semantic units — each review expresses one student's complete opinion about one professor in one course. Splitting mid-review would break meaning; a review that opens with praise and closes with a warning becomes misleading if cut in half. Fixed character chunking would either merge multiple reviews together (losing per-review attribution) or split a single review mid-sentence. Chunking by review boundary preserves each opinion as a standalone, retrievable fact. The professor name and course tag are prepended to each chunk so retrieval can distinguish between Evans/CS225 and Evans/CS173 reviews within the same file. The header block of each file (overall rating, would-take-again percentage, difficulty score) was retained as context preceding the first review chunk.

**Final chunk count:** 195 chunks across 10 files

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** all-MiniLM-L6-v2 via sentence-transformers (local, no API key required). Embeddings are stored in a persistent ChromaDB collection using cosine similarity.

**Production tradeoff reflection:** For a production deployment I would evaluate text-embedding-3-small (OpenAI) for higher accuracy on short opinion text — it handles informal, colloquial language better than general-purpose models. I would also consider paraphrase-multilingual-MiniLM-L12-v2 if the corpus included non-English reviews. The main tradeoffs are cost (API-based models charge per token vs. local models run free), latency (local inference avoids network round trips but adds startup time), and context length (all-MiniLM-L6-v2 caps at 256 tokens, which is appropriate for short reviews but would be limiting for longer documents like syllabi or handbooks). For this corpus of short RMP reviews, all-MiniLM-L6-v2 is appropriate and avoids any dependency on external APIs.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** The system prompt explicitly instructs the model to answer using only the information in the provided documents and to decline with a fixed phrase if the documents do not contain enough information: "If the documents do not contain enough information to answer, respond exactly with: 'I don't have enough information on that based on the available reviews.'" Temperature is set to 0.1 to reduce hallucination risk. Each chunk passed to the model is prefixed with its source filename in the format `[prof_1_review.txt]`, and the full chunk text including the prepended professor and course metadata is included so the model has complete attribution context.

**How source attribution is surfaced in the response:** Source filenames are surfaced in two ways. First, the model is instructed to list the source file(s) it drew from at the end of its answer under a "Sources:" line. Second, the Gradio interface displays a separate "Retrieved from" box populated programmatically from the chunk metadata returned by ChromaDB — this is independent of the model's output and guaranteed to be accurate regardless of how the model formats its response.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about Graham Evans's lectures in CS225? | Students describe lectures as unhelpful and disengaging, citing blank slides and irrelevance to MPs and exams | Described lectures as "very boring," "awful," and "irrelevant to MPs and exams"; cited blank slides, spelling mistakes, and reviewers recommending self-study | Relevant — only `prof_1_review.txt` retrieved | Accurate |
| 2 | Is CS374 with Jeff Erickson considered a difficult course? | Yes — highly difficult but praised for exceptional lecture notes | Correctly identified as difficult and test-heavy with varying ratings (3.0–5.0); did not surface praise for Erickson's notes | Partially relevant — `prof_1_review.txt` (Evans/CS173) retrieved alongside correct file due to shared difficulty vocabulary | Partially accurate |
| 3 | How does Wade Fagen approach teaching based on student reviews? | Students describe Fagen as energetic, passionate, and engaging; note all reviews are for STAT107, not a CS course | Accurately described Fagen as passionate and engaging with interactive lectures; drew entirely from STAT107 reviews | Partially relevant — correct professor file retrieved, but all reviews are for STAT107, not a CS course | Partially accurate |
| 4 | What are student complaints about Michael Nowak's CS128? | Confusing prompts, poor lectures, all-or-nothing quiz grading, test-heavy structure | Accurately identified all major complaint categories including confusing prompts, script-reading lectures, all-or-nothing quizzes, and unhelpful documentation | Relevant — only `prof_3_review.txt` retrieved | Accurate |
| 5 | Which CS411 professor do students prefer — Alawini or Chang? | Hypothesis: Alawini has more positive reviews; Chang reviews mention research mentorship | Concluded students prefer Chang based on retrieved reviews; Alawini reviews included a "avoid at all costs" warning | Relevant — both `prof_6_review.txt` and `prof_8_review.txt` retrieved | Accurate — original expected answer was a pre-corpus hypothesis that the system correctly contradicted |


**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** Q2 — Is CS374 with Jeff Erickson considered a difficult course? and Q3 — How does Wade Fagen approach teaching based on student reviews?

**What the system returned:** For Q2, the system retrieved `prof_1_review.txt` (Graham Evans, CS173) as one of the top-5 chunks alongside the correct Erickson file. For Q3, the system correctly retrieved `prof_10_review.txt` but all reviews in that file are for STAT107, not a CS course — the query asked specifically about CS courses.

**Root cause (tied to a specific pipeline stage):** Both failures occur at the retrieval stage. For Q2, the embedding model matches on teaching-style vocabulary ("difficult," "test-heavy," "exam-focused") rather than professor or course identity — CS173 reviews share enough semantic overlap with a CS374 difficulty query to rank in the top 5. For Q3, the embedding model matches on teaching-quality vocabulary ("passionate," "engaging," "lectures") regardless of course domain, so STAT107 reviews are indistinguishable from CS course reviews at the vector level. Neither failure is a generation failure — the LLM answered correctly from what it was given. The root cause in both cases is that all-MiniLM-L6-v2 has no awareness of course domain as a semantic category.

**What you would change to fix it:** For Q2, increasing top-k and adding a re-ranking step that weights professor name matches more heavily would reduce off-domain bleed. For Q3, metadata filtering at retrieval time — restricting results to chunks where the course field starts with "CS" — would prevent STAT107 chunks from being retrieved for CS-specific queries entirely.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** Writing the chunking strategy section before touching any code forced a decision about review boundaries that directly shaped the `parse_reviews_from_file()` implementation. Because the spec explicitly stated "chunking by review boundary preserves each opinion as a retrievable standalone fact," the regex split pattern in `ingestion.py` was written to match that exact boundary (`\n\nQuality\n`) rather than using a generic character-count splitter. Without the spec, the default choice would likely have been a fixed 500-character split, which would have merged multiple reviews into single chunks and broken per-review attribution.

**One way your implementation diverged from the spec, and why:** The spec assumed all 10 documents would be clean after removing the header block. In practice, `prof_3_review.txt` contained a UI artifact (`Computer Icon`) prepended to every course code, which caused the course extraction regex to return "Unknown" for all Nowak chunks. This required a targeted fix — stripping the artifact string before the regex match — that was not anticipated in planning. Additionally, the spec did not anticipate that Wade Fagen's RMP page would contain exclusively STAT107 reviews rather than CS course reviews, which became the primary planned failure case rather than a generic noise issue.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* My Chunking Strategy section from planning.md (chunk by review boundary, prepend professor and course tag, return list of dicts with keys text/source/professor/course) and my Documents section listing the 10 .txt files in the Documents/ folder.
- *What it produced:* A complete `ingestion.py` with `extract_professor_name()`, `extract_course()`, `parse_reviews_from_file()`, and `load_and_chunk()` functions using a regex split on `\n\nQuality\n` to detect review boundaries.
- *What I changed or overrode:* The initial `extract_course()` regex used a word boundary (`\b`) which failed to match course codes prefixed with the `Computer Icon` UI artifact in `prof_3_review.txt`. I directed Claude to fix it by stripping the artifact string before the regex match rather than relying on the boundary anchor.

**Instance 2**

- *What I gave the AI:* My Retrieval Approach section (all-MiniLM-L6-v2, ChromaDB, top-k=5, metadata includes source/professor/course) and my Architecture diagram.
- *What it produced:* A complete `retrieval.py` with `embed_and_store()` and `retrieve()` functions, using a persistent ChromaDB client with cosine similarity and a skip-if-populated guard to avoid re-embedding on every run.
- *What I changed or overrode:* The initial version loaded `SentenceTransformer` inside the `retrieve()` function, which re-instantiated the model on every query call and would have made the Gradio interface slow. I directed Claude to move the model instantiation to module level so it loads once per session.
