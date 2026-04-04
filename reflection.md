# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
    There are four main classes: owner, pet, task, and scheduler. 
    Owner has attributes such as name, preferences, avilability, and pet(s), along with the correpsonding getter and setter methods.
    Pet has attributes such as name, feeding, medicine(s), grooming, and enrichment, along with the corresponding getter and setter methods. It also contains a list of tasks, and methods to add and remove tasks. 
    Task has attributes such as assigned pet, description/name, duration, priority, and due time. It also has a boolean value to keep track of task completion, and a method to mark tasks as complete.
    Scheduler has a reference to owner and a pet as a parameter (since it needs access to both classes to create a recommended task list). It also includes method to order tasks by priority and by due time. Lastly, it's most important method, recommend daily tasks, prints the recommended daily task list based on task priority, due time, duration, and owner availability and preferences.
    
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
