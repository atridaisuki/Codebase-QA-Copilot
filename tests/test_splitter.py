from app.schemas import DocumentRecord
from app.services.text_splitter import TextSplitter


def test_splitter_prefers_paragraph_boundaries_and_tracks_metadata() -> None:
    document = DocumentRecord(
        source="sample.md",
        content="# Title\nIntro line.\n\n## Details\nLine one.\nLine two.\n\nTail paragraph.",
        file_type="md",
    )

    splitter = TextSplitter(chunk_size=80, chunk_overlap=10)
    chunks = splitter.split_documents([document])

    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk.content == "# Title\nIntro line.\n\n## Details\nLine one.\nLine two.\n\nTail paragraph."
    assert chunk.chunk_index == 0
    assert chunk.start_offset == 0
    assert chunk.end_offset == len(document.content)
    assert chunk.title == "Title"
    assert chunk.section == "Title"


def test_splitter_falls_back_to_overlapping_windows_for_long_segments() -> None:
    document = DocumentRecord(
        source="sample.txt",
        content="abcdefghij",
        file_type="txt",
    )

    splitter = TextSplitter(chunk_size=4, chunk_overlap=1)
    chunks = splitter.split_documents([document])

    assert [chunk.content for chunk in chunks] == ["abcd", "defg", "ghij"]
    assert [chunk.chunk_index for chunk in chunks] == [0, 1, 2]
    assert [(chunk.start_offset, chunk.end_offset) for chunk in chunks] == [(0, 4), (3, 7), (6, 10)]


def test_splitter_generates_stable_chunk_ids() -> None:
    document = DocumentRecord(
        source="stable.txt",
        content="Paragraph one.\n\nParagraph two.",
        file_type="txt",
    )

    splitter = TextSplitter(chunk_size=40, chunk_overlap=5)

    first = splitter.split_documents([document])
    second = splitter.split_documents([document])

    assert [chunk.id for chunk in first] == [chunk.id for chunk in second]
