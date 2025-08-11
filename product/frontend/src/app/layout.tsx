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
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <nav className="p-4 border-b flex gap-4">
          <Link href="/dashboard">Dashboard</Link>
          <Link href="/processos">Processos</Link>
          <Link href="/analises">Análises</Link>
          <Link href="/seguranca">Segurança</Link>
          <Link href="/jurisprudencia">Jurisprudência</Link>
        </nav>
        {children}
      </body>
    </html>
  );
}
