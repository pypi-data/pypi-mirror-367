from typing import Sequence, Union
import numpy as np
import torch
import matplotlib.pyplot as plt
from transformers import Pipeline


def _normalize_to_list(x, size: int, name: str) -> list[int]:
    """Turn int / iterable / 'all' into a validated list of indices."""
    if x is None or x == "all":
        return list(range(size))
    if isinstance(x, (int, np.integer)):
        x = [int(x)]
    if isinstance(x, Sequence):
        idxs = [i if i >= 0 else size + i for i in x]
        bad = [i for i in idxs if i < 0 or i >= size]
        if bad:
            raise ValueError(f"{name} index out of range: {bad}")
        return idxs
    raise TypeError(f"{name} must be int, list[int] or 'all'; got {x!r}")


def viz_generate(
    pipe: Pipeline,
    prompt: str,
    *,
    max_new_tokens: int = 30,
    layers: Union[int, Sequence[int], str] = -1,
    heads: Union[int, Sequence[int], str] = "all",
    savefile: str | None = None,
) -> str:
    """
    Generate text *and* show/save a heat-map of averaged attentions.

    Parameters
    ----------
    pipe
        A Hugging Face text-generation pipeline.
    prompt
        The prompt string.
    max_new_tokens
        Number of tokens to generate.
    layers
        One layer index, a list of indices, or 'all'.  Negatives allowed.
    heads
        Same idea, but for attention heads.
    savefile
        Path to save PNG; if ``None`` the figure is shown instead.

    Returns
    -------
    Full generated text (prompt + continuation).
    """
    # 1. run generation with attentions captured
    out = pipe.model.generate(
        **pipe.tokenizer(prompt, return_tensors="pt"),
        max_new_tokens=max_new_tokens,
        return_dict_in_generate=True,
        output_attentions=True,
    )

    full_ids = out.sequences[0]  # (seq_len,)
    tokens = [pipe.tokenizer.decode(i) for i in full_ids.tolist()]

    n_layers = len(out.attentions[0])
    n_heads = out.attentions[0][0].shape[1]

    layer_idxs = _normalize_to_list(layers, n_layers, "layer")
    head_idxs = _normalize_to_list(heads, n_heads, "head")

    # 2. collect per-token vectors averaged over chosen layers & heads
    rows = []
    for step_attn in out.attentions:  # one tuple per generated token
        sel_layers = torch.stack([step_attn[i] for i in layer_idxs])  # (L,1,H,1,K)
        sel_heads = sel_layers[:, 0, head_idxs, 0, :]                 # (L,H,K)
        vec = sel_heads.mean(dim=(0, 1))                              # (K,)
        rows.append(vec.cpu().numpy())

    # 3. pad ragged rows into rectangle
    seq_len = len(tokens)
    heat = np.full((len(rows), seq_len), np.nan, dtype=np.float32)
    for i, v in enumerate(rows):
        heat[i, : v.size] = v
    heat = np.nan_to_num(heat, nan=0.0)

    gen_tokens = tokens[-len(rows) :]  # y-labels

    # 4. plot
    plt.figure(figsize=(seq_len * 0.45, len(rows) * 0.35))
    plt.imshow(heat, cmap="magma", aspect="auto")
    plt.xticks(range(seq_len), tokens, rotation=90, fontsize=8)
    plt.yticks(range(len(rows)), gen_tokens, fontsize=8)

    lay_tag = ",".join(str(i if i >= 0 else n_layers + i) for i in layer_idxs)
    head_tag = ",".join(str(h) for h in head_idxs)
    plt.title(f"Layers {lay_tag} - Heads {head_tag} (avg)")
    plt.xlabel("Context tokens so far")
    plt.ylabel("Generated token")
    plt.colorbar(label="attention weight")
    plt.tight_layout()

    if savefile:
        plt.savefig(savefile)
    else:
        plt.show()
    plt.close()

    return pipe.tokenizer.decode(full_ids, skip_special_tokens=True)