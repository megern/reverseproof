# ReverseProof

A local, evidence-bound prototype for testing reverse-engineering hypotheses, by Megern Qaisse.

The current prototype combines **original BF16 Qwen3-0.6B running offline**, macOS ARM64 disassembly, a strict proposal boundary and an independent behavioral verifier. A model's explanation is never automatically treated as a verified result.

## Measured results

| Experiment | Local model output | Independent outcome |
|---|---|---|
| Initial prompt, four related owned fixtures | Four invalid claim schemas | Four rejected responses |
| Explicit schema example, same fixtures | Three invalid responses; one valid but wrong hypothesis | Three rejected; one refuted by execution |

The model copied arbitrary numbers from the schema example. **No correct model interpretation was demonstrated.** Both rounds and raw outputs are retained under `results/local-v1` and `results/local-v2`. These are tiny development smoke tests, not held-out benchmarks. The second prompt was written after observing the first failures. Neither round used the original source or oracle outcomes in the model prompt; the restricted clamp schema still supplies substantial task information.

A separate exact ARM64 instruction-pattern baseline derives bounds from two observed compiler signatures and can abstain on other code. Its first smoke study supported two clamp fixtures and abstained on three fixtures; after adding the second observed signature, its second smoke study supported all four clamp fixtures on 131 inputs each and abstained on the affine negative. Both rounds are retained under `results/pattern-v1` and `results/pattern-v2`. This is a post-run development comparison using related, already-seen functions. It is intentionally narrow, developed from these fixtures, and is not a general decompiler, novel algorithm or a fair held-out superiority benchmark.

## Run on macOS

No cloud service, API key or network request is used at runtime. macOS Command Line Tools and Python 3.10+ are required for the owned C demo. Local model inference additionally requires MLX/MLX-LM and an already-downloaded original model matching a supplied SHA-256 manifest.

```sh
python3 demo.py
python3 -m unittest discover -s tests -v
python3 -m reverseproof.cli inspect build/original
python3 -m reverseproof.cli propose-pattern build/original
```

`inspect` reads static information and never executes its target. `verify-owned` requires the exact SHA-256 of an explicitly approved owned fixture. This digest binds identity; **it is not an operating-system sandbox**. Only run owned, trusted test fixtures. Per-invocation timeout is five seconds. Tools and model responses cannot choose shell commands.

For offline model experiments, see `python3 run_local_study.py --help`. Install the optional local dependencies using `python3 -m pip install -e ".[local]"` in your local environment. Provide the model directory, pinned manifest, a fresh output directory. The default memory guard is included; the original two rounds used the equivalent guard frozen from [m1-memory-research](https://github.com/megern/m1-memory-research). The guard caps process-tree RSS at 6 GiB, MLX allocations at 4 GiB, system swap growth at 1536 MiB and job time at 900 seconds. Whole-system measurements cannot establish causal attribution to a single process. No adapter was trained for this reversing task.

## Evidence contract

Each target has a SHA-256 identity; tool output has a separate digest. Model proposals cite tool indices. The validator rejects extra actions, unsupported schemas and invalid citations. Citation existence alone does not establish semantic support. The verifier records concrete inputs, expected and observed outputs, counterexamples and inconclusive outcomes. Disassembly addresses are virtual addresses, not file offsets. Finite tests do not prove universal equivalence, source recovery or safety.

Embedded misleading strings are treated as untrusted data. Strict-schema tests and four paired fixtures do **not** prove prompt-injection resistance of an LLM or an autonomous agent. There is no self-directed tool loop yet: the harness selects fixed tools and owned targets.

## Research path

Next: source-separated blind fixtures, negative functions outside the supported schema, held-out compiler settings, independent oracles, model abstention and counterexample metrics, and comparisons with established tools. Preserve failed interpretations and partial jobs. No LinkedIn publication before the owner's review.

Related work: [REA](https://github.com/morluto/rea) already provides agent-assisted reverse engineering; [reverse-agent injection preprint](https://arxiv.org/abs/2605.30667) motivates distrust of target strings. This repository claims no superiority over those projects.
