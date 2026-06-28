import { describe, expect, it } from "vitest";
import { clientFormSchema, contactFormSchema } from "@/forms/clientSchemas";

describe("clientFormSchema", () => {
  it("validates a minimal client", () => {
    const result = clientFormSchema.safeParse({ name: "Acme Corp" });
    expect(result.success).toBe(true);
  });

  it("rejects empty name", () => {
    const result = clientFormSchema.safeParse({ name: "" });
    expect(result.success).toBe(false);
  });

  it("rejects invalid website URL", () => {
    const result = clientFormSchema.safeParse({ name: "Acme", website: "not-a-url" });
    expect(result.success).toBe(false);
  });
});

describe("contactFormSchema", () => {
  it("validates a contact with required fields", () => {
    const result = contactFormSchema.safeParse({
      first_name: "John",
      last_name: "Doe",
      email: "john@example.com",
    });
    expect(result.success).toBe(true);
  });
});
