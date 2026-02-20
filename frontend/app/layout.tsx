import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Dungeon Master",
  description: "An AI-powered storytelling adventure game",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gradient-to-br from-gray-900 to-gray-800 text-gray-100 min-h-screen">
        {children}
      </body>
    </html>
  );
}
