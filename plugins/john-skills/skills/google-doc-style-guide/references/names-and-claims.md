# Names, claims, and content you don't own

Product and feature names, trademarks, excessive claims, future features, timeless
documentation, and third-party content. Adapted from the Google developer documentation
style guide (CC BY 4.0).

---

## Product names

**Capitalization.** Follow the official capitalization for brands, companies, software,
products, services, features, and terms defined by companies and open source
communities. Google product names are generally title case — every word capitalized
except prepositions like *of* and *on* and articles like *a* and *the* — except when
you're matching a UI label.

- In a Kubernetes context, follow the Kubernetes docs: "A Job creates one or more Pods."
- If an official name starts with a lowercase letter, keep it lowercase even at the start
  of a sentence — but it's better to rewrite so it isn't first: "You can use macOS to run
  the app," not "macOS can run the app."

**Feature names.** A feature is a distinctive capability of a product, usually described
in terms of what it does. Feature names are generally lowercase unless officially
capitalized. When you're unsure, follow the precedent in other documents about the
feature, and match a UI label if you're referring to one.

**Don't abbreviate product names.** Use the full trademarked name, except when matching a
UI label — and then make clear you mean the product, not something else with a similar
name. Consider whether you need the product name throughout the document at all: once
you've established you're discussing Anthos Service Mesh, you can often frame the rest
around the concept of a service mesh.

**Articles.** Don't use *the* before a product name, unless the name is modifying
something else. Do use *the* before tool and API names.

| Recommended | Not recommended |
|---|---|
| Using Cloud Datastore with Cloud Dataproc | Using the Cloud Datastore with Cloud Dataproc |
| The Cloud Datastore options page | |
| The Google Cloud console · The Transcoder API · The `gcloud` CLI | |

With an indefinite article, watch the sound: *An Anthos Service Mesh environment*, but
*A Service Mesh environment*.

**Products as services.** It's fine to call products *services* — "the Compute Engine
service." If *services* becomes ambiguous, use the product names.

**Never use a product or feature name as a verb.**

**Possessives and plurals.** Don't form either from a product name, feature name, or
trademark. See `mechanics.md`.

---

## Trademarks

Follow whatever usage guidelines the trademark owner provides, including for marking and
attribution.

**Use a trademark only as a modifier** — always modifying a noun, never as a noun by
itself, and never as a verb. Never form a possessive or a plural from a trademark, and
never alter it in any way.

| Recommended | Not recommended |
|---|---|
| Another option is to use a Chromebook notebook computer. | Another option is to use a Chromebook. |
| | Chromebook's features rely on an internet connection. |
| | For information about Chromebook computers, google "notebook computers" |

---

## Avoid excessive claims

An excessive claim is an assertion that:

- makes a statement about performance or cost that the reader can't easily verify from
  available data;
- makes a statement about security that a single incident would invalidate; or
- could be read as subjective or disparaging, especially about a third-party product.

Judge the claim not only against what's true today but against what might be true later.

- **Avoid superlatives** — *best*, *simplest*, *fastest*, *never*, *always*. Be careful
  with *ensure* and *guarantee*; use them only when something truly can be.
- **Cite your source** for any specific performance claim.
- **Never claim a product is secure.** A single compromise invalidates the documentation.
  "Helps with security" or "is designed for security" stays true either way.
- **Be careful about competitors.** A claim about another product may be wrong because
  you misread how it works, or may become wrong at their next release.

Write factually and objectively, limited to verifiable information that stays true over
the document's lifespan.

| Recommended | Not recommended |
|---|---|
| Our product distributes datasets and computation in memory across a cluster, and therefore it can be faster for this scenario than ExampleCorporation's product. For more information, see Performance comparison. | Our product is faster than ExampleCorp's product. |
| Using our security product is part of an overall strategy that helps prevent account takeovers from phishing attacks. | Our security product prevents account takeovers from phishing attacks. |

---

## Future features

**Don't document future features or products, even in innocuous ways.** Don't
pre-announce anything unless legal counsel has approved it.

---

## Timeless documentation

Timeless documentation avoids words and phrases that anchor the text to a moment in time
or assume knowledge of earlier or later versions. Document the current version.

This matters most for documents that get read long after they're written. *Now*, *new*,
and *currently* can make documentation inaccurate, outdated, or meaningless. It also
reduces maintenance and avoids assuming the reader knows earlier versions.

| Recommended | Not recommended |
|---|---|
| These subcommands let you interact with HTTP load balancing. | These **new** subcommands let you interact with HTTP load balancing. |
| The following command-line options aren't supported: | The following command-line options aren't **currently** supported: |
| The emulator supports the following filters: | The emulator **now** supports the following filters: |

### Categories of problem words

- **Words that make promises or project plans.** In descriptions of product capability,
  *at present*, *as of this writing*, and *eventually* can prematurely disclose plans or
  imply that something might change. Don't use them there.
- **Words that are already implied.** Documentation is assumed to be current unless it
  names a release version, so *currently* and *as of this writing* add nothing.
- **Words that go stale quickly** — *soon*, *latest*.
- **Words that assume prior knowledge.** If you must use *new*, give a reference point:
  "The January 14, 2021 release of BigQuery includes a new resource panel."

### Words to avoid in product and reference documentation

*as of this writing · currently · does not yet · eventually · existing · future, in the
future · latest · new, newer · now · old, older · presently, at present · soon*

### Where time-anchored words are fine

Procedural and time-stamped content: press releases, blog posts, release notes.
*New* is fine in a post announcing updates. *Soon* is fine in procedural content
describing a state change: "The VM goes offline soon after you send the shutdown
command."

---

## Third-party content

**Don't copy content from another source** — it might violate copyright. Paraphrase and
link instead. This covers text, images, code, logos, and speech.

| Recommended | Not recommended |
|---|---|
| A recovery point objective (RPO), which is the maximum acceptable length of time during which data might be lost from your app due to a major incident. | Recovery Point Objective (RPO): "RPO is the maximum targeted period in which data (transactions) might be lost from an IT service due to a major incident" (https://en.wikipedia.org/wiki/…). |

Unless you're certain your organization owns the asset, avoid copying from:

- **Third-party sources** — documentation, websites, books, blogs, videos, images,
  podcasts.
- **Reference sources** — dictionaries, encyclopedias, Wikipedia.
- **Open source product documentation.** OSS licenses range from "no reuse without
  attribution" to complete freedom. Don't assume. When in doubt, don't.
- **GitHub content.** Different users adopt different licenses. Don't assume. When in
  doubt, don't.
