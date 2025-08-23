import type React from "react"
import type { Metadata } from "next"
import { DM_Sans } from "next/font/google"
import "./globals.css"

const dmSans = DM_Sans({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-dm-sans",
})

export const metadata: Metadata = {
  title: "智能摄影分析 - AI Photography Assistant",
  description: "使用AI分析照片构图和曝光参数，自动配置iPhone相机设置",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="zh-CN" className={`${dmSans.variable} antialiased`}>
      <body className="font-sans">{children}</body>
    </html>
  )
}
