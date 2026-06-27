import { describe, expect, it } from "vitest";
import { loginSchema, registerSchema } from "@/forms/authSchemas";

describe("authSchemas", () => {
  it("validates login form", () => {
    const result = loginSchema.safeParse({
      email: "user@example.com",
      password: "secret",
    });
    expect(result.success).toBe(true);
  });

  it("rejects weak register password", () => {
    const result = registerSchema.safeParse({
      organization_name: "Acme",
      first_name: "Jane",
      last_name: "Doe",
      email: "jane@acme.com",
      password: "weak",
    });
    expect(result.success).toBe(false);
  });

  it("accepts valid register form", () => {
    const result = registerSchema.safeParse({
      organization_name: "Acme Recruiters",
      first_name: "Jane",
      last_name: "Doe",
      email: "jane@acme.com",
      password: "SecurePass123",
    });
    expect(result.success).toBe(true);
  });
});
