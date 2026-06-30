import { Component, ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

/**
 * React error boundary to catch and display runtime errors gracefully.
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div className="p-6 rounded-lg border border-red-200 bg-red-50 text-red-800">
            <h2 className="text-lg font-semibold">Something went wrong</h2>
            <p className="text-sm mt-2">
              {this.state.error?.message ?? "An unexpected error occurred."}
            </p>
          </div>
        )
      );
    }
    return this.props.children;
  }
}
