# Generic chain trigger

**Source report:** CTI Prompt Library (Volume 2)
**Source URL:** https://feedly.com/ti-essentials/posts/cti-prompt-library-volume-2
**Section / workflow:** Prompt chains: From single prompts to workflows

## What this prompt does
Once the full library is loaded into a persistent workspace (e.g. a Claude Project, a Gemini Gem, or a saved Claude Skill) so the model keeps all twelve prompts and the critic prompt in context, this trigger activates a named prompt chain on a report or dataset. It runs each prompt in the chain in order, feeds each step's output into the next, and pauses to show output at each step.

## Prompt
```
Using the prompts saved in this project, run [CHAIN NAME] on the report below (or attached).

Run each prompt in order, feed each step's output into the next, apply my Context Pack throughout, and label each step's output clearly. Pause and show me the output of each step before moving to the next. Only pass forward the outputs the next prompt can actually use (for example, feed a detection prompt only the endpoint-observable techniques), carry every step's Validation status and caveats forward rather than dropping them, and re-emit full tables rather than only changed rows. Do not use em dashes.

[paste report here]
```

## Notes
"Context Pack" refers to your saved context variables (job role, sector, region, and stack summary) that you carry across every step of the chain.

Edit the generic trigger to name which chain you want to run. Ready-made triggers from the article:

- Chain 1: "Run Chain 1 (Report to Sentinel detection): Prompt 3, then Prompt 4 if we use Splunk. Output the detection opportunities, then the converted rules, then the telemetry gap list."
- Chain 2: "Run Chain 2 (Report to prioritized, feasible hunt): Prompt 6, then feed its lead table into Prompt 7 using my Context Pack stack summary. Output the ranked leads, then the feasibility table and resourcing recommendation."
- Chain 3: "Run Chain 3 (AI threat activity to detection opportunities): Prompt 2, then feed the observable mapped techniques into Prompt 3. Output the ATLAS mapping, then the detection ideas."
- Chain 4: "Run Chain 4 (Report to risk translation): Prompt 10 to build the structured threat assessment, then Prompt 12 to turn it into stack-tailored mitigations, and Prompt 11 if staff need an awareness brief. Output the assessment, then the mitigation plan, then the newsletter."

