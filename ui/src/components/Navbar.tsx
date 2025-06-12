"use client";

import React, { useState, useEffect } from "react";
import { Brain, Mail, Key, User, X, Sun, Moon, Laptop } from "lucide-react";
import * as Popover from "@radix-ui/react-popover";
import { usePathname } from "next/navigation";
import { useRouter } from "next/navigation";
import { useApplicationStore } from "@/store/useApplicationStore";
import { useTheme } from 'next-themes';

const stepTitles: Record<string, { title: string }> = {
	"/new-application/step-1": {
		title: "Step 1: Job & Resume Information",
	},
	"/new-application/step-2": {
		title: "Step 2: Email Composition",
	},
	"/new-application/step-3": {
		title: "Step 3: Review & Send",
	},
};

export default function Navbar() {
	const router = useRouter();
	const pathname = usePathname();
	const stepInfo = stepTitles[pathname] || null;
	const [openaiPopoverOpen, setOpenaiPopoverOpen] = useState(false);
	const [credentialsPopoverOpen, setCredentialsPopoverOpen] = useState(false);
	const { openaiKey, setOpenaiKey, credentials, setCredentials } =
		useApplicationStore();
	const { theme, setTheme, resolvedTheme } = useTheme();
	const [mounted, setMounted] = useState(false);
	useEffect(() => { setMounted(true); }, []);

	// Fetch OpenAI Key on popover open
	useEffect(() => {
		if (openaiPopoverOpen) {
			fetch("http://localhost:8000/api/get-openai-key")
				.then((res) => res.json())
				.then((data) => setOpenaiKey(data.OPENAI_API_KEY || ""));
		}
	}, [openaiPopoverOpen, setOpenaiKey]);

	// Fetch credentials on popover open
	useEffect(() => {
		if (credentialsPopoverOpen) {
			fetch("http://localhost:8000/api/get-credentials")
				.then((res) => res.json())
				.then((data) =>
					setCredentials(
						JSON.stringify(data.credentials, null, 2) || ""
					)
				);
		}
	}, [credentialsPopoverOpen, setCredentials]);

	// Store original values for change detection
	const [originalOpenaiKey, setOriginalOpenaiKey] = useState("");
	const [originalCredentials, setOriginalCredentials] = useState("");

	// useEffect(() => {
	//   if (openaiPopoverOpen) setOriginalOpenaiKey(openaiKey);
	// }, [openaiPopoverOpen, openaiKey]);
	// useEffect(() => {
	//   if (credentialsPopoverOpen) setOriginalCredentials(credentials);
	// }, [credentialsPopoverOpen, credentials]);

	const handleSaveOpenaiKey = async () => {
		if (openaiKey !== originalOpenaiKey) {
			if (
				!window.confirm(
					"You are about to change the OpenAI Key. Are you sure?"
				)
			)
				return;
			await fetch("http://localhost:8000/api/put-openai-key", {
				method: "PUT",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ OPENAI_API_KEY: openaiKey }),
			});
			setOriginalOpenaiKey(openaiKey);
		}
		setOpenaiPopoverOpen(false);
	};
	const handleSaveCredentials = async () => {
		console.log("Saving credentials", credentials, originalCredentials);
		if (credentials !== originalCredentials) {
			if (
				!window.confirm(
					"You are about to change credentials.json. Are you sure?"
				)
			)
				return;
			let parsed;
			try {
				parsed = JSON.parse(credentials);
			} catch {
				alert("Invalid JSON format for credentials.");
				return;
			}
			await fetch("http://localhost:8000/api/put-credentials", {
				method: "PUT",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ credentials: parsed }),
			});
			setOriginalCredentials(credentials);
		}
		setCredentialsPopoverOpen(false);
	};

	type ThemeType = 'light' | 'dark';
	const themeIcons: Record<ThemeType, React.ReactElement> = {
		light: <Sun className="w-4 h-4" />,
		dark: <Moon className="w-4 h-4" />,
	};
	const themeOrder: ThemeType[] = ['light', 'dark'];
	const currentTheme = (theme || 'dark') as ThemeType;
	const nextTheme = themeOrder[(themeOrder.indexOf(currentTheme) + 1) % themeOrder.length];

	return (
		<nav className="nav fixed top-0 left-0 right-0 z-50 h-16 flex items-center justify-center">
			<div className="flex items-center justify-center w-full h-full relative">
				{/* Left: Logo */}
				<div
					className="absolute left-6 flex items-center gap-2 cursor-pointer"
					onClick={() => router.push("/")}
				>
					<Brain className="w-6 h-6 text-primary" />
					<span className="text-xl font-bold text-foreground">
						AIRA
					</span>
				</div>
				{/* Center: Step Title/Subtitle */}
				{stepInfo && (
					<div className="flex flex-col items-center">
						<span className="text-lg font-semibold text-foreground">
							{stepInfo.title}
						</span>
					</div>
				)}
				{/* Right: OpenAI Key & Credentials */}
				<div className="absolute right-6 flex items-center gap-3">
					{/* OpenAI Key Popover */}
					<Popover.Root
						open={openaiPopoverOpen}
						onOpenChange={setOpenaiPopoverOpen}
					>
						<Popover.Trigger asChild>
							<button className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted rounded-lg transition-all">
								<Key className="w-4 h-4" />
								OpenAI Key
							</button>
						</Popover.Trigger>
						<Popover.Portal>
							<Popover.Content
								className="popover rounded-lg p-4 w-[480px] z-50"
								sideOffset={8}
							>
								<div className="flex items-center justify-between mb-3">
									<h3 className="text-sm font-semibold text-card-foreground">
										OpenAI API Key
									</h3>
									<Popover.Close asChild>
										<button className="text-muted-foreground hover:text-foreground transition-colors">
											<X className="w-4 h-4" />
										</button>
									</Popover.Close>
								</div>
								<div className="space-y-3">
									<textarea
										placeholder="sk-..."
										value={openaiKey}
										onChange={(e) =>
											setOpenaiKey(e.target.value)
										}
										className="textarea h-20 font-mono font-semibold"
									/>
									<div className="flex justify-end">
										<Popover.Close asChild>
											<button
												onClick={handleSaveOpenaiKey}
												className="btn btn-secondary"
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
					<Popover.Root
						open={credentialsPopoverOpen}
						onOpenChange={setCredentialsPopoverOpen}
					>
						<Popover.Trigger asChild>
							<button className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted rounded-lg transition-all">
								<Mail className="w-4 h-4" />
								credentials.json
							</button>
						</Popover.Trigger>
						<Popover.Portal>
							<Popover.Content
								className="popover rounded-lg p-4 w-[640px] z-50"
								sideOffset={8}
							>
								<div className="flex items-center justify-between mb-3">
									<h3 className="text-sm font-semibold text-card-foreground">
										credentials.json
									</h3>
									<Popover.Close asChild>
										<button className="text-muted-foreground hover:text-foreground transition-colors">
											<X className="w-4 h-4" />
										</button>
									</Popover.Close>
								</div>
								<div className="space-y-3">
									<textarea
										placeholder='{"email": "your@email.com", "password": "your-app-password"}'
										value={credentials}
										onChange={(e) =>
											setCredentials(e.target.value)
										}
										className="textarea h-84 font-mono font-semibold"
									/>
									<div className="flex justify-end">
										<Popover.Close asChild>
											<button
												onClick={handleSaveCredentials}
												className="btn btn-secondary"
											>
												Save
											</button>
										</Popover.Close>
									</div>
								</div>
							</Popover.Content>
						</Popover.Portal>
					</Popover.Root>
					{/* Single Theme Toggle Button */}
					{mounted && (
						<button
							type="button"
							className="p-2 rounded-lg bg-muted border border-border flex flex-row items-center gap-2 text-muted-foreground hover:text-foreground hover:bg-secondary transition-all"
							onClick={() => setTheme(nextTheme)}
							title={`Switch to ${nextTheme} mode`}
						>
							{themeIcons[currentTheme]} <span className="capitalize text-sm">{currentTheme}</span>
						</button>
					)}
				</div>
			</div>
		</nav>
	);
}
