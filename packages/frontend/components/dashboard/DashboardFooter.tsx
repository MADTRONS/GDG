import Link from 'next/link';

export function DashboardFooter() {
  return (
    <footer className="border-t bg-gray-50 py-6" role="contentinfo">
      <div className="container mx-auto px-4">
        <div className="flex flex-col sm:flex-row items-center justify-center gap-6 text-sm text-gray-600">
          <Link 
            href="/help" 
            className="hover:text-blue-600 hover:underline"
            aria-label="Get help and frequently asked questions"
          >
            Help / FAQ
          </Link>
          <span className="hidden sm:inline" aria-hidden="true"></span>
          <Link 
            href="/emergency" 
            className="hover:text-red-600 hover:underline font-medium"
            aria-label="Access emergency resources"
          >
            Emergency Resources
          </Link>
          <span className="hidden sm:inline" aria-hidden="true"></span>
          <span className="text-gray-500">
            National Suicide Prevention Lifeline: 988
          </span>
        </div>
      </div>
    </footer>
  );
}
