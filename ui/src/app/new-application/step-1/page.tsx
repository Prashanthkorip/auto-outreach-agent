"use client";
import { useRouter } from "next/navigation";
import { EmailContact, useApplicationStore } from "@/store/useApplicationStore";
import { useState, useEffect, useRef } from "react";
import { Briefcase, FileText, Mail, Upload, ArrowLeft, ArrowRight } from "lucide-react";

export default function Step1Page() {
  const router = useRouter();
  const {
    jobUrl, setJobUrl,
    jobDescription, setJobDescription,
    resumeFile, setResumeFile,
    resumeText, setResumeText,
    emailInput, setEmailInput,
    nameInput, setNameInput,
    emailList, setEmailList,
    generatedSubject, setGeneratedSubject,
    generatedTemplate, setGeneratedTemplate
  } = useApplicationStore();

  const isComplete = jobDescription.trim().length > 0 && resumeText.trim().length > 0;

  const [activeTab, setActiveTab] = useState<'resume' | 'template'>('resume');
  const [isScraping, setIsScraping] = useState(false);
  const [isGeneratingEmail, setIsGeneratingEmail] = useState(false);

  const onCancel = () => {
    router.push("/");
  };
  const onNext = async () => {
    setIsGeneratingEmail(true);
    try {
      const resp = await fetch("http://localhost:8000/api/generate-email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ /* include necessary fields here, e.g. jobDescription, resumeText, etc. */ })
      });
      const data = await resp.json();
      if (data.subject && data.content) {
        // If you have a subject field in your store, set it here
        // setSubject(data.subject);
        setGeneratedTemplate(data.content);
        setGeneratedSubject(data.subject);
        router.push("/new-application/step-2");
      } else {
        alert("Failed to generate email. Please try again.");
      }
    } catch (e) {
      alert("Error generating email template.");
    } finally {
      setIsGeneratingEmail(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setResumeFile(file);
      if (file.type === "application/pdf") {
        setIsScraping(true);
        setResumeText("Extracting resume text from PDF...");
        try {
          const formData = new FormData();
          formData.append("file", file);
          const resp = await fetch("http://localhost:8000/api/upload-resume", {
            method: "POST",
            body: formData
          });
          const data = await resp.json();
          setResumeText(data.description || "");
        } catch (e) {
          setResumeText("Failed to extract resume text. Please paste it manually.");
        } finally {
          setIsScraping(false);
        }
      } else {
        setResumeText(`File uploaded: ${file.name}\n\nYou can edit or paste your resume content here...`);
      }
    }
  };

  const handleJobUrlScrape = async () => {
    if (!jobUrl.trim()) return;
    setIsScraping(true);
    setJobDescription("Loading job description...\n\nYou can edit or paste the job description here...");
    try {
      console.log("Scraping job description for URL: ", jobUrl);
      const resp = await fetch("http://localhost:8000/api/scrape-job", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: jobUrl })
      });
      console.log("Scraped job description for URL: ", jobUrl);

      const data = await resp.json();
      setJobDescription(data.description || "");
    } catch (e) {
      setJobDescription(`Failed to fetch job description. Please paste it manually. ${e}`);
    } finally {
      setIsScraping(false);
    }
  };

  // Derive name from email address
  const deriveNameFromEmail = (email: string): string => {
    const localPart = email.split('@')[0];
    // Remove common separators and numbers
    const cleanedName = localPart
      .replace(/[._-]/g, ' ')
      .replace(/\d+/g, '')
      .trim();

    // Capitalize each word
    return cleanedName
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  };

  // Generate initials from name
  const generateInitials = (name: string): string => {
    return name
      .split(' ')
      .map(word => word.charAt(0).toUpperCase())
      .slice(0, 2)
      .join('');
  };

  // Add email to list
  const addEmailToList = () => {
    if (!emailInput.trim()) return;

    // Split input by comma, space, or new line
    const emails = emailInput
      .split(/[,\s\n]+/)
      .map((e: string) => e.trim().toLowerCase())
      .filter(Boolean);

    let added = false;
    const newContacts = [...emailList];

    emails.forEach((email: string) => {
      // Basic email validation
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return;
      if (newContacts.some(contact => contact.email === email)) return;
      const derivedName = nameInput.trim() || deriveNameFromEmail(email);
      const newContact: EmailContact = {
        id: Date.now().toString() + Math.random().toString(36).slice(2),
        email,
        name: derivedName,
      };
      newContacts.push(newContact);
      added = true;
    });

    if (!added) {
      alert('No new valid emails to add.');
    } else {
      setEmailList(newContacts);
      setEmailInput('');
      setNameInput('');
    }
  };

  // Remove email from list
  const removeEmailFromList = (id: string) => {
    setEmailList(emailList.filter(contact => contact.id !== id));
  };

  // Handle email input key press
  const handleEmailKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addEmailToList();
    }
  };

  // Debounce helpers
  function useDebouncedEffect(effect: () => void, deps: any[], delay: number) {
    const callback = useRef<ReturnType<typeof setTimeout> | null>(null);
    useEffect(() => {
      if (callback.current) clearTimeout(callback.current);
      callback.current = setTimeout(effect, delay);
      return () => {
        if (callback.current) clearTimeout(callback.current);
      };
    }, deps);
  }

  // Job Description sync
  useDebouncedEffect(() => {
    if (jobDescription.trim()) {
      fetch("http://localhost:8000/api/save-job-description", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description: jobDescription })
      });
    }
  }, [jobDescription], 1000);

  // Job Description sync
  useDebouncedEffect(() => {
    if (jobUrl.trim()) {
      fetch("http://localhost:8000/api/save-job-url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: jobUrl })
      });
    }
  }, [jobUrl], 1000);

  // Resume Content sync
  useDebouncedEffect(() => {
    if (resumeText.trim()) {
      fetch("http://localhost:8000/api/save-resume-description", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description: resumeText })
      });
    }
  }, [resumeText], 1000);

  // Email Template sync
  useDebouncedEffect(() => {
    if (generatedTemplate.trim()) {
      fetch("http://localhost:8000/api/save-email-template", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description: generatedTemplate })
      });
    }
  }, [generatedTemplate], 1000);

  useDebouncedEffect(() => {
    if (emailList) {
      fetch("http://localhost:8000/api/save-recipients", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ recipients: emailList })
      });
    }
  }, [emailList], 1000);

  useEffect(() => {
    // Fetch all initial data in parallel
    Promise.all([
      fetch("http://localhost:8000/api/get-job-url").then(res => res.json()),
      fetch("http://localhost:8000/api/get-job-description").then(res => res.json()),
      fetch("http://localhost:8000/api/get-resume-description").then(res => res.json()),
      fetch("http://localhost:8000/api/get-email-template").then(res => res.json()),
      fetch("http://localhost:8000/api/get-recipients").then(res => res.json()),
    ]).then(([jobUrl, jobDesc, resumeDesc, emailTemplate, recipients]) => {
      setJobUrl(jobUrl.url || "");
      setJobDescription(jobDesc.description || "");
      setResumeText(resumeDesc.description || "");
      setGeneratedTemplate(emailTemplate.description || "");
      setEmailList(recipients.recipients || []);
    });
  }, []);

  return (
    <div className="w-full max-h-[calc(100vh-64px)] h-screen flex-shrink-0 flex flex-col">
      <div className="flex-1 flex flex-col p-6">
        <div className="w-full flex flex-col h-full">
          <div className="flex gap-8 h-full">
            {/* Left Panel - Job Information */}
            <div className="flex flex-col card p-6 w-7/12">
              {/* Job URL Input */}
              <h3 className="text-lg font-medium text-card-foreground mb-3 flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-primary" />
                Job Information
              </h3>

              {/* Job URL */}
              <div className="flex gap-2 items-end mb-2">
                <input
                  type="url"
                  value={jobUrl}
                  onChange={(e) => setJobUrl(e.target.value)}
                  placeholder="https://company.com/careers/job-title"
                  className="input"
                />
                <button
                  type="button"
                  onClick={handleJobUrlScrape}
                  disabled={isScraping || !jobUrl.trim()}
                  className={`btn font-medium transition-colors ${isScraping || !jobUrl.trim() 
                    ? 'bg-muted text-muted-foreground cursor-not-allowed' 
                    : 'btn-primary'}`}
                >
                  {isScraping ? 'Fetching...' : 'Fetch'}
                </button>
              </div>

              {/* Job Description */}
              <label className="block text-sm font-medium text-muted-foreground mb-2 mt-3">
                Job Description
              </label>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste the job description here..."
                className="textarea flex-1"
                disabled={isScraping}
              />
              {isScraping && (
                <div className="text-primary text-sm mt-2">Scraping job description...</div>
              )}
            </div>

            {/* Right Panel - Tabbed Interface */}
            <div className="flex flex-col w-5/12">
              <div className="card flex flex-col h-full">
                {/* Tab Header */}
                <div className="flex border-b border-border">
                  <button
                    onClick={() => setActiveTab('resume')}
                    className={`flex-1 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'resume'
                      ? 'border-primary text-primary bg-accent'
                      : 'border-transparent text-muted-foreground hover:text-foreground hover:bg-muted'
                      }`}
                  >
                    <FileText className="w-4 h-4 mr-2 inline" />
                    Resume Information
                  </button>
                  <button
                    onClick={() => setActiveTab('template')}
                    className={`flex-1 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'template'
                      ? 'border-primary text-primary bg-accent'
                      : 'border-transparent text-muted-foreground hover:text-foreground hover:bg-muted'
                      }`}
                  >
                    <Mail className="w-4 h-4 mr-2 inline" />
                    Email Template
                  </button>
                </div>

                {/* Tab Content */}
                <div className="flex-1 p-6 flex flex-col">
                  {activeTab === 'resume' ? (
                    // Resume Tab Content
                    <>
                      {/* File Upload */}
                      <input
                        type="file"
                        accept=".pdf,.doc,.docx,.txt"
                        onChange={handleFileUpload}
                        className="hidden"
                        id="resume-upload"
                      />
                      <label
                        htmlFor="resume-upload"
                        className="w-full px-4 py-3 border-2 border-dashed border-border rounded-lg hover:border-primary transition-colors flex items-center justify-center gap-2 text-muted-foreground hover:text-primary mb-4 cursor-pointer"
                      >
                        <Upload className="w-5 h-5" />
                        {resumeFile ? resumeFile.name : 'Click to upload resume'}
                      </label>

                      {/* Resume Text */}
                      <label className="block text-sm font-medium text-muted-foreground mb-2">
                        Resume Content
                      </label>
                      <textarea
                        value={resumeText}
                        onChange={(e) => setResumeText(e.target.value)}
                        placeholder="Paste your resume content here or upload a file..."
                        className="textarea flex-1"
                      />
                    </>
                  ) : (
                    // Email Template Tab Content
                    <>
                      <label className="block text-sm font-medium text-muted-foreground mb-2">
                        Email Template
                      </label>
                      <textarea
                        value={generatedTemplate}
                        onChange={(e) => setGeneratedTemplate(e.target.value)}
                        placeholder="Your personalized email template will appear here. You can edit it manually or let AI generate it based on the job description and resume..."
                        className="textarea flex-1"
                      />
                    </>
                  )}
                </div>
              </div>

              {/* Email Recipients Input */}
              <div className="mt-6">
                <div className="flex justify-between items-center mb-2">
                  <label className="block text-sm font-medium text-muted-foreground">
                    Recipients
                  </label>
                  <div className="text-sm text-muted-foreground">
                    {emailList.length} recipient{emailList.length !== 1 ? 's' : ''} selected
                  </div>
                </div>
                <div className="border border-border rounded-md p-3 bg-card min-h-[60px]">
                  <div className="flex flex-wrap gap-2 items-center max-h-[300px] overflow-auto">
                    {/* Email Chips */}
                    {emailList.map((contact) => (
                      <div
                        key={contact.id}
                        className="flex items-center gap-2 bg-accent text-accent-foreground px-3 py-1 rounded-full text-sm flex-shrink-0 border border-border"
                      >
                        {/* Avatar */}
                        <div className="w-6 h-6 bg-primary rounded-full flex items-center justify-center text-primary-foreground text-xs font-medium flex-shrink-0">
                          {generateInitials(contact.name)}
                        </div>
                        <span className="whitespace-nowrap">{contact.email}</span>
                        <button
                          onClick={() => removeEmailFromList(contact.id)}
                          className="text-primary hover:text-destructive transition-colors flex-shrink-0"
                        >
                          &times;
                        </button>
                      </div>
                    ))}
                    {/* Input Field */}
                    <input
                      type="text"
                      value={emailInput}
                      onChange={(e) => setEmailInput(e.target.value)}
                      onKeyPress={handleEmailKeyPress}
                      placeholder={emailList.length === 0 ? "Enter email addresses..." : "Add another email..."}
                      className="flex-1 min-w-[200px] outline-none bg-transparent text-foreground placeholder-muted-foreground py-1"
                    />
                  </div>
                </div>
              </div>

            </div>
          </div>

          {/* Continue Button */}
          <div className="mt-4 flex justify-between">
            <button
              onClick={onCancel}
              className="btn btn-secondary"
            >
              <ArrowLeft className="w-6 h-6 mr-2 inline mb-0.5" />
              Cancel
            </button>
            <button
              onClick={onNext}
              disabled={!isComplete || isGeneratingEmail}
              className={`btn font-semibold ${isComplete && !isGeneratingEmail
                ? 'btn-primary'
                : 'bg-muted text-muted-foreground cursor-not-allowed border-border'
              }`}
            >
              {isGeneratingEmail ? 'Generating...' : 'Generate Email Template'}
              <ArrowRight className="w-6 h-6 ml-2 inline mb-0.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
} 