import type { Metadata } from "next";
import "./globals.css";
import { Activity, ShieldAlert, Target, Settings, Layers } from "lucide-react";
import Link from "next/link";

export const metadata: Metadata = {
  title: "PRISM Dashboard",
  description: "Threat Actor Attribution Dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen flex bg-midnight text-platinum">
        <aside className="w-64 glass-panel m-4 flex flex-col p-6 sticky top-4 h-[calc(100vh-2rem)] shrink-0">
          <div className="flex items-center gap-3 mb-10">
            <ShieldAlert className="text-cream" size={32} />
            <h1 className="text-xl font-bold tracking-wider text-cream">PRISM</h1>
          </div>

          <nav className="flex-1 space-y-4">
            <Link href="/" className="flex items-center gap-3 p-3 rounded-lg hover:bg-white/10 transition-colors">
              <Activity size={20} />
              <span>Dashboard</span>
            </Link>
            <Link href="/investigation/TA-017" className="flex items-center gap-3 p-3 rounded-lg hover:bg-white/10 transition-colors">
              <Target size={20} />
              <span>Active Investigation</span>
            </Link>
            <Link href="/actor-clusters" className="flex items-center gap-3 p-3 rounded-lg hover:bg-white/10 transition-colors">
              <Layers size={20} />
              <span>Actor Clusters</span>
            </Link>
          </nav>

          <Link href="/settings" className="mt-auto flex items-center gap-3 p-3 rounded-lg hover:bg-white/10 transition-colors">
            <Settings size={20} />
            <span>Settings</span>
          </Link>
        </aside>
        <main className="flex-1 p-4 overflow-y-auto">
          {children}
        </main>
      </body>
    </html>
  );
}
