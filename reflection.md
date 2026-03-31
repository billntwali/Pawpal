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

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
