
import numpy as np
from .TableFormatters import TableFormatter

__all__ = [
    "format_tensor_element_table",
    "format_symmetric_tensor_elements",
    "format_mode_labels"
]

def format_tensor_element_table(inds, vals,
                                headers=("Indices", "Value"),
                                format="{:8.3f}",
                                column_join="|",
                                index_format="{:>5.0f}",
                                **etc
                                ):
    vals = np.asanyarray(vals)
    if vals.ndim == 1:
        vals = vals[:, np.newaxis]
    spans = [len(inds), vals.shape[-1]]
    return TableFormatter(
        column_formats=[index_format] * spans[0] + (
            [format] * spans[1]
                if isinstance(format, str) else
            format
        ),
        headers=headers,
        header_spans=spans,
        column_join=[""] * (spans[0]-1) + [column_join],
        **etc
    ).format(np.concatenate([np.array(inds).T, vals], axis=1))

def format_symmetric_tensor_elements(
        tensor,
        symmetries=None,
        cutoff=1e-6,
        headers=("Indices", "Value"),
        format="{:12.3f}",
        **etc
):
    tensor = np.asanyarray(tensor)
    if symmetries is None:
        symmetries = [np.arange(tensor.ndim)]

    symmetries = [np.sort(s) for s in symmetries]

    inds = np.where(np.abs(tensor) >= cutoff)
    if len(symmetries) > 0:
        inds_tests = [
            np.all(np.diff([inds[i] for i in symm], axis=0) >= 0, axis=0)
            for symm in symmetries
        ]
        inds_mask = np.all(inds_tests, axis=0)
        inds = tuple(x[inds_mask] for x in inds)

    vals = tensor[inds]

    return format_tensor_element_table(inds, vals, headers=headers, format=format, **etc)

def format_mode_labels(labels,
                       freqs=None,
                       high_to_low=True,
                       mode_index_format="{:.0f}",
                       frequency_format="{:.0f}",
                       headers=None,
                       column_join=" | ",
                       none_tag="mixed",
                       **etc
                       ):
    labels = [
        none_tag
            if lab.type is None else
        " ".join(t for t in lab.type if t is not None)
        for lab in labels
    ]

    if freqs is not None:
        return TableFormatter(
            [mode_index_format, frequency_format, "{}"],
            headers=("Mode", "Frequency", "Label") if headers is None else headers,
            column_join=column_join,
            **etc
        ).format([
            [i+1, f, lab]
            for i,(f,lab) in enumerate(zip(
                reversed(freqs) if high_to_low else freqs,
                reversed(labels) if high_to_low else labels
            ))
        ])
    else:
        return TableFormatter(
            [mode_index_format, "{}"],
            headers=("Mode", "Label") if headers is None else headers,
            column_join=column_join,
            **etc
        ).format([
            [i + 1, lab]
            for i, lab in enumerate(
                reversed(labels) if high_to_low else labels
            )
        ])