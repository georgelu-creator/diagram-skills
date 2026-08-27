import { describe, expect, it } from "vitest";
import { resolveThemeTokens, themeStyle, themeTokens } from "./theme";

describe("editor themes", () => {
  it("defines a distinct complete token set for every supported theme", () => {
    const entries = Object.entries(themeTokens);
    expect(entries).toHaveLength(5);
    entries.forEach(([, tokens]) => {
      expect(Object.keys(tokens).sort()).toEqual([
        "accent", "group", "group_stroke", "hair", "ink", "muted", "page", "primary", "surface",
      ]);
    });
    expect(new Set(entries.map(([, tokens]) => JSON.stringify(tokens))).size).toBe(entries.length);
  });

  it("applies every brand override to canvas CSS variables", () => {
    const brand = {
      primary: "#111111", accent: "#222222", page: "#333333", surface: "#444444", ink: "#555555",
      muted: "#666666", hair: "#777777", group: "#888888", group_stroke: "#999999",
    } as const;
    expect(resolveThemeTokens({ theme: "paper", brand })).toEqual(brand);
    expect(themeStyle({ theme: "paper", brand })).toMatchObject({
      "--brand-primary": "#111111",
      "--brand-accent": "#222222",
      "--vs-page": "#333333",
      "--vs-surface": "#444444",
      "--vs-ink": "#555555",
      "--vs-muted": "#666666",
      "--vs-hair": "#777777",
      "--vs-group": "#888888",
      "--vs-group-stroke": "#999999",
    });
  });
});
