import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AudioCraft Text-to-Audio Generator',
  description: 'Generate audio from text prompts using Meta AudioCraft',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="it">
      <body>{children}</body>
    </html>
  )
}

