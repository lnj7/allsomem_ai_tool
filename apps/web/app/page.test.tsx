import { render, screen } from "@testing-library/react";
import { vi } from "vitest";
import LandingPage from "@/app/page";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: React.ReactNode }) => <a href={href}>{children}</a>,
}));

describe("landing page", () => {
  it("renders the hero and CTAs", () => {
    render(<LandingPage />);
    expect(screen.getByText("Your AI Creator Manager")).toBeInTheDocument();
    expect(screen.getByText("Start Building My Profile")).toBeInTheDocument();
    expect(screen.getByText("Create Content")).toBeInTheDocument();
  });
});
