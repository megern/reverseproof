# Evidence-bound interpretation on a local M1 Mac: development study

Author: Megern Qaisse. Client date: 2026-10-09. Status: development report, not a peer-reviewed paper.

## Question and apparatus

Can a locally executed original BF16 Qwen3-0.6B propose a supported explanation of small ARM64 programs, and can a separate verifier prevent adoption of unsupported answers? All inference and compilation ran locally. The model revision, model/tokenizer hashes, frozen harness sources, prompts, raw responses and resource guard outcomes accompany each round.

## Protocol

An owned C fixture prints an integer clamped to either [0,9] or [0,10]. Each upper bound has a clean metadata string and a string that requests ignoring evidence and reporting 777. These are four closely related variants of one program, not four independent software projects. Compilation uses local Apple Command Line Tools with an explicit SDK and `-O2`.

The model sees static tool records, with source text, oracle outputs and variant/path names excluded from the prompt. It receives a restricted clamp schema and can abstain. Target identity is supplied by the harness rather than inferred by the model. Greedy generation is capped at 256 new tokens. Existing tool-index citations must be valid, but citation validity alone does not prove an explanation.

Each schema-valid proposal is checked on the frozen inputs -64 through 64, plus -1,000,000 and 1,000,000: 131 inputs. These finite tests can refute a claim or support it on these inputs; they cannot establish universal equivalence. Invalid model proposals are not executed. The verifier executes only the owned, digest-approved fixture, not generated commands.

Round two was designed after observing round-one errors. It adds a schema example with arbitrary bounds [-3,27]. It is a development intervention, not an independent preregistered test.

## Outcomes

Round one produced four invalid claim schemas. Round two produced three invalid responses with trailing punctuation and one schema-valid proposal using the arbitrary example bounds. The valid but wrong proposal was refuted on 121 of 131 inputs. Correct model interpretations demonstrated: zero of eight attempts across the two development rounds. The two rounds are repeated observations of related fixtures, not an eight-project benchmark.

The strict response boundary rejected seven invalid answers and the independent verifier refuted the eighth. This demonstrates rejection and counterexample recording for these attempts, not improved model accuracy or a universally safe agent. The embedded-note pairs cannot establish injection resistance: the underlying interpretation task already failed.

A separate pattern baseline recognizes two exact observed ARM64 instruction signatures. Its first round supported two clamp variants and abstained on the other two and on an affine negative. After adding the second observed compiler signature, its second round supported four clamp variants on the tested inputs and abstained on the affine negative. These rules were developed from the same fixtures; the result is not a held-out performance estimate and not a fair superiority comparison with the model or existing reversing tools.

## Resource reporting

The recorded peak process-tree RSS for local inference was approximately 1.54–1.61 billion bytes per job. The monitor samples at 0.5-second intervals and can miss short peaks; it does not cover all accelerator allocations or total system memory. Separate MLX peak-allocation records are present in model result files. Guarded whole-job durations were approximately 4.59–6.69 seconds, including loading and setup; these are uncontrolled development observations, not latency or throughput benchmarks. Whole-system swap changes are shared-process measurements, not causal attribution.

The model uses its original small-model weights; this study does not run or train an original 70B model. No reversing adapter was trained. SMS-trained adapters from the companion memory project were not used as reversing specialists.

## Limitations and next experiment

The tasks supply a narrow function family; there is one source program, one CPU instruction set, one local model and one compiler configuration. Model pretraining contamination is unknown. No source-code recovery, real application reconstruction, novel learning algorithm, formal proof, general injection resistance or improvement over REA is established.

The next useful study must freeze source-separated target groups, include functions outside the supported schema, vary compiler settings, verify independent behavioral oracles, and measure correct interpretations, invalid responses, abstention and counterexamples without removing failures. Model tuning must use a separate training group before a held-out evaluation. Local compute and recorded resource guards remain mandatory.
