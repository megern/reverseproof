# ReverseProof

## Version 1.0.0

Static multi-target review. Processes up to 100 distinct <=64-MiB owned target files, retains per-target errors and static evidence, and produces local HTML/JSON. macOS Command Line Tools required. Never executes the target binary or lets a model choose tools. Static hypotheses are not behavioral verification; the existing digest-bound verify-owned workflow remains separate.

See the [complete local workflow](docs/v1-workflow.md) for installation, commands, review artifacts and limits. Earlier preview notes below describe their historical tagged revisions.

## Audit a verification report without executing a binary (local development)

`reverseproof audit-report /absolute/local/verification.json` recomputes expected
clamp outputs, counterexamples and the final finite-test status from recorded
cases. It rejects inconsistent status/counterexample summaries, invalid process
result fields, booleans masquerading as integer outputs and malformed hashes.
It reports distinct inputs and coverage below, inside and above the claimed
bounds. Reports are capped at 16 MiB and 1000 cases.

This command never executes the target. It checks internal evidence consistency,
not report authenticity or universal behavior. As with other commands,
`--output` must precede the subcommand and must point to a fresh file.

## Public preview v0.3.0

Python 3.11+; commands below use a local Mac/Linux shell. Source and reports are public; this is a research/development preview, not a production-security certification.

```sh
git clone --branch v0.3.0 https://github.com/megern/reverseproof.git
cd reverseproof
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install .
reverseproof --help
```

The installed entry point was exercised outside the checkout in a separate local environment. This revision has 24 passing local tests. No hosted CI or cloud compute is used. Report an issue with the command, Python/OS versions, sanitized input and expected/actual behavior; remove credentials and private records first. Benchmarks describe the supplied fixtures and hardware.

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

## v0.2.0: one local workflow

```sh
python3 -m reverseproof.agent --target build/original --model /LOCAL/models/qwen3-0.6b-original --output /LOCAL/runs/reverseproof-fresh
```

This inspects the target and obtains an offline model hypothesis; it does not execute the target. For an owned trusted fixture only, add `--owned-sha256 EXACT_HASH_FROM_INSPECT` to enable the bounded behavioral check. The output directory must be fresh. A rejected or abstaining model response can use an explicitly labeled exact-instruction-rule fallback. A valid-but-refuted model response remains refuted; it is never replaced with a more favorable rule answer. Any model process/resource failure stops the workflow before target execution.

The integrated workflow was also run on the owned original fixture: the model returned a valid but incorrect proposal, and the verifier retained its refutation with 120 counterexamples. It did not substitute a favorable rule outcome. See `results/workflow-v1`. A separate real run without an owned execution approval retained an unverified hypothesis with no target-execution report (`results/static-workflow-v1`). The current suite passes 20 tests. This is another related integration smoke test, not an independent held-out benchmark.

## Evidence contract

Each target has a SHA-256 identity; tool output has a separate digest. Model proposals cite tool indices. The validator rejects extra actions, unsupported schemas and invalid citations. Citation existence alone does not establish semantic support. The verifier records concrete inputs, expected and observed outputs, counterexamples and inconclusive outcomes. Disassembly addresses are virtual addresses, not file offsets. Finite tests do not prove universal equivalence, source recovery or safety.

Embedded misleading strings are treated as untrusted data. Strict-schema tests and four paired fixtures do **not** prove prompt-injection resistance of an LLM or an autonomous agent. There is no self-directed tool loop yet: the harness selects fixed tools and owned targets.

## Research path

Next: source-separated blind fixtures, negative functions outside the supported schema, held-out compiler settings, independent oracles, model abstention and counterexample metrics, and comparisons with established tools. Preserve failed interpretations and partial jobs. No LinkedIn publication before the owner's review.

Related work: [REA](https://github.com/morluto/rea) already provides agent-assisted reverse engineering; [reverse-agent injection preprint](https://arxiv.org/abs/2605.30667) motivates distrust of target strings. This repository claims no superiority over those projects.

## Bounded hashing and alternate compiler coverage

Large target/model files are hashed with a 1 MiB streaming buffer instead of a whole-file Python allocation. Hash values and target binding semantics are unchanged; this is a buffer bound, not a measured total RAM reduction.

```sh
python3 run_coverage_study.py --output /tmp/reverseproof-coverage-new
python3 -m unittest discover -s tests
```

The study freezes source and signature-rule hashes before compiling eight owned variants: upper bounds 7/23 with O0/O1/O2/Os. It retains abstentions and verifies proposed clamps on 131 bounded inputs. Exported protocol and report are in `results/compiler-coverage-20261011/`; compiled executables stay local. In this run, six variants produced hypotheses supported on all 131 tested inputs; both O0 variants caused abstention. These are related toy cases, not a real-application benchmark or an LLM quality result. Earlier model failures remain visible.


### Negative controls and CLI outcomes

```sh
python3 run_coverage_study.py --include-negatives --output /tmp/reverseproof-fresh-robustness
reverseproof --output /tmp/owned-inspection.json inspect build/original
```

The twelve-cell robustness study adds four affine negative controls to the eight alternate-source clamp/compiler variants. The frozen rules produce six supported clamp hypotheses on 131 inputs each, abstain on both O0 clamp variants, and abstain on all four affine controls. Complete disassembly evidence and source hashes are retained in `results/robustness-20261011/`. These related toy fixtures do not establish general decompilation accuracy; no local language model was evaluated in this study.

The CLI accepts lower/upper bounds and bounded input ranges, preserves existing output files, and returns 1 for a refuted claim or 2 for an input/tool error. Inspection and pattern proposals do not execute the target. Execution still requires approval bound to the exact owned-fixture hash.
