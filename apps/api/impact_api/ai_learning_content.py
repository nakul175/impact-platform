"""Practical editorial lessons; progress is self-recorded, never a certification."""

from copy import deepcopy
from types import MappingProxyType

# These original positional keys keep their published meaning. Never derive aliases
# from the current lesson order, or reuse a retired key for different material.
LEGACY_LESSON_ALIASES = MappingProxyType(
    {
        "foundations:0": "foundations:safe-practice-task",
        "foundations:1": "foundations:verify-claims",
        "foundations:2": "foundations:choose-useful-method",
        "foundations:3": "foundations:data-boundary",
        "pilot_design:0": "pilot_design:problem-and-owner",
        "pilot_design:1": "pilot_design:measure-baseline",
        "pilot_design:2": "pilot_design:test-difficult-cases",
        "pilot_design:3": "pilot_design:review-and-stop-rule",
        "procurement:0": "procurement:testable-requirements",
        "procurement:1": "procurement:comparable-offers",
        "procurement:2": "procurement:whole-cost-and-exit",
        "procurement:3": "procurement:data-and-delivery-terms",
    }
)

_LESSONS = {
    "foundations": [
        (
            "foundations:safe-practice-task",
            "Start with a safe practice task",
            "Choose a small task with public or invented information. Give the tool a goal, audience, constraints and an example of the format you need. Compare the draft with your own checklist before sharing it. A useful prompt does not replace a responsible reviewer.",
            "Invent a community workshop with a date, venue and three topics. Ask for a short invitation using only those facts. Check every detail against your invented brief.",
            "What belongs in a first practice prompt?",
            ["A beneficiary case file", "Invented workshop details", "A colleague's password"],
            1,
            "Invented details let you practise without disclosing people's information.",
        ),
        (
            "foundations:verify-claims",
            "Check claims before using a draft",
            "An answer can sound confident and still be wrong. List the claims that matter, find the underlying evidence, and check that each source supports the specific claim. If the source cannot be checked, remove the claim or label the uncertainty. A generated link alone is not evidence.",
            "Write a sample paragraph containing two invented statistics. Mark both unsupported. Rewrite it without presenting either figure as a fact.",
            "A generated answer cites a link you cannot verify. What next?",
            [
                "Publish because it has a citation",
                "Ask it to sound more confident",
                "Verify independently or omit the claim",
            ],
            2,
            "A citation must be inspected and support the claim before you rely on it.",
        ),
        (
            "foundations:choose-useful-method",
            "Choose the simplest useful method",
            "Use a checklist for fixed steps and a spreadsheet or governed calculation for exact arithmetic. AI may help draft or explain, but it should not replace the approved rules that determine official results. Compare a manual method with an AI-assisted method on the same task.",
            "Split a monthly report into tasks: add approved totals, draft an introduction, check required sections. Choose arithmetic, AI assistance or a checklist for each, and explain why.",
            "Which method should determine an official programme total?",
            [
                "An approved deterministic calculation",
                "The most fluent AI answer",
                "An average of generated guesses",
            ],
            0,
            "Official totals need reproducible calculations over approved records.",
        ),
        (
            "foundations:data-boundary",
            "Write a data boundary",
            "Agree what staff may enter into each tool before a real pilot. Identify personal information, confidential documents and credentials. Name the person who reviews provider terms and approves permitted data. Removing names may leave other identifying details; do not assume a file is safe just because a name is absent.",
            "Write two lists for your workshop task: allowed public facts and prohibited personal or confidential details. Add a reviewer and an escalation step for uncertain material.",
            "A case summary has no name but includes an address and medical details. Is it automatically safe?",
            [
                "Yes, names are the only identifier",
                "No, review the remaining information",
                "Yes, if the prompt is short",
            ],
            1,
            "Other details can identify a person and reveal sensitive information.",
        ),
    ],
    "pilot_design": [
        (
            "pilot_design:problem-and-owner",
            "Name one problem and an owner",
            "Define the task, intended users, responsible owner and the human decision the tool supports. Keep the first pilot narrow enough to inspect every output. Describe the benefit you hope to test rather than promising a saving before measurement.",
            "Draft a one-sentence pilot goal for public workshop invitations. Add an owner role, intended users and who reviews each invitation.",
            "Which scope is easier to evaluate?",
            [
                "Transform all organisational work",
                "Replace every reviewer",
                "Draft one type of invitation with human review",
            ],
            2,
            "A bounded task gives you observable outputs and a clear review responsibility.",
        ),
        (
            "pilot_design:measure-baseline",
            "Measure the current process",
            "Record a baseline before changing the task: staff time, corrections, output quality and accessibility. Include review time when measuring the pilot. Compare similar tasks and record uncertainty rather than treating one fast example as proof of a lasting improvement.",
            "Create a synthetic baseline table for three invitations. Include drafting minutes, review minutes and factual corrections. Design the same columns for the pilot.",
            "What belongs in a fair time comparison?",
            [
                "Drafting and review time for both methods",
                "Only AI drafting time",
                "The tool's marketing estimate",
            ],
            0,
            "Review and correction effort are part of the work the team actually performs.",
        ),
        (
            "pilot_design:test-difficult-cases",
            "Test ordinary and difficult cases",
            "Prepare representative examples and cases where the tool should stop or ask for clarification. Include missing facts, unsupported claims and attempts to introduce prohibited data. Keep the expected outcome for each case explicit. Use synthetic examples during this exercise.",
            "Write three tests: a complete invitation brief, one without a date, and one containing invented prohibited personal details. Specify what the tool and reviewer should do for each.",
            "What should a test with a missing date expect?",
            ["A convincing invented date", "A clarification or a clearly marked gap", "Silent publication"],
            1,
            "The tool should expose missing information rather than fabricate it.",
        ),
        (
            "pilot_design:review-and-stop-rule",
            "Agree a review and stop rule",
            "Name the reviewer, acceptance checks, incident contact and conditions that pause the pilot. Set a review date and decide who may expand the scope. A completed checklist records an action; it does not establish that a pilot is approved or safe for wider use.",
            "Write a stop rule for your invitation pilot, such as pausing after a factual error reaches an audience. Name who investigates and who decides whether to resume.",
            "Who decides whether to expand the pilot?",
            [
                "The tool itself",
                "Whoever clicked a checklist first",
                "The organisation's accountable decision owner",
            ],
            2,
            "Scope changes need a human decision under the organisation's own authority.",
        ),
    ],
    "procurement": [
        (
            "procurement:testable-requirements",
            "Turn a goal into testable requirements",
            "Describe the task, users, languages, access needs, data boundary and required outputs. Separate essential requirements from preferences. Ask each supplier to demonstrate the same acceptance cases so offers can be compared on evidence.",
            "Write three essential requirements for workshop invitations and one preference. Add a pass/fail test for every essential requirement.",
            "Which requirement is testable?",
            [
                "Retains every supplied date exactly in ten synthetic cases",
                "Has impressive AI",
                "Feels innovative",
            ],
            0,
            "An observable expected result supports a fair demonstration and acceptance decision.",
        ),
        (
            "procurement:comparable-offers",
            "Ask for comparable written offers",
            "Give suppliers the same brief and ask them to state assumptions, exclusions, implementation work, support, pricing units and offer validity. A directory entry is a starting point for research; it is not a quote, certification or commitment to supply.",
            "Draft a short request asking two suppliers to respond to the same requirements and tests. Ask each to identify features that require a different subscription.",
            "What does a catalogue listing establish?",
            ["A binding price", "A researched starting point for further checks", "An approved purchase"],
            1,
            "Written offers and your own review are still needed before a purchase decision.",
        ),
        (
            "procurement:whole-cost-and-exit",
            "Compare the whole cost and exit",
            "Include setup, subscriptions, usage, integrations, staff training, review, support and exit. State the currency, period and assumptions used in a quote. Ask how spending is capped and how data and configuration can be exported when the arrangement ends.",
            "Build a blank cost checklist for two offers. Include recurring fees, staff review time, optional features and export/exit work. Leave unquoted amounts unknown.",
            "A supplier has not quoted integration costs. What do you record?",
            ["Zero", "A guessed discount", "Unknown; request the missing cost"],
            2,
            "Missing costs should remain visible rather than making one offer appear cheaper.",
        ),
        (
            "procurement:data-and-delivery-terms",
            "Review data terms and delivery responsibilities",
            "Ask what information leaves your environment, who can access it, where it is processed, how it is retained, and whether the relevant plan's terms permit your intended use. Assign integration, support and incident responsibilities. Have the authorised people review the written terms; the directory does not make a legal or compliance decision.",
            "Add five supplier questions covering permitted data, retention, access, support and exit. Identify which internal roles must review the answers.",
            "Can a marketing statement replace review of your plan's written data terms?",
            [
                "No; check the relevant terms and intended use",
                "Yes, if the brand is familiar",
                "Yes, if the plan is discounted",
            ],
            0,
            "Data handling depends on the actual service, plan, terms and configuration you will use.",
        ),
    ],
}


def lesson_keys():
    """Currently available identifiers, attached to meaning rather than position."""
    return frozenset(lesson[0] for lessons in _LESSONS.values() for lesson in lessons)


def canonical_lesson_key(key):
    """Resolve a known alias without inventing a meaning for unavailable content."""
    canonical = LEGACY_LESSON_ALIASES.get(key, key)
    return canonical if canonical in lesson_keys() else None


def enrich_learning_paths(paths):
    result = deepcopy(paths)
    for path in result:
        path["lessons"] = [
            {
                "key": key,
                "title": title,
                "lesson": lesson,
                "exercise": exercise,
                "check": {
                    "question": question,
                    "options": list(options),
                    "answer": answer,
                    "explanation": explanation,
                },
            }
            for key, title, lesson, exercise, question, options, answer, explanation in _LESSONS[path["id"]]
        ]
    return result
