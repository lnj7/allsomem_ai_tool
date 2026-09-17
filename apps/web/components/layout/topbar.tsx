export function Topbar({ title }: { title: string }) {
  return (
    <header className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-4 sm:px-8">
      <div>
        <p className="text-xs font-medium uppercase tracking-[0.2em] text-indigo-600">Jadon Family creatorOS & co.</p>
        <h1 className="text-lg font-semibold text-navy-900">{title}</h1>
      </div>
      <div className="rounded-full bg-slate-100 px-3 py-1.5 text-sm text-slate-600">Profile</div>
    </header>
  );
}
