# Neo4j Training Optimization Test

## Date: 2025-11-08

## Objective
Test if TypeScript-style optimizations can improve training speed without exceeding VRAM limits on RTX 4090 (24GB).

## Changes Applied (from TypeScript config)

### 1. **Gradient Checkpointing: DISABLED** ⚡ (MAJOR SPEEDUP)
- **Before:** `gradient_checkpointing: true`
- **After:** `gradient_checkpointing: false`
- **Impact:** Removes recomputation overhead during backward pass. Expected 20-40% speedup, but uses more VRAM.

### 2. **Group by Length: ENABLED** 📊
- **Before:** `group_by_length: false`
- **After:** `group_by_length: true`
- **Impact:** Reduces padding waste by grouping similar-length sequences together. Improves throughput.

### 3. **Max Sequence Length: INCREASED** 📏
- **Before:** `max_seq_length: 1024`
- **After:** `max_seq_length: 2048`
- **Impact:** More FLOPs per step, better GPU utilization. Uses more VRAM per batch.

### 4. **Precision: FP16 instead of BF16** 🔢
- **Before:** `fp16: false, bf16: true`
- **After:** `fp16: true, bf16: false`
- **Impact:** May be faster on some GPUs. FP16 uses less VRAM than BF16.

### 5. **Optimizer: Fused AdamW** ⚙️
- **Before:** `optim: "adamw_bnb_8bit"`
- **After:** `optim: "adamw_torch_fused"`
- **Impact:** Fused operations are faster, but uses more VRAM (no 8-bit quantization).

## Expected Results

### Speed Improvements
- **Gradient checkpointing disabled:** 20-40% faster training
- **Group by length:** 5-10% throughput improvement
- **Fused optimizer:** 5-10% faster optimizer steps
- **Total expected:** 30-50% faster training

### VRAM Impact
- **Gradient checkpointing disabled:** +2-4GB VRAM
- **Max seq length 2048:** +1-2GB VRAM
- **Fused optimizer (no 8-bit):** +0.5-1GB VRAM
- **Total expected increase:** +3.5-7GB VRAM

### Current Baseline (with gradient checkpointing)
- VRAM usage: ~20-21GB
- Expected with optimizations: ~23.5-28GB

## Risk Assessment
- **Low risk:** RTX 4090 has 24GB VRAM, should handle the increase
- **Monitor:** Watch for OOM errors during first few steps
- **Fallback:** If OOM occurs, can reduce `max_seq_length` back to 1024 or re-enable gradient checkpointing

## Backup
Original manifest saved to: `manifest.json.backup`

## Test Plan
1. Start training with optimized config
2. Monitor VRAM usage during first 10 steps
3. Compare training speed (samples/sec) vs baseline
4. If successful, measure full training time
5. Document results and decide if optimizations should be kept

## Commands

### Start Training
```bash
# From project root
cargo run -- train expert-neo4j
```

### Monitor VRAM (in another terminal)
```bash
# Windows PowerShell
nvidia-smi -l 1

# Or WSL
watch -n 1 nvidia-smi
```

### Restore Original Config (if needed)
```bash
cp manifest.json.backup manifest.json
```

