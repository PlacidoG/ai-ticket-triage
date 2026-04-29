
"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Ticket,
  PlusCircle,
  BrainCircuit,
  ChevronLeft,
  ChevronRight,
  Bot,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/theme-toggle";
import { Separator } from "@/components/ui/separator";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const navItems = [
  {
    title: "Dashboard",
    href: "/",
    icon: LayoutDashboard,
    section: "Overview",
  },
  {
    title: "Tickets",
    href: "/tickets",
    icon: Ticket,
    section: "Overview",
  },
  {
    title: "Submit Ticket",
    href: "/submit",
    icon: PlusCircle,
    section: "Actions",
  },
  {
    title: "AI Performance",
    href: "/ai-performance",
    icon: BrainCircuit,
    section: "Analytics",
  },
];

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();

  // Group nav items by section
  const sections = navItems.reduce(
    (acc, item) => {
      if (!acc[item.section]) acc[item.section] = [];
      acc[item.section].push(item);
      return acc;
    },
    {} as Record<string, typeof navItems>
  );

  return (
    <TooltipProvider delayDuration={0}>
      <aside
        className={cn(
          "flex flex-col border-r bg-card transition-all duration-300",
          collapsed ? "w-16" : "w-64"
        )}
      >
        {/* Header */}
        <div className="flex h-14 items-center border-b px-3">
          {!collapsed && (
            <div className="flex items-center gap-2 px-1">
              <Bot className="h-6 w-6 text-primary" />
              <span className="text-sm font-semibold">AI Triage</span>
            </div>
          )}
          {collapsed && (
            <div className="flex w-full justify-center">
              <Bot className="h-6 w-6 text-primary" />
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-2">
          {Object.entries(sections).map(([section, items]) => (
            <div key={section} className="mb-4">
              {!collapsed && (
                <p className="mb-1 px-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  {section}
                </p>
              )}
              {items.map((item) => {
                const isActive = pathname === item.href;
                const linkContent = (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                      isActive
                        ? "bg-primary text-primary-foreground"
                        : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
                      collapsed && "justify-center px-2"
                    )}
                  >
                    <item.icon className="h-4 w-4 shrink-0" />
                    {!collapsed && <span>{item.title}</span>}
                  </Link>
                );

                if (collapsed) {
                  return (
                    <Tooltip key={item.href}>
                      <TooltipTrigger asChild>{linkContent}</TooltipTrigger>
                      <TooltipContent side="right">
                        {item.title}
                      </TooltipContent>
                    </Tooltip>
                  );
                }

                return linkContent;
              })}
            </div>
          ))}
        </nav>

        {/* Footer */}
        <div className="border-t p-2">
          <div
            className={cn(
              "flex items-center",
              collapsed ? "justify-center" : "justify-between px-1"
            )}
          >
            {!collapsed && <ThemeToggle />}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setCollapsed(!collapsed)}
              className="h-8 w-8"
            >
              {collapsed ? (
                <ChevronRight className="h-4 w-4" />
              ) : (
                <ChevronLeft className="h-4 w-4" />
              )}
            </Button>
            {collapsed && <ThemeToggle />}
          </div>
        </div>
      </aside>
    </TooltipProvider>
  );
}