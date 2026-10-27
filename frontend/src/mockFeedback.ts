import type { WritingFeedback, WritingStyle } from "./types";
export const mockFeedback: WritingFeedback = {
  summary:
    "Your paragraph communicates a clear idea, but a few wordy phrases and one run-on sentence reduce its impact. Overall, the logic flows well.",

  grammar: [
    {
      original: "the the importance of",
      suggestion: "the importance of",
      explanation: "Duplicated word. Remove the repeated 'the'.",
      severity: "high",
    },
    {
      original: "since last semester we of learned",
      suggestion: "since last semester, we have learned",
      explanation: "Missing comma after a time phrase, and 'of learned' is a grammatical error (should be 'have learned').",
      severity: "high",
    },
  ],

  clarity: [
    {
      original:
        "In the event that a student decides to participate in the extracurricular activity, they must complete the registration form no later than the last day of the semester.",
      suggestion:
        "If a student joins the activity, they must register by the last day of the semester.",
      explanation:
        "'In the event that' → 'If'; 'decides to participate in the extracurricular activity' → 'joins the activity'; 'complete the registration form no later than' → 'register by'. The shorter version says the same thing in half the words.",
      severity: "medium",
    },
  ],

  conciseness: [
    {
      original: "actually, in fact, really",
      suggestion: "(remove all three)",
      explanation:
        "These are filler words that add no information. Removing them makes your point more direct and confident.",
      severity: "low",
    },
    {
      original: "It is important to note that",
      suggestion: "Note that",
      explanation: "'It is important to note that' is a four-word way to say 'Note that'.",
      severity: "low",
    },
  ],

  tone: {
    detected: "Mostly formal/academic, with occasional conversational slips",
    consistency: "Generally consistent, but one sentence reads like spoken language",
    note: "Aim for a steady academic register. Avoid contractions ('it's' → 'it is') and interjections in formal writing.",
  },

  strengths: [
    "Your central argument is stated clearly in the first sentence.",
    "You use specific examples rather than vague generalizations.",
    "Paragraph structure follows a logical progression (claim → evidence → conclusion).",
  ],
};