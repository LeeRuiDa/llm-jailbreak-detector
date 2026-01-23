# Method

## Model
- Backbone: microsoft/deberta-v3-base
- LoRA adapter: r=8, alpha=16, dropout=0.05

## Normalization
- Training normalization (normalize_train): NFKC + strip Cf, optional Mn removal (off in Week 7)
- Inference normalization (normalize_infer): OFF for Week 7 evaluation

## Adversarial augmentation (adv2)
- Character-level perturbations (unicode mixing, homoglyphs, noise) applied with probability 0.25 when enabled

## Rewrite augmentation
- Light rewrite (synonyms, filler tokens, minor reordering); evaluation-only in Week 7
