"""Diagnostic: trace MPS segfault through the full training step.

Run: .venv/bin/python scripts/debug_mps_segfault.py
"""

import os

os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"

print("[1/15] Importing...", flush=True)
import torch  # noqa: E402
import torch.nn.functional as F  # noqa: E402
from peft import LoraConfig, get_peft_model  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

print(f"        PyTorch {torch.__version__}, MPS={torch.backends.mps.is_available()}", flush=True)

MODEL = "meta-llama/Llama-3.1-8B-Instruct"
DTYPE = torch.bfloat16
DEVICE = "mps"
NUM_SLOTS = 128

print("[2/15] Tokenizer...", flush=True)
tokenizer = AutoTokenizer.from_pretrained(MODEL)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
if "[MEM]" not in tokenizer.get_vocab():
    tokenizer.add_special_tokens({"additional_special_tokens": ["[MEM]"]})
mem_token_id = tokenizer.convert_tokens_to_ids("[MEM]")

print("[3/15] Load model...", flush=True)
base = AutoModelForCausalLM.from_pretrained(MODEL, dtype=DTYPE, low_cpu_mem_usage=True)
base.resize_token_embeddings(len(tokenizer))
base.to(DEVICE)
torch.mps.synchronize()
print("        OK", flush=True)

print("[4/15] LoRA...", flush=True)
lora_cfg = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
)
encoder = get_peft_model(base, lora_cfg)
encoder.print_trainable_parameters()
decoder = encoder
print("        OK", flush=True)

print("[5/15] Optimizer...", flush=True)
optim = torch.optim.AdamW(
    [p for p in encoder.parameters() if p.requires_grad], lr=3e-4, betas=(0.9, 0.95)
)
print("        OK", flush=True)

print("[6/15] Tokenize dummy batch...", flush=True)
texts = ["The quick brown fox jumps over the lazy dog."] * 2
anchor_inputs = tokenizer(
    texts, return_tensors="pt", padding=True, truncation=True, max_length=512
).to(DEVICE)
positive_inputs = tokenizer(
    texts, return_tensors="pt", padding=True, truncation=True, max_length=512
).to(DEVICE)


def append_mem(inputs):
    B = inputs["input_ids"].size(0)
    mem = torch.full((B, NUM_SLOTS), mem_token_id, device=DEVICE, dtype=inputs["input_ids"].dtype)
    return {
        "input_ids": torch.cat([inputs["input_ids"], mem], dim=1),
        "attention_mask": torch.cat([inputs["attention_mask"], torch.ones_like(mem)], dim=1),
    }


a_in = append_mem(anchor_inputs)
p_in = append_mem(positive_inputs)
print(f"        shapes: {a_in['input_ids'].shape}", flush=True)

print("[7/15] Encoder forward (anchor)...", flush=True)
a_out = encoder(**a_in, output_hidden_states=True, return_dict=True)
torch.mps.synchronize()
a_mem = a_out.hidden_states[-1][:, -NUM_SLOTS:, :]
print(f"        OK — {a_mem.shape}", flush=True)

print("[8/15] Encoder forward (positive)...", flush=True)
p_out = encoder(**p_in, output_hidden_states=True, return_dict=True)
torch.mps.synchronize()
p_mem = p_out.hidden_states[-1][:, -NUM_SLOTS:, :]
print(f"        OK — {p_mem.shape}", flush=True)

print("[9/15] Decoder forward (disable_adapter + inputs_embeds)...", flush=True)
with decoder.disable_adapter():
    with torch.no_grad():
        dec_input_embeds = decoder.get_input_embeddings()(anchor_inputs["input_ids"])
    soft_prompt = a_mem
    full_embeds = torch.cat([soft_prompt, dec_input_embeds], dim=1)
    labels = anchor_inputs["input_ids"].clone()
    labels[anchor_inputs["attention_mask"] == 0] = -100
    pad_lab = torch.full((labels.size(0), NUM_SLOTS), -100, device=DEVICE, dtype=labels.dtype)
    labels_full = torch.cat([pad_lab, labels], dim=1)
    dec_out = decoder(inputs_embeds=full_embeds, return_dict=True)
torch.mps.synchronize()
print(f"        OK — logits {dec_out.logits.shape}", flush=True)

print("[10/15] L_recon (cross_entropy)...", flush=True)
l_recon = F.cross_entropy(
    dec_out.logits.view(-1, dec_out.logits.size(-1)),
    labels_full.view(-1),
    ignore_index=-100,
)
torch.mps.synchronize()
print(f"        OK — l_recon={float(l_recon):.4f}", flush=True)

print("[11/15] L_NCE (infonce)...", flush=True)
a_pool = a_mem.mean(dim=1)
p_pool = p_mem.mean(dim=1)
sim = F.cosine_similarity(a_pool.unsqueeze(1), p_pool.unsqueeze(0), dim=-1) / 0.07
targets = torch.arange(sim.size(0), device=DEVICE)
l_nce = F.cross_entropy(sim, targets)
torch.mps.synchronize()
print(f"        OK — l_nce={float(l_nce):.4f}", flush=True)

print("[12/15] Combined loss...", flush=True)
loss = l_recon + 0.3 * l_nce
print(f"        OK — loss={float(loss):.4f}", flush=True)

print("[13/15] loss.backward()...", flush=True)
(loss / 8).backward()
torch.mps.synchronize()
print("        OK", flush=True)

print("[14/15] optimizer.step()...", flush=True)
torch.nn.utils.clip_grad_norm_(encoder.parameters(), 1.0)
optim.step()
optim.zero_grad(set_to_none=True)
torch.mps.synchronize()
print("        OK", flush=True)

print("[15/15] Cleanup...", flush=True)
del a_out, p_out, dec_out, loss, l_recon, l_nce
torch.mps.empty_cache()

print("\nFull training step PASSED. No segfault.", flush=True)
