# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The initial UML contains five classes across two layers — two plain classes and three dataclasses.

| Class | Type | Responsibility |
|-------|------|----------------|
| `Task` | dataclass | Holds a single care activity: its title, how long it takes, priority level, optional preferred time of day, and whether it is required. Pure data — no behaviour. |
| `ScheduledTask` | dataclass | Wraps a `Task` once it has been placed on the timeline, adding a start time, end time, and a human-readable reason explaining why it was chosen. |
| `Pet` | class | Stores a pet's profile (name, species, age, breed, special needs) and owns a collection of `Task` objects. Responsible for managing the list of tasks that belong to that pet. |
| `Owner` | class | Stores the owner's profile and their daily availability window (day_start / day_end). Owns a collection of `Pet` objects and is the single entry point for adding or removing pets. |
| `Scheduler` | class | Contains the scheduling intelligence. Given an `Owner` (and through it, all pets and tasks), it prioritises tasks (high → medium → low), fits them into the available time window, and produces an ordered list of `ScheduledTask` objects along with a plain-English explanation. |

Relationships: `Owner` has one-to-many `Pet`; `Pet` has zero-to-many `Task`; `Scheduler` takes one `Owner` and produces zero-to-many `ScheduledTask`, each of which wraps exactly one `Task`.

**b. Design changes**

After reviewing the skeleton, two issues were identified and fixed:

1. **Added `pet_name: str` to `ScheduledTask`.**
   The original design had no way to know which pet a scheduled task belonged to. Without this field, `explain_plan` could only say "Walk at 08:00" — it couldn't say "Walk *Mochi* at 08:00". This matters especially when an owner has multiple pets whose tasks get merged into a single timeline. Adding `pet_name` directly to `ScheduledTask` was the simplest fix: no extra lookup needed when generating the explanation.

2. **Removed the unused `field` import from `dataclasses`.**
   The original skeleton imported `field` from `dataclasses` but never used it. Removing it keeps the imports honest and avoids confusion during implementation.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints, in order of importance:

1. **Required vs optional** — required tasks are always scheduled before optional ones, regardless of priority. A pet must be fed even if a playtime session would rank higher by priority alone.
2. **Priority level** (high → medium → low) — within each required/optional bucket, high-priority tasks get the earliest slots.
3. **Available time window** (owner's `day_start` / `day_end`) — tasks that would push past `day_end` are skipped rather than truncated, so no task ever runs over the owner's available hours.

Required tasks were ranked first because missing them (feeding, medication) has real welfare consequences, while missing optional tasks (playtime, grooming) is merely inconvenient.

**b. Tradeoffs**

The conflict detector checks for *exact time-window overlap* (`A.start < B.end AND B.start < A.end`) rather than accounting for gaps between tasks. This means two tasks scheduled back-to-back with zero minutes between them — say, a 30-minute walk ending at 08:30 followed immediately by a 10-minute feeding at 08:30 — are treated as conflict-free even though a real owner would need at least a moment to transition between them.

This tradeoff is reasonable for this scenario because the app is a planning aid, not a rigid timer. A small gap between tasks is a natural human behaviour that doesn't need to be modelled explicitly at this stage. If PawPal+ were extended to handle professional pet-sitters managing many pets on tight schedules, adding a configurable "buffer time" between tasks would be the right next step. For a single busy owner, exact-overlap detection is sufficient to catch real mistakes (like accidentally double-booking the same time slot for two pets) without producing false warnings on normal back-to-back scheduling.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
