import type { WritingFeedback, WritingStyle } from "./types";

export interface Issue {
  original: string;
  suggestion: string;
  explanation: string;
  severity: Severity;
}

export interface ToneAssessment {
  detected: string;
  consistency: string;
  note: string;
}

export interface WritingFeedback {
  summary: string;
  grammar: Issue[];
  clarity: Issue[];
  conciseness: Issue[];
  tone: ToneAssessment;
  strengths: string[];
}

export type WritingStyle = "academic" | "professional" | "casual";