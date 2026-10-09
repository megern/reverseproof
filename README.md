# ReverseProof — local prototype

A bounded verifier for reverse-engineering hypotheses, built by Megern Qaisse.
This first release analyzes owned Mach-O fixtures with macOS tools, binds observations to SHA-256, and tests a proposed clamp behavior. It preserves counterexamples instead of allowing a generated explanation to become a verified fact.

## Run on macOS

```sh
python3 demo.py
python3 -m unittest discover -s tests -v
python3 -m reverseproof.cli inspect build/original
```

The original fixture supports the hypothesis on 21 inputs; a changed upper bound refutes it. `results/demo.json` records exact tool outputs, target hashes, inputs, expected and observed outputs.

## Current scope

This is a deterministic verification core, **not yet an autonomous LLM reverse-engineering agent**. The proposal validator is ready for a future local model but no model has been integrated, trained or benchmarked for this task. Disassembly is evidence, not proof of reconstructed semantics. Finite tests do not prove equivalence. This toy example does not establish performance on real applications or research novelty.

`inspect` never executes its target. `verify-owned` requires the exact SHA-256 of an explicitly approved owned fixture; this is an identity check, **not an operating-system sandbox**. Do not use it to run untrusted binaries. Target strings never become commands; only fixed tools and a strict claim schema are accepted. Injection schema rejection is not proof that an eventual LLM agent is injection resistant.

Next research: blinded source-separated fixtures, independent test oracles, local model proposals, accuracy/abstention and counterexample rate, then comparison against an established baseline. No LinkedIn publication before review.

Related work: [REA](https://github.com/morluto/rea) already provides agent-assisted reverse engineering; [reverse-agent injection preprint](https://arxiv.org/abs/2605.30667) motivates treating target contents as untrusted. No superiority claim.
