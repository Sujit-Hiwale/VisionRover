from ddgs import DDGS
import time

import smallFaces
import speak

# ---------------------------------
# SUMMARIZER
# ---------------------------------

def summarize(text, max_sentences=2):

    if not text:

        return "No summary available."

    sentences = [

        s.strip()

        for s in text.split('.')

        if s.strip()
    ]

    summary = '. '.join(
        sentences[:max_sentences]
    )

    if summary:
        summary += '.'

    return summary

# ---------------------------------
# ASSISTANT SEARCH
# ---------------------------------

def assistant_search(
    query,
    voice=False
):

    try:

        print(
            f"🌐 Searching: {query}"
        )

        # =====================================
        # SEARCHING FACE
        # =====================================

        smallFaces.searching()

        time.sleep(0.3)

        # =====================================
        # SEARCH WEB
        # =====================================

        results = []

        with DDGS() as ddgs:

            results = list(

                ddgs.text(
                    query,
                    max_results=3
                )
            )

        print(
            f"📦 Results Found: "
            f"{len(results)}"
        )

        # =====================================
        # NO RESULTS
        # =====================================

        if not results:

            print(
                "❌ No results found"
            )

            smallFaces.not_found()

            if voice:

                speak.speak(
                    "No results found"
                )

            return "No results found."

        # =====================================
        # FIND BEST RESULT
        # =====================================

        top = None

        for result in results:

            body = result.get(
                "body",
                ""
            )

            if len(body) > 30:

                top = result

                break

        if top is None:

            top = results[0]

        title = top.get(
            "title",
            "No title"
        )

        body = top.get(
            "body",
            ""
        )

        print(
            f"📰 Title: {title}"
        )

        print(
            f"📄 Body: {body}"
        )

        # =====================================
        # SUMMARIZE
        # =====================================

        summary = summarize(body)

        answer = (
            f"{title}\n\n"
            f"{summary}"
        )

        # =====================================
        # FOUND FACE
        # =====================================

        smallFaces.found()

        # =====================================
        # SPEAK
        # =====================================

        if voice:

            print(
                "🗣️ Speaking result"
            )

            speak.speak(summary)

        else:

            # Return to neutral only if not speaking
            time.sleep(1)

            smallFaces.neutral()

        return answer

    except Exception as e:

        print(
            f"❌ Search Error: {e}"
        )

        # =====================================
        # ERROR FACE
        # =====================================

        smallFaces.angry()

        if voice:

            try:

                speak.speak(
                    "Internet search failed"
                )

            except Exception as speak_error:

                print(
                    f"Speak error: "
                    f"{speak_error}"
                )

        else:

            time.sleep(1)

            smallFaces.neutral()

        return f"Error: {e}"