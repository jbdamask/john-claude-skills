# API reference documentation

Reference code comments and verb forms in generated reference docs. Adapted from the
Google developer documentation style guide (CC BY 4.0).

Apply this guidance as appropriate for the language you're documenting; some of it
doesn't fit every API or every language. This doesn't specify a markup syntax for doc
comments — follow the language's own convention (Javadoc, docstrings, JSDoc, rustdoc,
and so on).

---

## Documentation basics

A complete API reference describes:

- Every class, interface, struct, and similar member (unions in C++, for example).
- Every constant, field, enum, and typedef.
- Every method, including each parameter, the return value, and any exceptions thrown.

Strong recommendations:

- **Put a code sample (roughly 5-20 lines) at the top of each class or interface page.**
- Put all API names, classes, methods, constants, and parameters in code font, and link
  each to its reference page. Most doc generators do this for you.
- Put string literals in code font inside double quotation marks: `"wrap_content"`,
  `"true"`.
- Spell class names exactly as the code does — capitals, no spaces: `ActionBar`.
- **Don't pluralize class names.** Add a plural noun instead: `Intent` objects,
  `Activity` instances — not `Intents` or `Activities`.
- If a class name is also a common word, you can refer to the general concept in
  lowercase, ordinary font: *activities*, *action bar*.

---

## Classes, interfaces, and structs

The first sentence states the intended purpose or function, giving information that
isn't already obvious from the name and signature. Later sentences explain how to use
the API: how to invoke or instantiate it, its key features, best practices, and pitfalls.

Many tools extract the first sentence for class-list summaries, so make it unique,
descriptive, and short. Also:

- **Don't repeat the class name** in the first sentence.
- **Don't write "this class will…" or "this class does…"**
- **Don't use a period before the actual end of the sentence.** Some generators
  naively truncate the short description at the first period — which is one more reason
  to write *for example* rather than *e.g.*

Example, from Android's `ActionBar`:

> A primary toolbar within the activity that may display the activity title,
> application-level navigation affordances, and other interactive items.

---

## Members (constants and fields)

Keep descriptions as brief as possible, and link to the methods that use the constant or
field.

Example, from `ActionBar.DISPLAY_SHOW_HOME`:

> Show 'home' elements in this action bar, leaving more space for other navigation
> elements. This includes logo and icon.
>
> See also: `setDisplayOptions(int)`, `setDisplayOptions(int, int)`

---

## Methods

The first sentence states what action the method performs. Later sentences explain why
and how to use it, any prerequisites for calling it, details about exceptions, and
related APIs.

Document any dependency needed to call the method — a permission, for example — and what
happens if it's missing ("the method throws a `SecurityException`", "the method returns
`null`").

**Use present tense throughout**: "Adds a new bird to the ornithology list." "Returns a
bird."

Note the third-person form. In reference documentation, phrase a method description in
terms of what the method does (*gets*, *lists*, *creates*, *searches*), not what the
developer uses it to do (*get*, *list*, *create*, *search*).

- Recommended: "`tasks.insert`: Creates a new task on the specified task list."
- Not recommended: "`tasks.insert`: Create a new task on the specified task list."

### Opening verbs by method kind

| Method kind | Start the description with |
|---|---|
| Performs an operation and returns data | The verb for the operation: "Adds a new bird to the ornithology list and returns the ID of the new entry." |
| Getter returning a boolean | "Checks whether …" |
| Getter returning anything else | "Gets the …" |
| Turns on an ability or setting | "Sets the …" |
| Updates a property | "Updates the …" |
| Deletes something | "Deletes the …" |
| Registers a callback or element | "Registers …" |
| A callback (often named `onX`) | "Called by …" — for example, "Called by Android when …". Later in the description: "Subclasses implement this method to …" |
| Convenience method constructing the class object | "Creates a …" |

Example, from `Activity.isChangingConfigurations`:

> Checks whether this activity is in the process of being destroyed in order to be
> recreated with a new configuration. This is often used in `onStop` to determine whether
> the state needs to be cleaned up or if it's passed on to the next instance of the
> activity using `onRetainNonConfigurationInstance`.

---

## Parameters

- Capitalize the first word; end with a period.
- Begin non-boolean parameter descriptions with *The* or *A* where you can: "The ID of
  the bird you want to get." "A description of the bird."
- **Boolean parameters that tell the API to do something:** state what happens for each
  value. "`enableCertificateValidation`: If true, validates the SSL certificate before
  proceeding. If false, trusts the certificate without validating it."
- **Boolean parameters that describe an already-established state:** use "True if …;
  false otherwise." — "True if the zoom is set; false otherwise."
- In these descriptions, don't put *true* and *false* in code font or quotation marks.
- **Parameters with default behavior:** describe the behavior for each value or range,
  then state the default using the format `Default:`.

---

## Return values

Be brief; put detail in the class description.

- Anything other than a boolean: start with "The …" — "The bird specified by the given
  ID."
- A boolean: "True if …; false otherwise." — "True if the bird is in the sanctuary; false
  otherwise."

---

## Exceptions

Where the reference generator inserts the word "Throws" automatically, begin with "If
…": "If no key is assigned."

Otherwise begin with "Thrown when …": "Thrown when no key is assigned."

---

## Deprecations

Tell the reader what to use instead. If you track the API with version numbers, say
which version first deprecated it.

Only the first sentence appears in the summary and index, so put the replacement there.
Later sentences can explain why it's deprecated and anything else a developer needs.

If a method is deprecated, tell the reader what to change to make their code work.

> Deprecated. Use `#CameraPose` instead.
>
> Deprecated. Access this field using the `getField` method.

---

## Linking API terms

Link the first instance of each API element — class, method, constant, XML attribute —
in a section, using code font. For later uses of the same element in the same section,
keep the code font but don't link again.

Very common classes don't need a link every time. When you use such a term as a concept
rather than a class, don't put it in code font and don't capitalize it: *activity*,
*service*, *fragment*, *view*, *loader*, *action bar*, *intent*, *content provider*,
*broadcast receiver*, *app widget*. When you mean an actual instance of the class, use
the formal class name and link to it.

- "The `Activity` class is an important part of an application's overall lifecycle…"
- "The user interface for an activity is provided by a hierarchy of views — objects
  derived from the `View` class."

Linking patterns:

- **A class:** use the class name as the link text.
  `<a href="/reference/android/widget/TextView">TextView</a>`
- **A method:** use the method name as a fragment identifier. Include the class name in
  the link text for a static method. Show the full signature when you need to
  distinguish overloads.
  `<a href="/reference/android/app/Activity.html#onCreate(android.os.Bundle)">onCreate(Bundle)</a>`
- **A widget or layout attribute:** link to the page plus the fragment
  `#attr_android:ATTRIBUTE_NAME`.
  `<a href="/reference/android/widget/TextView.html#attr_android:inputType">inputType</a>`
