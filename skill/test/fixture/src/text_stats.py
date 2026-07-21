def count_words(text: str) -> dict:
    """Count words, lines, characters in text."""
    lines = text.splitlines()
    words = text.split()
    return {
        "lines": len(lines),
        "words": len(words),
        "chars": len(text),
    }

def process_file(path: str) -> dict:
    """Process a single file and return counts."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return count_words(text)

def process_files(paths: list[str]) -> dict:
    """Process multiple files and return combined counts."""
    total = {"lines": 0, "words": 0, "chars": 0}
    for p in paths:
        counts = process_file(p)
        total["lines"] += counts["lines"]
        total["words"] += counts["words"]
        total["chars"] += counts["chars"]
    return total