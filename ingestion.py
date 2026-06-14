# Milestone 3 — Document Ingestion and Chunking
#
# Summary of steps:
#   1. Read each .txt file from the Documents/ folder
#   2. Extract professor name from the file header
#   3. Split file content into individual review blocks (one review = one chunk)
#   4. Prepend professor name and course tag to each chunk per planning.md spec
#   5. Return a flat list of chunk dicts: {text, source, professor, course}
#
# Time complexity:  O(n) where n = total characters across all files
# Space complexity: O(k) where k = total number of review chunks produced

import os
import re
import random

DOCS_FOLDER = "Documents"


def extract_professor_name(header_text):
    """
    Extract professor name from the RMP header block.
    The professor name is the first non-empty line after
    'Overall Quality Based on X ratings'.
    """
    lines = header_text.strip().split('\n')
    for i, line in enumerate(lines):
        if 'Overall Quality Based on' in line:
            for j in range(i + 1, len(lines)):
                candidate = lines[j].strip()
                # Skip the department description line, grab the name
                if candidate and not candidate.startswith('Professor in'):
                    return candidate
    return "Unknown Professor"


def extract_course(review_block):
    """
    Extract course code (e.g. CS225, STAT107) from a single review block.
    Course code appears as 2-4 uppercase letters followed by 3 digits.
    """
    match = re.search(r'([A-Z]{2,4}\d{3})', review_block.replace('Computer Icon', ''))
    return match.group(1) if match else "Unknown"


def parse_reviews_from_file(filepath):
    """
    Load one .txt file and return one chunk dict per review.
    Each chunk: {text, source, professor, course}
    Splits on review boundaries (blank line before 'Quality' line).
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the start of the first review block (first standalone 'Quality' line)
    first_review = re.search(r'(?m)^Quality$', content)
    if not first_review:
        print(f"  Warning: no reviews found in {filepath}")
        return []

    # Everything before the first review is the header
    header = content[:first_review.start()]
    reviews_section = content[first_review.start():]

    professor = extract_professor_name(header)
    source = os.path.basename(filepath)

    # Split into individual reviews on blank line + 'Quality' boundary
    # Each review starts with 'Quality\n' — re.split removes the delimiter,
    # so we add it back to every block after the first
    raw_blocks = re.split(r'\n\nQuality\n', reviews_section)

    chunks = []
    for i, block in enumerate(raw_blocks):
        if i > 0:
            block = "Quality\n" + block  # restore stripped delimiter
        block = block.strip()
        if not block:
            continue

        course = extract_course(block)

        # Prepend metadata so retrieval can distinguish professor + course
        # (per planning.md chunking strategy)
        full_text = f"Professor: {professor} | Course: {course}\n{block}"

        chunks.append({
            "text": full_text,
            "source": source,
            "professor": professor,
            "course": course
        })

    return chunks


def load_and_chunk():
    """
    Load all .txt files from Documents/ and return a flat list of chunk dicts.
    Prints per-file chunk counts and a total for verification.
    """
    all_chunks = []

    for filename in sorted(os.listdir(DOCS_FOLDER)):
        if not filename.endswith('.txt'):
            continue
        filepath = os.path.join(DOCS_FOLDER, filename)
        chunks = parse_reviews_from_file(filepath)
        all_chunks.extend(chunks)
        print(f"  {filename}: {len(chunks)} chunks")

    print(f"\nTotal chunks: {len(all_chunks)}")
    return all_chunks


if __name__ == "__main__":
    print("Loading and chunking documents...\n")
    chunks = load_and_chunk()

    # Verification: print 5 random chunks and inspect manually
    # Each chunk should be a complete review with professor + course metadata
    print("\n--- 5 Random Chunks for Verification ---\n")
    for i, chunk in enumerate(random.sample(chunks, min(5, len(chunks))), 1):
        print(f"[Chunk {i}]")
        print(f"  Source:    {chunk['source']}")
        print(f"  Professor: {chunk['professor']}")
        print(f"  Course:    {chunk['course']}")
        print(f"  Text preview:\n    {chunk['text'][:300]}")
        print()