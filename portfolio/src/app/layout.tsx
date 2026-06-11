import type { Metadata } from 'next';
import './globals.css';
import LenisProvider from '@/components/LenisProvider';
import CustomCursor from '@/components/CustomCursor';

export const metadata: Metadata = {
  title: 'Nacho Palmeri | Neural Command Center',
  description: 'Builder obsesionado con IA, sistemas autónomos y automatización. 44 workflows, 17 agentes, 78 skills.',
  keywords: ['AI', 'agents', 'automation', 'Next.js', 'Python', 'Claude', 'portfolio'],
  authors: [{ name: 'Nacho Palmeri' }],
  openGraph: {
    title: 'Nacho Palmeri | Neural Command Center',
    description: 'Builder obsesionado con IA, sistemas autónomos y automatización.',
    url: 'https://ignaciopalmeri.vercel.app',
    type: 'website',
    siteName: 'Nacho Palmeri',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Nacho Palmeri | Neural Command Center',
    description: '44 workflows, 17 agentes, 78 skills. Builder obsesionado con IA.',
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#0a0a0a" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="bg-[#0a0a0a] text-gray-100 antialiased">
        <LenisProvider />
        <CustomCursor />
        {children}
      </body>
    </html>
  );
}
