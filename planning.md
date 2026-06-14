# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

UIUC CS professor reviews scraped from Rate My Professor (RMP), covering 10 professors across 8 courses including CS128, CS173, CS225, CS233, CS361, CS374, CS411, CS425, CS126, and STAT107. This knowledge is valuable because RMP data is not queryable; a student cannot ask "which CS professor is most exam-heavy" or "does Evans respond to students outside class" and get a direct answer. Official university channels provide no student opinion data at all.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Rate My Professors | Graham Evans — CS225, CS173 | ratemyprofessors.com/professor/2254924 |
| 2 | Rate My Professors | Michael Nowak — CS128 | ratemyprofessors.com/professor/2685082 |
| 3 | Rate My Professors | Craig Zilles — CS233 | ratemyprofessors.com/professor/877830 |
| 4 | Rate My Professors | Jeff Erickson — CS374 | ratemyprofessors.com/professor/180296 |
| 5 | Rate My Professors | Indranil Gupta — CS425 | ratemyprofessors.com/professor/831224 |
| 6 | Rate My Professors | Abdussalam Alawini — CS411 | ratemyprofessors.com/professor/2442487 |
| 7 | Rate My Professors | Hongye Liu — CS361 | ratemyprofessors.com/professor/2527253 |
| 8 | Rate My Professors | Kevin Chang — CS411 | ratemyprofessors.com/professor/1867625 |
| 9 | Rate My Professors | Lawrence Angrave — CS126 | ratemyprofessors.com/professor/1117293 |
| 10 | Rate My Professors | Wade Fagen — STAT107 | ratemyprofessors.com/professor/1815742 |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 1 review per chunk (approximately 100–400 characters)

**Overlap:** None

**Reasoning:** RMP reviews are already self-contained semantic units; each review expresses one student's complete opinion about one professor. Splitting mid-review would break the meaning (e.g., a review that opens with praise and closes with a warning becomes misleading if cut in half). Fixed character chunking would either merge multiple reviews together (losing attribution) or split a single review mid-sentence. Chunking by review boundary preserves each opinion as a retrievable, standalone fact. The professor name and course tag are prepended to each chunk so that retrieval can distinguish between Evans/CS225 and Evans/CS173 reviews within the same file.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers (local, no API key)

**Top-k:** 5

**Production tradeoff reflection:** For a production deployment I would evaluate text-embedding-3-small (OpenAI) for higher accuracy on short opinion text, and consider multilingual models like paraphrase-multilingual-MiniLM-L12-v2 if the corpus included non-English reviews. 

The main tradeoffs are cost (API-based models charge per token vs. local models run free), latency (local inference adds startup time but no network round trips), and context length (all-MiniLM-L6-v2 caps at 256 tokens, which is fine for short reviews but would be limiting for longer documents). 

For this corpus of short RMP reviews, all-MiniLM-L6-v2 is appropriate.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What do students say about Graham Evans's lectures in CS225? | Students consistently describe Evans's lectures as unhelpful and disengaging — many report skipping lecture and self-studying instead. Common complaints include blank or unclear slides and lectures irrelevant to MPs and exams. |
| 2 | Is CS374 with Jeff Erickson considered a difficult course? | Yes — students rate CS374 as highly difficult but praise Erickson's lectures and lecture notes as exceptional. The course is considered tough but worth it. |
| 3 | How does Wade Fagen approach teaching based on student reviews? | Students describe Fagen as energetic, passionate, and engaging — reviews are overwhelmingly positive. Note: all reviews in this corpus are for STAT107, not a CS course. |
| 4 | What are student complaints about Michael Nowak's CS128? | Students cite an overwhelming workload for a 3-credit course, harsh quiz grading that penalizes minor syntax errors, and a test-heavy structure. |
| 5 | Which CS411 professor do students prefer — Alawini or Chang? | System should retrieve reviews from both prof_6 and prof_8 and surface differences. Expected: Alawini has higher overall volume of positive reviews; Chang reviews mention research mentorship positively. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Off-domain retrieval from the STAT107 file: Wade Fagen's reviews all describe STAT107, not a CS course. Queries using generic teaching-quality language ("engaging lectures," "exam-heavy," "lots of homework") may retrieve STAT107 chunks because the embedding model has no course-domain awareness (it matches on teaching style vocabulary, not subject matter). This will surface as a failure case in evaluation question 3.

2. Review-level chunks may be too short for reliable semantic matching: Several reviews in the corpus are 1–2 sentences (e.g., "He was amazing!" or "You can tell he enjoys what he is doing"). These produce embeddings with very little semantic signal, which means similarity scores for these chunks will be noisy and they may outrank longer, more informative chunks on unrelated queries. This could cause the LLM to generate responses that technically cite a source but draw from a low-information chunk.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

Document Ingestion      Chunking               Embedding + Vector Store     Retrieval              Generation
──────────────────      ────────────────       ────────────────────────     ─────────────────      ──────────────────────
Load .txt files    →    Split by review    →   Embed with                →  Query ChromaDB    →    Groq llama-3.3-70b
from /Documents         boundary               all-MiniLM-L6-v2            top-k=5 chunks         with retrieved context
(plain text,            Prepend professor       Store in ChromaDB           + source metadata      Grounded prompt:
10 files)               name + course tag       with metadata               returned with           answer from docs only
                        to each chunk           (source filename,           each chunk             + cite source file
                                                professor, course)

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

I will give Claude my Documents section (file locations, format) and my Chunking Strategy section (chunk by review boundary, prepend professor + course tag). I will ask Claude to implement a load_and_chunk() function that reads each .txt file, splits on review boundaries, prepends metadata, and returns a list of chunk dictionaries with keys: text, source, professor, course. I will verify by printing 5 random chunks and confirming each is a complete review with metadata attached.

**Milestone 4 — Embedding and retrieval:**

I will give Claude my Retrieval Approach section and my Architecture diagram. I will ask Claude to implement an embed_and_store() function using SentenceTransformer("all-MiniLM-L6-v2") and ChromaDB, storing each chunk with its metadata. I will also ask for a retrieve() function that takes a query string and returns top-5 chunks with source filenames. I will verify by running 3 of my evaluation questions and checking that returned chunks are visibly relevant.

**Milestone 5 — Generation and interface:**

I will give Claude my grounding requirement (answers from retrieved context only, cite source file) and ask it to implement an ask() function that formats a prompt with retrieved chunks and calls Groq's llama-3.3-70b-versatile. I will also ask Claude to build a Gradio interface with a query input, answer output, and sources output. I will verify grounding by asking a question my documents don't cover and confirming the system declines to answer.