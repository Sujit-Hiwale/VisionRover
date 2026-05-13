from ddgs import DDGS
import subprocess
import time
import smallFaces
import speak

# ---------------------------------
# Simple Summarizer
# ---------------------------------

def summarize(text, max_sentences=2):

    sentences = text.split(". ")

    summary = ". ".join(sentences[:max_sentences])

    return summary


# ---------------------------------
# Assistant Search
# ---------------------------------

def assistant_search(query, voice=False):

    try:

        # Searching face
        smallFaces.searching()

        # Search web
        results = list(
            DDGS().text(query, max_results=1)
        )

        if not results:

            smallFaces.not_found()

            return "No results found."

        top = results[0]

        title = top.get("title", "")
        body = top.get("body", "")

        # Summarize result
        summary = summarize(body)

        answer = f"{title}\n\n{summary}"

        # Found expression
        smallFaces.found()

        # Speak summary
        if voice:
            speak.speak(summary)

        else:
            time.sleep(1)
            smallFaces.neutral()

        return answer

    except Exception as e:

        # Error face
        smallFaces.angry()

        return f"Error: {e}"