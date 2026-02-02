import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";

describe("Simple", () => {
    it("works", () => {
        expect(true).toBe(true);
    });

    it("renders react", () => {
        render(<div>Hello </div>);
        expect(screen.getByText("Hello")).toBeInTheDocument();
    });
});
