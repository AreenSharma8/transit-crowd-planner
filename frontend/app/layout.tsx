import type { Metadata, Viewport } from 'next';
import './globals.css';
const basePath=process.env.NEXT_PUBLIC_BASE_PATH||'';
export const metadata:Metadata={title:'Nagar — Transit Crowd Planner',description:'A clearly labelled demo of a Delhi bus journey planner with relative ticketing-activity signals.',applicationName:'Nagar Transit Demo',manifest:`${basePath}/manifest.webmanifest`};
export const viewport:Viewport={themeColor:'#f4f6f2',width:'device-width',initialScale:1};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>}
