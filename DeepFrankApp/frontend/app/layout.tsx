import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'DeepFrank - Cat Emotional Analysis',
  description: 'Analyze your cat\'s emotional state using deep learning',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

