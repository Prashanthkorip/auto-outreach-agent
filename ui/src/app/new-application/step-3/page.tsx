"use client";
import { useRouter } from "next/navigation";
import { useApplicationStore } from "@/store/useApplicationStore";

export default function Step3Page() {
  const router = useRouter();
  const onComplete = () => {
    router.push("/");
  };
  return (
    <div className="w-full h-screen flex-shrink-0 p-6">
      <div className="max-w-4xl mx-auto p-6">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Application Complete!
          </h2>
          <p className="text-gray-600 mb-6">
            Your outreach emails have been successfully sent to all recipients.
          </p>
          
          <button
            onClick={onComplete}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            View Application Dashboard
          </button>
        </div>
      </div>
    </div>
  );
} 