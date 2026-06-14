# Milestone 5 — Gradio Query Interface
#
# Summary:
#   Launches a local web UI at http://localhost:7860
#   Input:  a plain-language question about UIUC CS professors
#   Output: a grounded answer (from retrieved reviews only) + source file list
#
# Run with: python3 app.py

import gradio as gr
from generation import ask


def handle_query(question):
    """
    Handler called by Gradio on button click or Enter.
    Returns (answer_text, sources_text) for the two output boxes.
    """
    # Guard against empty input
    if not question.strip():
        return "Please enter a question.", ""

    result = ask(question)

    # Format source list as bullets for the sources box
    sources_text = "\n".join(f"• {s}" for s in result["sources"])

    return result["answer"], sources_text


# --- Gradio UI ---
with gr.Blocks(title="Unofficial UIUC CS Guide") as demo:
    gr.Markdown("# 📚 Unofficial UIUC CS Professor Guide")
    gr.Markdown(
        "Ask questions about UIUC CS professors based on student reviews from Rate My Professors. "
        "Answers are grounded in the review documents only."
    )

    inp = gr.Textbox(
        label="Your question",
        placeholder="e.g. What do students say about Evans's lectures in CS225?"
    )

    btn = gr.Button("Ask", variant="primary")

    answer_box = gr.Textbox(label="Answer", lines=10)
    sources_box = gr.Textbox(label="Retrieved from", lines=4)

    # Trigger on button click or pressing Enter in the input box
    btn.click(handle_query, inputs=inp, outputs=[answer_box, sources_box])
    inp.submit(handle_query, inputs=inp, outputs=[answer_box, sources_box])

demo.launch()