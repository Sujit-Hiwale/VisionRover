from ddgs import DDGS

import time

import smallFaces
import speak

# =====================================
# SUMMARIZER
# =====================================

def summarize(
    text,
    max_sentences=2
):

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

# =====================================
# SEARCH
# =====================================

def assistant_search(
    query,
    voice=False
):

    try:

        print(
            f"🌐 Searching: {query}"
        )

        # =================================
        # FACE
        # =================================

        try:

            smallFaces.searching()

        except:
            pass

        time.sleep(0.3)

        # =================================
        # SEARCH
        # =================================

        results = []

        with DDGS() as ddgs:

            results = list(

                ddgs.text(

                    query,

                    max_results=3
                )
            )

        print(
            f"📦 Results: {len(results)}"
        )

        # =================================
        # NO RESULTS
        # =================================

        if not results:

            try:
                smallFaces.not_found()
            except:
                pass

            if voice:

                try:
                    speak.speak(
                        "No results found"
                    )
                except:
                    pass

            return "No results found."

        # =================================
        # BEST RESULT
        # =================================

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

        summary = summarize(body)

        answer = (

            f"{title}\n\n"

            f"{summary}"
        )

        # =================================
        # FOUND FACE
        # =================================

        try:

            smallFaces.found()

        except:
            pass

        # =================================
        # SPEAK
        # =================================

        if voice:

            try:

                speak.speak(summary)

            except Exception as e:

                print(
                    f"Speak failed: {e}"
                )

        else:

            try:

                time.sleep(1)

                smallFaces.neutral()

            except:
                pass

        return answer

    except Exception as e:

        print(
            f"❌ Search Error: {e}"
        )

        try:

            smallFaces.angry()

        except:
            pass

        if voice:

            try:

                speak.speak(
                    "Internet search failed"
                )

            except:
                pass

        return f"Error: {e}"