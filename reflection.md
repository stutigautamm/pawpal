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

Constraints:
Time Limits: The app tracks how many total minutes the owner has available today. It will never book more tasks than there is time for, and it will skip a large task if it doesn't fit so it can look for smaller tasks that do.

Task Priorities: Tasks are ranked by importance (HIGH, MEDIUM, LOW). If two tasks have the same priority, the app automatically chooses the shorter one first so you can get more done.

I decided the time constraint mattered more because it is a hard limit where you simply cannot do a 45-minute task if you only have 30 minutes left in your day.

After checking the time, I thought the priority constraint matters as well. Important health tasks (like giving medication) should always happen before optional tasks (like grooming) to make sure the pet's basic needs are met first.


**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

Our scheduler uses a quick and simple way to check for time conflicts rather than a complex calendar booking system.

How it works right now: The app only flags a warning if two tasks have the exact same start time (like two tasks both set for `09:05`).

The Tradeoff: This makes the code very fast and prevents the app from crashing. However, it doesn't calculate if a task's duration runs into another task. For example, if a 45-minute walk starts at `08:00` and a vet call is set for `08:15`, the app won't show a warning even though those tasks technically overlap.

Why this choice was made: The main goal of this app is to fit tasks into a total daily minute budget. Keeping the code simple and easy to read was more important than building a full, complicated calendar tracking system.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI across three key steps: managing application memory with st.session_state, designing the string-sorting algorithm, and writing the date math for recurring tasks. It helped me turn rough ideas into operational logic that handles data correctly. The kind of prompts or questions that were most helpful were short and specific questions like "How do I use a lambda function to sort strings in HH:MM format?" or "How do I use timedelta to add a day to a date?" Separating my chats into different steps also helped keep the AI on track. Also, providing all the files needed for context and giving the AI as much specific information as possible helped as well. 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

The AI suggested a very dense, compressed loop for the scheduling engine that combined multiple filtering and sorting steps into a single line of code. I rejected it because it was too complicated for a human to read or debug if something went wrong. I chose to keep my explicit, multi-step loop so the system remains clean and easy to maintain. I verified every AI suggestion by running my custom main.py terminal test script and 27 automated unit tests. If the AI changed code related to dates or sorting, I checked the test results to ensure everything passed perfectly. This process proved that no new bugs were accidentally introduced into the engine.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested five main behaviors: priority ordering, chronological time sorting, automatic date progression for daily/weekly tasks, time-clash detection, and strict budget limits. These tests made sure the app acts predictably every time a user changes inputs or finishes a task. This safeguarded the core engine from infinite loops and missing data. These tests are important because Streamlit runs the script from top to bottom on every single click, the backend code has to be completely airtight. The tests proved that data stays safe, unique IDs generate correctly, and recurring tasks repeat without multiplying.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am completely confident because all 27 of my unit tests passed on the first try. This quick run proves that both everyday user workflows and tricky input validation rules are safe. If I had more time, I would test what happens if a task starts late at night and ends after midnight to see how it spans across two days. I would also test what happens if an owner changes a pet's name while active tasks are already connected to it.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most happy with the automated task recurrence framework. It is amazing to watch the system complete a daily task, use timedelta to find tomorrow's date, assign a brand-new ID, and automatically append the next occurrence back into the pet's list.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would upgrade the conflict detection algorithm to look at task durations instead of just matching start times. Right now, it only flags tasks that start at the exact same minute. I want it to warn users if a new task begins while a previous long task is still running.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

I learned that working with AI requires me to act as the lead architect. AI is great at writing quick snippets, but it doesn't plan for human readability or clean structure. It is my job to break down problems into small parts and enforce good standards so the code stays clean (human readable) and easy to manage.