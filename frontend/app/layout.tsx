import type { Metadata } from 'next'
import './globals.css'
export const metadata: Metadata={title:'ITSM Intelligence — SLA & Service Health Command Center',description:'Interactive ITSM analytics for SLA risk, change impact, root cause, service health, and accountable actions.'}
export default function RootLayout({children}:Readonly<{children:React.ReactNode}>){return <html lang="en"><body>{children}</body></html>}
