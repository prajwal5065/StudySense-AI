/**
 * Application-wide constants for StudySense AI.
 */

export const APP_NAME = "StudySense AI";
export const APP_VERSION = "1.0.0";

export const MAX_UPLOAD_SIZE_MB = 50;
export const SUPPORTED_FILE_TYPES = [".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"];

export const DEFAULT_QUIZ_QUESTIONS = 10;
export const DEFAULT_PLANNER_WEEKS = 4;

export const CHAT_MAX_HISTORY = 50;

export const DIFFICULTY_LABELS = {
  easy: "Easy",
  medium: "Medium",
  hard: "Hard",
} as const;
