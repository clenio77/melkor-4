import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

import Link from "next/link";

export const metadata: Metadata = {
  title: "Kermartin 3.0",
  description: "Assistente de Análise Jurídica",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <header className="sticky top-0 z-50 border-b bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <nav className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
            <div className="font-semibold">Kermartin</div>
            <div className="flex gap-4 text-sm">
              <Link href="/dashboard" className="hover:underline">Dashboard</Link>
              <Link href="/processos" className="hover:underline">Processos</Link>
              <Link href="/analises" className="hover:underline">Análises</Link>
              <Link href="/seguranca" className="hover:underline">Segurança</Link>
              <Link href="/jurisprudencia" className="hover:underline">Jurisprudência</Link>
            </div>
          </nav>
        </header>
        <main className="mx-auto max-w-6xl p-4">
          {children}
        </main>
        <footer className="mt-10 border-t py-6 text-center text-xs text-foreground/60">
          © {new Date().getFullYear()} Kermartin 3.0
        </footer>
      </body>
    </html>
  );
}
