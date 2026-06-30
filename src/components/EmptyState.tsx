/**
 * Reusable empty-state placeholder for list views.
 */
interface Props {
  title: string;
  description?: string;
  icon?: string;
  action?: { label: string; onClick: () => void };
}

export function EmptyState({ title, description, icon = "\u{1F4ED}", action }: Props) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-slate-700">{title}</h3>
      {description && (
        <p className="mt-2 text-sm text-slate-500 max-w-sm">{description}</p>
      )}
      {action && (
        <button
          onClick={action.onClick}
          className="mt-4 px-4 py-2 bg-slate-900 text-white text-sm rounded hover:bg-slate-700 transition-colors"
        >
          {action.label}
        </button>
      )}
    </div>
  );
}
