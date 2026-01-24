import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Study Planner",
  description:
    "Convert PDFs to study notes and get personalized study recommendations",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50">{children}</body>
    </html>
  );
}
