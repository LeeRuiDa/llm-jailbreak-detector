# Related Work

## 2.1 Guardrail detection background
Brief overview of prompt-safety detection and adversarial robustness themes.

## 2.2 Threat taxonomy
Table 2.1: Threats, evaluated defenses, and observed weaknesses.
| Threat / perturbation | Defense(s) evaluated | Weakness / limitation noted |
| --- | --- | --- |
| unicode mixing | Training-time normalization (NFKC, drop Cf) | Synthetic perturbations approximate real-world attacks and may miss unseen tactics. |
| adv2 character noise | adv2 augmentation; normalization-only baseline | Augmentation can overfit to the specific perturbation families implemented; dataset shift between main and JBB splits can confound robustness attribution. |
| rewrite paraphrase | Evaluation on rewrite perturbations; fixed threshold transfer | A single fixed threshold assumes calibration stability across distribution shifts. |

## 2.3 Defenses and evaluation practices
Context for normalization, data augmentation, and threshold transfer in prior work.

## 2.4 Summary
Key takeaways that motivate the method and evaluation choices in this thesis.
