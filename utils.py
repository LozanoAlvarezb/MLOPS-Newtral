from typing import Iterable, Optional


def join_docs(docs: list[str], separator: str) -> Optional[str]:
    text = separator.join(docs)
    text = text.strip()
    if text == "":
        return None
    else:
        return text


def merge_splits(
    splits: Iterable[str],
    chunk_size: int,
    chunk_overlap: int,
    separator: str,
) -> list[str]:
    # We now want to combine these smaller pieces into medium size
    # chunks to send to the LLM.
    separator_len = len(separator)

    docs = []
    current_doc: list[str] = []
    total = 0
    for d in splits:
        _len = len(d)
        if total + _len + (separator_len if len(current_doc) > 0 else 0) > chunk_size:
            if total > chunk_size:
                print(
                    f"Created a chunk of size {total}, "
                    f"which is longer than the specified {chunk_size}"
                )
            if len(current_doc) > 0:
                doc = join_docs(current_doc, separator)
                if doc is not None:
                    docs.append(doc)
                # Keep on popping if:
                # - we have a larger chunk than in the chunk overlap
                # - or if we still have any chunks and the length is long
                while total > chunk_overlap or (
                    total + _len + (separator_len if len(current_doc) > 0 else 0)
                    > chunk_size
                    and total > 0
                ):
                    total -= len(current_doc[0]) + (
                        separator_len if len(current_doc) > 1 else 0
                    )
                    current_doc = current_doc[1:]
        current_doc.append(d)
        total += _len + (separator_len if len(current_doc) > 1 else 0)
    doc = join_docs(current_doc, separator)
    if doc is not None:
        docs.append(doc)
    return docs


def split_text(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
    separators: list[str],
) -> list[str]:
    """Split incoming text and return chunks."""
    final_chunks = []
    # Get appropriate separator to use
    for _s in separators:
        if _s == "":
            separator = _s
            break
        if _s in text:
            separator = _s
            break
    # Now that we have the separator, split the text
    if separator:
        splits = text.split(separator)
    else:
        splits = list(text)
    # Now go merging things, recursively splitting longer texts.
    _good_splits = []
    for s in splits:
        if len(s) < chunk_size:
            _good_splits.append(s)
        else:
            if _good_splits:
                merged_text = merge_splits(
                    _good_splits,
                    chunk_size,
                    chunk_overlap,
                    separator,
                )
                final_chunks.extend(merged_text)
                _good_splits = []
            other_info = split_text(s)
            final_chunks.extend(other_info)
    if _good_splits:
        merged_text = merge_splits(
            _good_splits,
            chunk_size,
            chunk_overlap,
            separator,
        )
        final_chunks.extend(merged_text)
    return final_chunks
