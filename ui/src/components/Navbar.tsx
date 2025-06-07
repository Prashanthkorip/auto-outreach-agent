"use client";

import { useState } from "react";
import { Mail, Key, User, X } from "lucide-react";
import * as Popover from "@radix-ui/react-popover";
import { usePathname } from "next/navigation";
import { useRouter } from "next/navigation";

const stepTitles: Record<string, { title: string }> = {
  "/new-application/step-1": {
    title: "Step 1: Job & Resume Information",
  },
  "/new-application/step-2": {
    title: "Step 2: Email Composition",
  },
  "/new-application/step-3": {
    title: "Step 3: Review & Send",
  }
};

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const stepInfo = stepTitles[pathname] || null;
  const [openaiPopoverOpen, setOpenaiPopoverOpen] = useState(false);
  const [credentialsPopoverOpen, setCredentialsPopoverOpen] = useState(false);
  const [openaiKey, setOpenaiKey] = useState("");
  const [credentials, setCredentials] = useState("");

  const handleSaveOpenaiKey = () => {
    localStorage.setItem("openaiKey", openaiKey);
    setOpenaiPopoverOpen(false);
  };
  const handleSaveCredentials = () => {
    localStorage.setItem("credentials", credentials);
    setCredentialsPopoverOpen(false);
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 h-16 flex items-center justify-center shadow-none">
      <div className="flex items-center justify-center w-full h-full relative">
        {/* Left: Logo */}
        <div className="absolute left-6 flex items-center gap-2" onClick={() => router.push("/")}>
          <Mail className="w-6 h-6 text-blue-600" />
          <span className="text-xl font-bold text-gray-900">AIRA</span>
        </div>
        {/* Center: Step Title/Subtitle */}
        {stepInfo && (
          <div className="flex flex-col items-center">
            <span className="text-lg font-semibold text-gray-900">{stepInfo.title}</span>
          </div>
        )}
        {/* Right: OpenAI Key & Credentials */}
        <div className="absolute right-6 flex items-center gap-3">
          {/* OpenAI Key Popover */}
          <Popover.Root open={openaiPopoverOpen} onOpenChange={setOpenaiPopoverOpen}>
            <Popover.Trigger asChild>
              <button className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
                <Key className="w-4 h-4" />
                OpenAI Key
              </button>
            </Popover.Trigger>
            <Popover.Portal>
              <Popover.Content
                className="bg-white rounded-lg shadow-lg border border-gray-200 p-4 w-[480px] z-50"
                sideOffset={8}
              >
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-semibold text-gray-900">
                    OpenAI API Key
                  </h3>
                  <Popover.Close asChild>
                    <button className="text-gray-400 hover:text-gray-600">
                      <X className="w-4 h-4" />
                    </button>
                  </Popover.Close>
                </div>
                <div className="space-y-3">
                  <textarea
                    placeholder="sk-..."
                    value={openaiKey}
                    onChange={(e) => setOpenaiKey(e.target.value)}
                    className="w-full h-20 px-3 py-2 text-base font-mono font-semibold bg-gray-50 text-black border border-gray-200 rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <div className="flex justify-end">
                    <Popover.Close asChild>
                      <button
                        onClick={handleSaveOpenaiKey}
                        className="px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md  border border-gray-200 transition-colors"
                      >
                        Save
                      </button>
                    </Popover.Close>
                  </div>
                </div>
              </Popover.Content>
            </Popover.Portal>
          </Popover.Root>
          {/* Credentials Popover */}
          <Popover.Root open={credentialsPopoverOpen} onOpenChange={setCredentialsPopoverOpen}>
            <Popover.Trigger asChild>
              <button className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
                <Mail className="w-4 h-4" />
                credentials.json
              </button>
            </Popover.Trigger>
            <Popover.Portal>
              <Popover.Content
                className="bg-white rounded-lg shadow-lg border border-gray-200 p-4 w-[640px] z-50"
                sideOffset={8}
              >
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-semibold text-gray-900">
                    credentials.json
                  </h3>
                  <Popover.Close asChild>
                    <button className="text-gray-400 hover:text-gray-600">
                      <X className="w-4 h-4" />
                    </button>
                  </Popover.Close>
                </div>
                <div className="space-y-3">
                  <textarea
                    placeholder='{"email": "your@email.com", "password": "your-app-password"}'
                    value={credentials}
                    onChange={(e) => setCredentials(e.target.value)}
                    className="w-full h-84 px-3 py-2 text-base font-mono bg-gray-50 text-black border border-gray-200 rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <div className="flex justify-end">
                    <Popover.Close asChild>
                      <button
                        onClick={handleSaveCredentials}
                        className="px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100 border border-gray-200 rounded-md transition-colors"
                      >
                        Save
                      </button>
                    </Popover.Close>
                  </div>
                </div>
              </Popover.Content>
            </Popover.Portal>
          </Popover.Root>
        </div>
      </div>
    </nav>
  );
}