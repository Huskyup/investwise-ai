# D5 reviewed learning case

**Company message:** We turned a recorded savings-and-wages conversation into reviewed fictional training material, updated two existing D5 classifiers once and measured the change on training-excluded text. Some raw classifications improved, but the ML still could not safely take over a new savings reply under the existing gates. We retained the current demo.

## The business problem

A customer saying they own or receive money has not necessarily said that it pays living costs. D5 must preserve that relationship, handle combinations and exclusions, and confirm the answer. In the earlier live demonstration, GPT understood the savings-and-wages dialogue while the original ML escalated the first reply.

## What we changed

The business owner approved sixteen new training contrasts and eight separately authored validation replies. We retained the previous eight approved training examples and fitted only the two existing D5 classifiers. The architecture, financial checks, fifteen-question journey and defaults were unchanged.

## What the evidence shows

- Previously opened clear validation source predictions improved from **2/4 to 4/4**.
- Fresh raw intent predictions improved from **4/6 to 6/6**; fresh clear source predictions stayed **2/4**.
- Both new savings replies had the right top-scoring source but several plausible options, so **neither became an independently accepted ML answer**.
- One earlier raw gain was lost. A newly observed wrong baseline acceptance was avoided by candidate uncertainty, not repaired into a correct candidate answer.

These are small, AI-authored, human-reviewed samples. Opened cases are development evidence; the eight new cases were excluded from training and calibration. No new live conversation was run because the offline requirements failed.

## Honest demonstration boundary

Use the existing documented ML + GPT entry for the previously demonstrated conversation, subject to service availability. Label saved recordings as recordings. The new candidate is an audit artifact and has no launch profile. The learning process is reproducible, but the intended successful flywheel—new ML acceptance followed by live confirmation—has not yet been completed.

The [result report](RESULTS.md) links the reviewed examples, exact predictions, artifacts and commands. The original prototype is preserved; this case makes no whole-product reliability or automatic-learning claim.
