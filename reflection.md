# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
    There are four main classes: owner, pet, task, and scheduler. 

    Owner has attributes such as name, preferences, avilability, and pet(s), along with the correpsonding getter and setter methods.

    Pet has attributes such as name, feeding, medicine(s), grooming, and enrichment, along with the corresponding getter and setter methods. It also contains a list of tasks, and methods to add and remove tasks. 

    Task has attributes such as assigned pet, description/name, duration, priority, and due time. It also has a boolean value to keep track of task completion, and a method to mark tasks as complete.

    Scheduler has a reference to owner and a pet as a parameter (since it needs access to both classes to create a recommended task list). It also includes a method to order tasks by priority and by due time. Lastly, its most important method, recommend daily tasks, prints the recommended daily task list based on task priority, due time, duration, and owner availability and preferences.
    
**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
    Yes, in fact, I ended up redoing the entire UML diagram. Originally, the AI pointed out that the Scheduler class was missing a reference to the Owner class, meaning it couldn't access the owner's availability and preferences. After fixing this error, I realized I didn't understand the relationship between the classes enough, so I made the entire UML diagram by hand. 

    By making the UML diagram by hand, I realized I was missing several attributes (owner name, task duration, pet species, etc.). I then asked the AI to review my updated UML and add/remove methods or attributes with reasoning provided. I reviewed the edits it made, which all made sense. The add/remove task methods were moved from the Task class to the Pet class, since it's the pets that have tasks, not the tasks themselves. Some attributes were also changed from list to dictionary since they contained key-value pairs rather than just a list of information.

    Then, I had the AI review the UML again, and it pointed out that having priority and due_time be a plain string made it harder to stort, so I created a system to assign them all integer values.

    Lastly, as the AI suggested, I edited the recommend_daily_tasks function to account for multiple pet functionality (so that the owner is not double-booked.)

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?
    The scheduler considers factors such as task due time, task priority, owner availability, and owner preferences. It sorts the tasks by priority, then by due time, then by preference. I considered priority first since the site clarifies that high-priority tasks MUST be completed today. The algorithm tries to assign all high-priority tasks first. Any tasks that can't be assigned are added to the "Unassigned table." It will assign the task to the earliest available slot that is before the task due time. To decide what was most important, I created several real-world examples and modeled it after how I would organize my tasks.                  

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
    The scheduler will pass on tasks if it can't find a suitable slot for them, adding them to the "Unassigned Tasks" table. To provide some light resolution, the "Unassigned Tasks" table is displayed after the Daily Schedule to warn users that some tasks could not be assigned. The system also sends a Toast warning if the duration of all the high-priority tasks exceed the owner's total availability.

    The owner can also only choose available hours and task due times in 30-minute time blocks, as I didn't want the UI to look overwhelming with a very long selection list. I think the reasonable trade off is that most people block their own time in 30-minute or hourly intervals.   
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?
    The most helpful prompts or questions were when I had a revision I was making to the code, but needed guidance finding all the pieces of code that would need to be updated as a result of said revison. For example, when I switched from a 24-hour day to a 1440-minute day to better assign tasks in the scheduler, I asked the AI to indentify all the code snippets in app.py that I would have to edit as a result of this change. I used it mostly for debugging and refactoring my code to make it more Pythonic.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
    The AI kept suggesting ways to assign tasks to the earliest available slot, but failed to implement it correctly any time I tested it on the site. I decided to write the algorithm down myself on paper and then explained to the AI how to assign tasks based on a 1440-element array where 0=unavailable, 1=available, 2=reserved. Once it made this revision, I created several taste cases both through main.py and the site. 
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
