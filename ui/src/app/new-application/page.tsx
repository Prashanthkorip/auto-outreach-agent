import { redirect } from "next/navigation";

export default function NewApplicationRoot() {
  redirect("/new-application/step-1");
  return null;
} 