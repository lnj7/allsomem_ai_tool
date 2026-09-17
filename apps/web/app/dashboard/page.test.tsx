import { render, screen, waitFor } from "@testing-library/react";
import { vi } from "vitest";
import DashboardPage from "@/app/dashboard/page";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: React.ReactNode }) => <a href={href}>{children}</a>,
}));

vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard",
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
}));

vi.mock("@/lib/api/health", () => ({
  getApiHealth: vi.fn().mockResolvedValue({ status: "ok", service: "creatoros-api" }),
}));

vi.mock("@/lib/api/product", () => ({
  authApi: { me: vi.fn().mockResolvedValue({ full_name: "Test User" }), logout: vi.fn() },
  productApi: {
    dashboard: vi.fn().mockResolvedValue({
      creator_name: "Test User",
      followers: 0,
      content_count: 0,
      ready_count: 0,
      profile_completion: 10,
      today_plan: [],
      ai_configured: false,
    }),
  },
}));

describe("dashboard page", () => {
  it("renders journey widgets and connected backend status", async () => {
    render(<DashboardPage />);
    expect(screen.getByText(/Good morning/)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("Connected")).toBeInTheDocument();
    });
  });
});
