"""Chain format I/O support."""

import gzip
from typing import Union, Optional
from pathlib import Path

from ..core.genome_alignment import GenomeAlignmentsCollection
from .._chainparser import parse_many_chain_chunks


def read_chain_file(file_path: Union[str, Path],
                    min_score: Optional[int] = None) -> GenomeAlignmentsCollection:
    file_path = Path(file_path)
    is_gzipped = file_path.suffix.lower() == '.gz'
    if is_gzipped:
        with gzip.open(file_path, 'rb') as f:
            content = f.read()
    else:
        with file_path.open("rb") as f:
            content = f.read()
    
    parts = content.split(b"chain ")
    chunks = [b"chain " + part.strip() for part in parts[1:] if len(part.strip()) > 10]

    if min_score is not None:
        alignments = parse_many_chain_chunks(chunks, min_score)
    else:
        alignments = parse_many_chain_chunks(chunks)
    
    return GenomeAlignmentsCollection(alignments=alignments, source_file=str(file_path))
