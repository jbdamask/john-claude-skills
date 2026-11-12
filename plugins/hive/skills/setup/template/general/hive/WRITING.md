# Writing for people

These rules apply to every text a person reads: pages, reports, issue briefs and comments, messages to {{owner}}, and anything the product shows its user. Bead notes and commit messages are for agents and are exempt. The first five follow Shreya Shankar, "Five Principles for Generating Readable AI Text in Bulk" (https://fsdatalab.github.io/blog/agent-text-at-scale/).

1. **Start each item with its subject or its verb**, in one form and tense per kind of item.
2. **Put the words that tell items apart first**; readers often see only the first two words.
3. **Use one sentence structure per kind of item and one word per concept.**
4. **Vary items only when the difference means something**; readers assume every difference matters.
5. **Match the verb to the news**, so good news reads as good and trouble as trouble.
6. **Write whole sentences a newcomer can read once**: "7 days", not "7 d"; "against", not "vs". Symbols and short headers go only in tables, with a legend.
7. **Use the field's own words; never invent one where a standard term exists.** Terms live in one place, hive/DEFINITIONS.jsonl (`python3 hive/tools/term.py <term>`); a new term gets its entry there first, and a document links to it rather than defining it again.
8. **No hyperbole**: every "every", "never", "all", "only" and every number is checked against the code or the data, or softened to what is true.

## Writing for {{owner}}
Lead with the answer, then only what is needed to act or decide; big picture before detail. When something said earlier was wrong, say so plainly in the same reply. A command for {{owner}} to run is one line that works exactly as pasted.
