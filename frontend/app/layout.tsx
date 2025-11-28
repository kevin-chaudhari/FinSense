"use client"

import "./globals.css"
import { Inter } from "next/font/google"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { FiHome, FiDollarSign, FiHelpCircle, FiBarChart2, FiSun, FiMoon } from "react-icons/fi"
import type React from "react" // Added import for React

const inter = Inter({ subsets: ["latin"] })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [darkMode, setDarkMode] = useState(false)
  const pathname = usePathname()

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark")
    } else {
      document.documentElement.classList.remove("dark")
    }
  }, [darkMode])

  const navItems = [
    { path: "/", icon: FiHome, label: "Home" },
    { path: "/update-transaction", icon: FiDollarSign, label: "Update Transaction" },
    { path: "/ask-question", icon: FiHelpCircle, label: "Ask Question" },
    { path: "/visualize-data", icon: FiBarChart2, label: "Visualize Data" },
  ]

  return (
    <html lang="en" className={darkMode ? "dark" : ""}>
      <body
        className={`${inter.className} bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen flex flex-col transition-colors duration-300`}
      >
        <header className="bg-white dark:bg-gray-800 shadow-lg transition-colors duration-300">
          <div className="container mx-auto px-4 py-4">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <Link
                href="/"
                className="text-2xl font-bold text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 transition-colors mb-4 md:mb-0"
              >
                Financial App
              </Link>
              <nav className="w-full md:w-auto">
                <ul className="flex flex-wrap justify-center md:justify-end space-x-2 md:space-x-4">
                  {navItems.map((item) => (
                    <li key={item.path}>
                      <Link
                        href={item.path}
                        className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                          pathname === item.path
                            ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-200"
                            : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                        }`}
                      >
                        <item.icon className="w-5 h-5 mr-1" />
                        <span>{item.label}</span>
                        {pathname === item.path && (
                          <motion.div
                            className="absolute bottom-0 left-0 w-full h-0.5 bg-indigo-600 dark:bg-indigo-400"
                            layoutId="underline"
                            transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                          />
                        )}
                      </Link>
                    </li>
                  ))}
                  <li>
                    <button
                      onClick={() => setDarkMode(!darkMode)}
                      className="flex items-center px-3 py-2 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
                      aria-label="Toggle dark mode"
                    >
                      {darkMode ? <FiSun className="w-5 h-5" /> : <FiMoon className="w-5 h-5" />}
                    </button>
                  </li>
                </ul>
              </nav>
            </div>
          </div>
        </header>
        <main className="flex-grow container mx-auto px-4 py-8">
          <motion.div
            key={pathname}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            {children}
          </motion.div>
        </main>
        <footer className="bg-white dark:bg-gray-800 text-center p-4 transition-colors duration-300">
          <p>&copy; 2025 Financial App. All rights reserved.</p>
        </footer>
      </body>
    </html>
  )
}
  
