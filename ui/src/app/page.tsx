"use client";

import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-foreground mb-4">
          Welcome to AIRA
        </h1>
        <p className="text-xl text-muted-foreground mb-8">
          Your AI Reachout Assistant to mail your resume and job application to recruiters and hiring managers.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8 mb-12">
        <div className="card p-6">
          <h2 className="text-xl font-semibold text-card-foreground mb-3">
            🚀 Start New Application
          </h2>
          <p className="text-muted-foreground mb-4">
            Create personalized outreach emails for job applications using AI. Upload your resume and job description to get started.
          </p>
          <Link
            href="/new-application"
            className="btn btn-primary inline-block"
          >
            Create Application
          </Link>
        </div>

        <div className="card p-6">
          <h2 className="text-xl font-semibold text-card-foreground mb-3">
            📊 View Past Applications
          </h2>
          <p className="text-muted-foreground mb-4">
            Review your previous outreach campaigns, track responses, and analyze performance metrics.
          </p>
          <Link
            href="/past-applications"
            className="btn btn-secondary inline-block"
          >
            View History
          </Link>
        </div>
      </div>

      <div className="alert alert-warning">
        <h3 className="text-sm font-semibold mb-2">
          🔧 Setup Required
        </h3>
        <p className="text-sm">
          Please configure your OpenAI API key and email credentials in the navigation bar before creating your first application.
        </p>
      </div>
    </div>
  );
}
