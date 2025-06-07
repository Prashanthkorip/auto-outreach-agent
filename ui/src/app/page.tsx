"use client";

import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to AIRA
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Your AI Reachout Assistant to mail your resume and job application to recruiters and hiring managers.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8 mb-12">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-3">
            🚀 Start New Application
          </h2>
          <p className="text-gray-600 mb-4">
            Create personalized outreach emails for job applications using AI. Upload your resume and job description to get started.
          </p>
          <Link
            href="/new-application"
            className="inline-block px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            Create Application
          </Link>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-3">
            📊 View Past Applications
          </h2>
          <p className="text-gray-600 mb-4">
            Review your previous outreach campaigns, track responses, and analyze performance metrics.
          </p>
          <Link
            href="/past-applications"
            className="inline-block px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white font-medium rounded-lg transition-colors"
          >
            View History
          </Link>
        </div>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-yellow-800 mb-2">
          🔧 Setup Required
        </h3>
        <p className="text-sm text-yellow-700">
          Please configure your OpenAI API key and email credentials in the navigation bar before creating your first application.
        </p>
      </div>
    </div>
  );
}
