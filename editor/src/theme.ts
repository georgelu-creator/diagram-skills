import type React from "react";
import type { DiagramSpecView } from "./model";

export type ThemeTokens = {
  primary: string;
  accent: string;
  page: string;
  surface: string;
  ink: string;
  muted: string;
  hair: string;
  group: string;
  group_stroke: string;
};

const BASE_ACCENTS = { primary: "#4F46E5", accent: "#14B8A6" };

export const themeTokens: Record<DiagramSpecView["theme"], ThemeTokens> = {
  paper: {
    ...BASE_ACCENTS,
    page: "#F8F7F3",
    surface: "#FFFEFA",
    ink: "#111827",
    muted: "#667085",
    hair: "#DDDCD4",
    group: "#EEF6FF",
    group_stroke: "#93C5FD",
  },
  notion: {
    ...BASE_ACCENTS,
    page: "#FFFFFF",
    surface: "#FFFFFF",
    ink: "#191919",
    muted: "#6B6B6B",
    hair: "#DEDEDE",
    group: "#F7F7F5",
    group_stroke: "#B8B8B3",
  },
  spectrum: {
    ...BASE_ACCENTS,
    page: "#FFFFFF",
    surface: "#FFFFFF",
    ink: "#172033",
    muted: "#526071",
    hair: "#D7E0EA",
    group: "#F8FAFC",
    group_stroke: "#C7D2E0",
  },
  blueprint: {
    primary: "#60A5FA",
    accent: "#22D3EE",
    page: "#0B1930",
    surface: "#102544",
    ink: "#F4F8FF",
    muted: "#A9BDD8",
    hair: "#32547F",
    group: "#122D52",
    group_stroke: "#4F83BD",
  },
  terminal: {
    primary: "#3FB950",
    accent: "#2DD4BF",
    page: "#0C1117",
    surface: "#141B22",
    ink: "#F0F6FC",
    muted: "#9DA7B3",
    hair: "#303A45",
    group: "#111F1B",
    group_stroke: "#2D6A57",
  },
};

export function resolveThemeTokens(view: Pick<DiagramSpecView, "theme" | "brand">): ThemeTokens {
  const base = themeTokens[view.theme];
  const brand = view.brand ?? {};
  return {
    primary: brand.primary ?? base.primary,
    accent: brand.accent ?? base.accent,
    page: brand.page ?? base.page,
    surface: brand.surface ?? base.surface,
    ink: brand.ink ?? base.ink,
    muted: brand.muted ?? base.muted,
    hair: brand.hair ?? base.hair,
    group: brand.group ?? base.group,
    group_stroke: brand.group_stroke ?? base.group_stroke,
  };
}

export function themeStyle(view: Pick<DiagramSpecView, "theme" | "brand">): React.CSSProperties {
  const tokens = resolveThemeTokens(view);
  return {
    "--brand-primary": tokens.primary,
    "--brand-accent": tokens.accent,
    "--vs-page": tokens.page,
    "--vs-surface": tokens.surface,
    "--vs-ink": tokens.ink,
    "--vs-muted": tokens.muted,
    "--vs-hair": tokens.hair,
    "--vs-group": tokens.group,
    "--vs-group-stroke": tokens.group_stroke,
  } as React.CSSProperties;
}
