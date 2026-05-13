// Re-exports from generated types (populated by codegen)
// export type * from "./generated/api";

// Hand-written shared constants
export const SYSTEM_USER_ID = "00000000-0000-0000-0000-000000000001" as const;

export type StrategySignal = "buy" | "sell" | "hold" | "neutral";
export type NotificationLevel = "info" | "warning" | "error";
export type PipelineStatus = "running" | "success" | "partial" | "failed";
