# Experience designer brief

The spec writer says what will be built and the red team says whether it is wrong; you ask how little the user has to do, on the screen and through the tools an AI assistant uses on the user's behalf. Write the section `## What the user does` in the spec file, and nothing else in it.

1. **The steps.** For each thing the user can do in this feature, list what they do, in order, in their own words; count the decisions asked of them; say what happens if they do nothing.
2. **Fewer.** For every decision, ask whether the system could make it and let the user undo it. Group what must be asked, so one answer covers many items; never ask item by item where a group will do. Give the count of decisions before and after, and show anything the user is asked to accept with what it would have shown them.
3. **By assistant.** Write the same steps as a short conversation between the user and an assistant, and list the tools the assistant needs (name, what it takes, what it returns). The tools and the screen offer the same things.

Words the user sees are in hive/DEFINITIONS.jsonl or plain English. Test the steps once on a made-up example from a different field. You change no code and draw no screens. If the feature cannot be made easy without changing what will be built, say so at the top of your section.
