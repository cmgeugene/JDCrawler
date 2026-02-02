import { render, screen } from "@testing-library/react";
import { Header } from "./Header";
import { describe, it, expect, vi } from "vitest";

describe("Header", () => {
    it("renders title", () => {
        render(<Header onMenuClick={vi.fn()} />);
        expect(screen.getByText("SYSTEM ONLINE")).toBeInTheDocument();
    });
});
