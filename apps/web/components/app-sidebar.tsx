"use client";

import * as React from "react";

import { NavUser } from "@/components/nav-user";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";
import { useMe } from "@/hooks/use-me";
import Link from "next/link";
import { FolderKanban, Plus } from "lucide-react";
import { usePathname } from "next/navigation";

type NavMainProps = {
  onCreateProjectClick: () => void;
};

function NavMain({ onCreateProjectClick }: NavMainProps) {
  const pathname = usePathname();
  const { setOpenMobile } = useSidebar();

  function closeMobileSidebar() {
    setOpenMobile(false);
  }

  function onCreateProjectButtonClick() {
    closeMobileSidebar();
    onCreateProjectClick();
  }

  return (
    <SidebarGroup>
      <SidebarGroupContent className="flex flex-col gap-2">
        <SidebarMenu>
          <SidebarMenuItem className="flex items-center gap-2">
            <SidebarMenuButton
              tooltip="Create project"
              className="min-w-8 bg-primary text-primary-foreground duration-200 ease-linear hover:bg-primary/90 hover:text-primary-foreground active:bg-primary/90 active:text-primary-foreground"
              onClick={onCreateProjectButtonClick}
            >
              <Plus />
              <span>Create project</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              asChild
              tooltip="Projects"
              isActive={pathname.startsWith("/projects")}
            >
              <Link href="/projects" onClick={closeMobileSidebar}>
                <FolderKanban />
                <span>Projects</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  );
}

type AppSidebarProps = React.ComponentProps<typeof Sidebar> & {
  onCreateProjectClick: () => void;
};

export function AppSidebar({
  onCreateProjectClick,
  ...props
}: AppSidebarProps) {
  const { data } = useMe();

  return (
    <Sidebar collapsible="offcanvas" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              asChild
              className="data-[slot=sidebar-menu-button]:p-1.5!"
            >
              {/* <a href="#"> */}
              <Link href="/">
                <span className="text-base font-semibold">RPAP</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <NavMain onCreateProjectClick={onCreateProjectClick} />
      </SidebarContent>
      <SidebarFooter>{data && <NavUser user={data} />}</SidebarFooter>
    </Sidebar>
  );
}
