import re


#Fixed source types used inside the app
#Users do not choose these directly; the app chooses them for the question
SOURCES_TYPE = ["official", "news", "web", "social_sentiment"]

#Fixed source usage roles.
#This tells the report generator how each source is allowed to be used
USE_AS_TYPES = ["fact", "background", "sentiment"]

def choose_source_types(question):
    #Decide which source types are needed based on the user's questions
    #Later we will replace the inside of this function with an ML or AI planner
    question_lower = question.lower()

    #Default baseline: most stock questions benefit from news and web context
    source_types = {"news", "web"}

    if any(word in question_lower for word in ["filing", "sec", "earnings", "guidance", "财报", "公告", "指引"]):
        source_types.add("official")

    social_keywords = [
        "sentiment", "reddit", "twitter", "forum", "stocktwits",
        "社交", "媒体", "情绪", "论坛"
    ]

    #Match X as a platform name without matching the x inside words like "explain".
    mentions_x = re.search(r"(?<![a-z0-9])x(?![a-z0-9])", question_lower) is not None

    if any(word in question_lower for word in social_keywords) or mentions_x:
        source_types.add("social_sentiment")

    return [
        source_type
        for source_type in SOURCES_TYPE
        if source_type in source_types
    ]

def retrieve_sources(ticker, question, source_types):
    #Later this function can call real web search/news/social APIs.
    # For now it returns fake sources using our internal source object format.
    sources = []

    if "official" in source_types:
        sources.append({
            "id": len(sources) + 1,
            "title": f"{ticker} mock official filing",
            "publisher": "Mock Official Source",
            "date": "2026-07-10",
            "url": "https://example.com/mock-official",
            "source_type": "official",
            "use_as": "fact",
            "summary": f"Mock official-source summary for {ticker}. This is only test data."
        })

    if "news" in source_types:
        sources.append({
            "id": len(sources) + 1,
            "title": f"{ticker} mock news source",
            "publisher": "Mock News",
            "date": "2026-07-10",
            "url": "https://example.com/mock-news",
            "source_type": "news",
            "use_as": "fact",
            "summary": f"Mock news summary for {ticker}. This is only test data."
        })

    if "web" in source_types:
        sources.append({
            "id": len(sources) + 1,
            "title": f"{ticker} mock web background source",
            "publisher": "Mock Web",
            "date": "2026-07-10",
            "url": "https://example.com/mock-web",
            "source_type": "web",
            "use_as": "background",
            "summary": f"Mock web background summary for {ticker}. This is only test data."
        })

    if "social_sentiment" in source_types:
        sources.append({
            "id": len(sources) + 1,
            "title": f"{ticker} mock social sentiment source",
            "publisher": "Mock Social",
            "date": "2026-07-10",
            "url": "https://example.com/mock-social",
            "source_type": "social_sentiment",
            "use_as": "sentiment",
            "summary": f"Mock social sentiment summary for {ticker}. This is only test data."
        })

    return sources


def format_sources_for_prompt(sources):
    # Tell the report generator clearly when no external sources were found.
    if not sources:
        return (
            "No external sources were retrieved.\n"
            "Do not make current, recent, news, or social sentiment claims."
        )

    source_blocks = []

    # Convert every internal source object into text the AI can read.
    for source in sources:
        source_block = (
            f"[{source['id']}]\n"
            f"Title: {source['title']}\n"
            f"Publisher: {source['publisher']}\n"
            f"Date: {source['date']}\n"
            f"URL: {source['url']}\n"
            f"Source type: {source['source_type']}\n"
            f"Use as: {source['use_as']}\n"
            f"Summary: {source['summary']}"
        )
        source_blocks.append(source_block)

    # Keep a blank line between sources so the prompt stays readable.
    return "\n\n".join(source_blocks)


def format_sources_section(sources):
    # Be explicit when the report has no external evidence.
    if not sources:
        return "## Sources\n\nNo external sources were retrieved."

    source_entries = []

    # Build the user-visible source list directly from source objects.
    for source in sources:
        source_entry = (
            f"[{source['id']}] {source['title']}\n"
            f"Publisher: {source['publisher']}\n"
            f"Date: {source['date']}\n"
            f"Source type: {source['source_type']}\n"
            f"URL: {source['url']}"
        )
        source_entries.append(source_entry)

    return "## Sources\n\n" + "\n\n".join(source_entries)
