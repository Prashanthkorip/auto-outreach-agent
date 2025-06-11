"use client";
import { useRouter } from "next/navigation";
import { useApplicationStore } from "@/store/useApplicationStore";

export default function Step3Page() {
  const router = useRouter();
  const { emailStats } = useApplicationStore();
  const onComplete = () => {
    router.push("/");
  };
  return (
    <div className="w-full h-screen flex-shrink-0 p-6">
      <div className="max-w-4xl mx-auto p-6">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-foreground mb-4">
            Application Complete!
          </h2>
          <p className="text-muted-foreground mb-6">
            Your outreach emails have been successfully sent to all recipients.
          </p>
          {emailStats && (
            <div className="mb-6">
              <div className="flex justify-center gap-8 text-lg">
                <div><span className="font-bold text-foreground">Sent:</span> <span className="text-foreground">{emailStats.sent}</span></div>
                <div><span className="font-bold text-green-600 dark:text-green-400">Successful:</span> <span className="text-green-600 dark:text-green-400">{emailStats.successful}</span></div>
                <div><span className="font-bold text-destructive">Failed:</span> <span className="text-destructive">{emailStats.failed}</span></div>
              </div>
            </div>
          )}
          
          <button
            onClick={onComplete}
            className="btn btn-primary"
          >
            View Application Dashboard
          </button>
        </div>
      </div>
    </div>
  );
} 