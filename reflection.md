# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

For the initial design of PawPal+, the system was built using four clear classes. This keeps data organized and separates profile information from the scheduling logic:

Owner Class - Responsibilities: Keeps track of the user's name and how many total minutes they have available to care for their pets today. It also holds a list of the owner's pets.

Pet Class - Responsibilities: Stores a pet's profile details (like name, breed, and age). It holds the list of tasks assigned to that specific pet and can calculate the total time needed for all of them.

Task Class - Responsibilities: Represents a single chore (like a walk or feeding). It holds vital details like how long it takes, how important it is (priority), and whether it has been completed yet.

Scheduler Class - Responsibilities: Acts as the "brain" of the app. It collects all the tasks for all pets, sorts them by importance, and fits them into the owner's free time. It also writes down the reasoning for why certain tasks made the cut and others didn't.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, the design changed slightly when moving from the initial plan to the actual Python code. These changes protect the app from bugs and make it much easier to build the user interface.

What changed: 
1. Task priority was changed from a plain number to a fixed list of options (Priority using an IntEnum).
2. Every Task now strictly requires a pet_name string right when it is created.

Why the change was made: 
1. Using a fixed IntEnum stops users from accidentally putting in broken numbers (like a priority of 99 or -5). It also lets the scheduling system sort the tasks automatically by their value (Low, Medium, High).
2. Forcing a pet_name on every task matches how a user actually interacts with the app (e.g., clicking on a pet, then adding a task for them). More importantly, when the scheduler mixes all the tasks together into one master daily plan, having the pet's name on the task ensures the final calendar can clearly say "Walk (for Biscuit)" instead of just "Walk".


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
