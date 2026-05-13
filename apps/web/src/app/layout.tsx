import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Monarqhs Analytics",
  description: "Personal investor/trader analytics dashboard for IDX and US markets",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
