"""Narrow ARM64 clamp signature. Abstain on any unrecognized instruction sequence."""
import re
from .core import check_proposal

def propose(evidence):
 for index,record in enumerate(evidence["tools"]):
  if record["returncode"]!=0:continue
  if "_main:" not in record["stdout"]:continue
  instructions=[]
  for line in record["stdout"].splitlines():
   match=re.match(r"^([0-9a-f]{16})\s+(\w+)\s*(.*)$",line)
   if match:instructions.append((match[1],match[2],match[3].split(";")[0].strip()))
  # This exact compiler signature is intentionally limited to observed fixtures.
  for start in range(len(instructions)-6):
   block=instructions[start:start+7]
   pattern=[("mov",r"w19, #(0x[0-9a-f]+)"),("mov",r"x1, #0x0"),("mov",r"w2, #0xa"),("bl",r"0x[0-9a-f]+"),("cmp",r"x0, #(0x[0-9a-f]+)"),("csel",r"x8, x0, x19, lt"),("bic",r"x8, x8, x8, asr #63")]
   matched=[re.fullmatch(operand,row[2]) if row[1]==opcode else None for row,(opcode,operand) in zip(block,pattern)]
   if not all(matched):continue
   upper=int(matched[0].group(1),16)
   if upper!=int(matched[4].group(1),16) or not 0<=upper<=1000000:continue
   # Require library call labels and exact print of the computed value.
   if "symbol stub for: _strtol" not in record["stdout"] or "symbol stub for: _printf" not in record["stdout"]:continue
   tail=instructions[start+7:start+11]
   if len(tail)!=4 or tail[0][1:]!=("str","x8, [sp]") or tail[-1][1]!="bl":continue
   proposal=check_proposal({"claim":{"kind":"clamp","lower":0,"upper":upper},"target_sha256":evidence["target_sha256"],"evidence_indices":[index]},evidence)
   proposal.update(method="exact_observed_ARM64_signature",instruction_addresses=[row[0] for row in block],scope="Narrow signature hypothesis only; verify execution on approved owned inputs. Address values are virtual disassembly addresses, not file offsets. Not a general decompiler or formal equivalence proof.")
   return proposal
 return {"status":"abstained","reason":"No supported exact instruction signature"}
