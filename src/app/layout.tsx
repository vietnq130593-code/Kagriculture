import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "KaggressurE Arena — v18",
  description: "Sân đấu AI agent trên mô phỏng nông trại KaggressurE — engine kaggle-environments 1.32.7, 720 turn, ai nhiều tiền hơn thắng. v18 nền jaxa623 Beyond 48-0.",
  keywords: ["Kaggle", "KaggressurE", "arena", "battle observer", "agent", "v18", "jaxa623"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-background text-foreground`}
      >
        {children}
        <Toaster />
      </body>
    </html>
  );
}
