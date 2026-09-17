import { EmptyState } from "@/components/ui/empty-state";
import { AppShell } from "@/components/layout/app-shell";

export function ComingSoonPage({ title }: { title: string }) {
  return (
    <AppShell title={title}>
      <EmptyState
        title="Coming in the next Jadon Family creatorOS & co. milestone."
        description="This screen is a placeholder so navigation is in place. Functionality is not implemented yet."
      />
    </AppShell>
  );
}
