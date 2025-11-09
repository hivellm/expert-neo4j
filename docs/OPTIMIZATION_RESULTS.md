# Neo4j Training Optimization Results

## Date: 2025-11-08

## Final Optimizations Applied

### Speed Optimizations (TypeScript-style)

1. **`gradient_checkpointing: false`** ✅
   - Removes recomputation overhead during backward pass
   - Expected: 20-40% speedup
   - Trade-off: Uses more VRAM (+2-4GB)

2. **`group_by_length: true`** ✅
   - Reduces padding waste by grouping similar-length sequences
   - Expected: 5-10% throughput improvement

3. **`max_seq_length: 2048`** ✅ (was 1024)
   - More FLOPs per step, better GPU utilization
   - Uses more VRAM per batch (+1-2GB)

4. **`gradient_accumulation_steps: 4`** ✅ (was 45)
   - Smaller effective batch size (8 vs 90)
   - Fewer steps per epoch = faster training
   - Matches TypeScript configuration

5. **`optim: "adamw_torch_fused"`** ✅ (was `adamw_bnb_8bit`)
   - Fused operations are faster
   - Uses more VRAM (no 8-bit quantization)

6. **`fp16: true, bf16: false`** ✅
   - Matches TypeScript configuration
   - May be faster on RTX 4090

### Configuration Details

- **Unsloth**: Enabled (`use_unsloth: true`)
  - Provides 2x faster training and 70% less VRAM
  - Note: Causes pickle issues on Windows, forcing Trainer instead of SFTTrainer (packing disabled)

- **Decoding Parameters** (Qwen3 recommended):
  - `temperature: 0.6` (thinking mode)
  - `top_p: 0.95`
  - `top_k: 20`
  - `min_p: 0`
  - Reference: https://huggingface.co/unsloth/Qwen3-0.6B-GGUF

## Expected Performance

### Speed Improvements
- **Gradient checkpointing disabled**: 20-40% faster
- **Group by length**: 5-10% throughput improvement
- **Fused optimizer**: 5-10% faster optimizer steps
- **Smaller gradient accumulation**: Faster steps (fewer accumulations)
- **Total expected**: 30-50% faster training

### VRAM Impact
- **Gradient checkpointing disabled**: +2-4GB VRAM
- **Max seq length 2048**: +1-2GB VRAM
- **Fused optimizer (no 8-bit)**: +0.5-1GB VRAM
- **Total expected increase**: +3.5-7GB VRAM
- **Unsloth savings**: -70% VRAM (offsets the increase)

### Current Configuration
- **Effective batch size**: 8 (batch_size=2 × gradient_accumulation=4)
- **Training steps per epoch**: ~562 steps (4500 examples / 8)
- **Total steps**: ~1124 steps (2 epochs)

## Comparison with TypeScript

| Setting | Neo4j (Optimized) | TypeScript | Status |
|---------|-------------------|------------|--------|
| `gradient_checkpointing` | false | false | ✅ Match |
| `group_by_length` | true | true | ✅ Match |
| `max_seq_length` | 2048 | 2048 | ✅ Match |
| `gradient_accumulation_steps` | 4 | 4 | ✅ Match |
| `optim` | adamw_torch_fused | adamw_torch_fused | ✅ Match |
| `fp16/bf16` | fp16: true | fp16: true | ✅ Match |
| `use_unsloth` | true | false | ⚠️ Different |
| `batch_size` | 2 | 2 | ✅ Match |

## Notes

- **Unsloth trade-off**: Enables faster training but causes pickle issues on Windows, preventing SFTTrainer packing
- **TypeScript advantage**: Without Unsloth, can use SFTTrainer with packing (30-40% faster)
- **Current approach**: Keep Unsloth for VRAM savings, optimize other parameters for speed

## Next Steps

1. ✅ Wait for checkpoint to test quality
2. Monitor VRAM usage during training
3. Compare training speed with baseline
4. Evaluate model quality at checkpoint-250
5. Document final performance metrics

## Backup

Original manifest saved to: `manifest.json.backup`

