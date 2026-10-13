# D5 correction follow-up: addition, replacement and actual use

13 October 2026 · Huskyup/investwise-ai · `feature/all-question-ml-prototype`

**The standalone D5 correction follow-up now asks the unresolved funding question explicitly.** It quotes the user's validated evidence as their words, then asks whether the sources pay living costs together, one replaces another, or a mentioned source is not used for those costs. It does not assert that receiving support establishes expenditure.

## The saved example

The user entered `most of my wages`, selected `/change`, then entered `im getting financial support from my parents` and `most of my wages`. The saved GPT responses had the full history. Both correction replies returned valid abstentions with `complete_answer_needed`; neither was rejected by the validator. The old authored question merely asked which source was changing and repeated itself.

For the saved parental-support reply, the new display is:

> Your words: "most of my wages"; "im getting financial support from my parents"
>
> For your updated answer, do the sources you mentioned pay your living costs together, does one replace another, or is a source not used for these costs? Please name the sources and say which applies. You can say if you are still unsure.

This general template uses exact validated quotations. It adds no wage/parent phrase matching, inferred source categories, model instructions, schema fields or state transitions. A bare yes to several alternatives still does not establish which applies. Models, validators, existing checks, all 15 questions and the main default are unchanged.

## Bounded verification

Only this saved three-reply conversation was replayed, once, through the ML + GPT session with the original ML resolution and GPT outputs. The [receipt](checks.json) records:

| Step | Before and after interpretation | Display change |
|---|---|---|
| `most of my wages` | Salary candidate awaiting confirmation | None |
| `/change` | Candidate invalidated; history retained; no interpretation call | None |
| Parental-support reply | Unresolved; no financial candidate | Exact quotes and explicit funding alternatives |
| Repeated wages reply | Still unresolved; no financial candidate | Same improved template with its validated quotes |

Raw outputs, routes and all non-wording result fields were preserved. The updated follow-up was included in the next replay's context. There were **zero live ML/GPT calls, authentication calls, fits or new examples**. The [preservation audit](preservation.json) records unchanged files.

This demonstrates a wording and context-preservation repair. Replaying saved outputs does not establish that GPT will resolve the next new reply, or that this conversation has reached a confirmed answer. The unresolved decision must remain until the user clarifies it.

Pull the Huskyup branch and restart the terminal using the [handoff commands](../d5-semantic-method-handoff.md). No new dependency or sign-in change is required.
