# pipeline-viz

`hf_pipeline_viz` is a python helper that lets you peek inside a Hugging Face *text-generation* pipeline and see which context tokens the model attends to for every new word it writes.

Why you might care:

* **Model interpretability** – spot “sink” heads, long-range dependencies, or where a layer shifts focus from syntax to semantics.
* **Prompt engineering & debugging** – confirm the model is actually reading the parts of the prompt you think are important.
* **Teaching & demos** – a single screenshot often explains causal masking better than a paragraph of text.

## Installation

```bash
pip install hf_pipeline_viz
```
## Quick start

```python
from transformers import pipeline
from hf_pipeline_viz import viz_generate

pipe = pipeline("text-generation", model="openai-community/gpt2-large")

prompt = "The secret to making a good cake is "
viz_generate(pipe, prompt, max_new_tokens=20)
```

A heat-map is generated; each row is a freshly generated token, each column a context token.  Bright squares = high averaged attention.

## Fine control

```python
# average only layer 11 over all heads
viz_generate(pipe, prompt, layers=11)

# average layers 8 & 11, but keep heads 0,3,7
viz_generate(pipe, prompt, layers=[8,11], heads=[0,3,7])

# last four layers, single head 5
viz_generate(pipe, prompt, layers=[-4,-3,-2,-1], heads=5,
                savefile="attn.png")
```

Negative indices follow Python slicing rules (`-1` = last layer/head).