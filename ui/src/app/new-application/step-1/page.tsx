"use client";
import { useRouter } from "next/navigation";
import { EmailContact, useApplicationStore } from "@/store/useApplicationStore";
import { useState } from "react";
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
    generatedTemplate, setGeneratedTemplate
  } = useApplicationStore();

  const isComplete = jobDescription.trim().length > 0 && resumeText.trim().length > 0;

  const [activeTab, setActiveTab] = useState<'resume' | 'template'>('resume');

  const onCancel = () => {
    router.push("/");
  };
  const onNext = () => {
    router.push("/new-application/step-2");
  };


    const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            setResumeFile(file);
            // Here you would typically extract text from the file
            // For now, we'll just show the filename
            setResumeText(`File uploaded: ${file.name}\n\nYou can edit or paste your resume content here...`);
        }
    };

    const handleJobUrlChange = async (url: string) => {
        setJobUrl(url);
        // Here you would typically fetch job description from the URL
        // For now, we'll simulate it
        if (url.trim()) {
            setJobDescription("Loading job description...\n\nYou can edit or paste the job description here...");
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

        const email = emailInput.trim().toLowerCase();
        // Check if email already exists
        if (emailList.some(contact => contact.email === email)) {
            alert('Email already added to the list');
            return;
        }

        const derivedName = nameInput.trim() || deriveNameFromEmail(email);
        const newContact: EmailContact = {
            id: Date.now().toString(),
            email,
            name: derivedName,
            initials: generateInitials(derivedName)
        };

        setEmailList([...emailList, newContact]);
        setEmailInput('');
        setNameInput('');
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

    return (
        <div className="w-full max-h-[calc(100vh-64px)] h-screen flex-shrink-0 flex flex-col">
            <div className="flex-1 flex flex-col p-6">
                <div className="w-full flex flex-col h-full">
                    <div className="flex gap-8 h-full">
                        {/* Left Panel - Job Information */}
                        <div className="flex flex-col bg-white rounded-lg border border-gray-200 p-6 w-7/12">
                            {/* Job URL Input */}
                            <h3 className="text-lg font-medium text-gray-900 mb-3 flex items-center gap-2">
                                <Briefcase className="w-5 h-5 text-blue-600" />
                                Job Information
                            </h3>

                            {/* Job URL */}
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Job URL
                            </label>
                            <input
                                type="url"
                                value={jobUrl}
                                onChange={(e) => setJobUrl(e.target.value)}
                                placeholder="https://company.com/careers/job-title"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />

                            {/* Job Description */}
                            <label className="block text-sm font-medium text-gray-700 mb-2 mt-3">
                                Job Description
                            </label>
                            <textarea
                                value={jobDescription}
                                onChange={(e) => setJobDescription(e.target.value)}
                                placeholder="Paste the job description here..."
                                className="flex-1 px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                            />
                        </div>

                        {/* Right Panel - Tabbed Interface */}
                        <div className="flex flex-col w-5/12">
                            <div className="bg-white rounded-lg border border-gray-200 flex flex-col h-full">
                                {/* Tab Header */}
                                <div className="flex border-b border-gray-200">
                                    <button
                                        onClick={() => setActiveTab('resume')}
                                        className={`flex-1 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'resume'
                                                ? 'border-blue-600 text-blue-600 bg-blue-50'
                                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                                            }`}
                                    >
                                        <FileText className="w-4 h-4 mr-2 inline" />
                                        Resume Information
                                    </button>
                                    <button
                                        onClick={() => setActiveTab('template')}
                                        className={`flex-1 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'template'
                                                ? 'border-blue-600 text-blue-600 bg-blue-50'
                                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
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
                                                className="w-full px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-400 transition-colors flex items-center justify-center gap-2 text-gray-600 hover:text-blue-600 mb-4"
                                            >
                                                <Upload className="w-5 h-5" />
                                                {resumeFile ? resumeFile.name : 'Click to upload resume'}
                                            </label>

                                            {/* Resume Text */}
                                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                                Resume Content
                                            </label>
                                            <textarea
                                                value={resumeText}
                                                onChange={(e) => setResumeText(e.target.value)}
                                                placeholder="Paste your resume content here or upload a file..."
                                                className="flex-1 px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                                            />
                                        </>
                                    ) : (
                                        // Email Template Tab Content
                                        <>
                                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                                Email Template
                                            </label>
                                            <textarea
                                                value={generatedTemplate}
                                                onChange={(e) => setGeneratedTemplate(e.target.value)}
                                                placeholder="Your personalized email template will appear here. You can edit it manually or let AI generate it based on the job description and resume..."
                                                className="flex-1 px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                                            />
                                            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
                                                <p className="text-sm text-blue-800">
                                                    <strong>Tip:</strong> The email template supports Markdown formatting. Use **bold**, *italic*, and bullet points to make your email stand out.
                                                </p>
                                            </div>
                                        </>
                                    )}
                                </div>
                            </div>

                            {/* Email Recipients Input */}
                            <div className="mt-6">
                                <div className="flex justify-between items-center mb-2">
                                    <label className="block text-sm font-medium text-gray-700 ">
                                        Recipients
                                    </label>
                                    <div className="text-sm text-gray-500">
                                        {emailList.length} recipient{emailList.length !== 1 ? 's' : ''} selected
                                    </div>
                                </div>
                                <div className="border border-gray-300 rounded-md p-3 bg-white min-h-[60px]">
                                    <div className="flex flex-wrap gap-2 items-center  max-h-[300px] overflow-auto">
                                        {/* Email Chips */}
                                        {emailList.map((contact) => (
                                            <div
                                                key={contact.id}
                                                className="flex items-center gap-2 bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm flex-shrink-0"
                                            >
                                                {/* Avatar */}
                                                <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-white text-xs font-medium flex-shrink-0">
                                                    {contact.initials}
                                                </div>
                                                <span className="whitespace-nowrap">{contact.email}</span>
                                                <button
                                                    onClick={() => removeEmailFromList(contact.id)}
                                                    className="text-blue-600 hover:text-red-500 transition-colors flex-shrink-0"
                                                >
                                                    &times;
                                                </button>
                                            </div>
                                        ))}
                                        {/* Input Field */}
                                        <input
                                            type="email"
                                            value={emailInput}
                                            onChange={(e) => setEmailInput(e.target.value)}
                                            onKeyPress={handleEmailKeyPress}
                                            placeholder={emailList.length === 0 ? "Enter email addresses..." : "Add another email..."}
                                            className="flex-1 min-w-[200px] outline-none bg-transparent text-gray-900 placeholder-gray-500 py-1"
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
                            className={`px-6 py-3 font-semibold rounded-lg transition-colors bg-gray-100 text-gray-900 border border-gray-200`}
                        >
                            <ArrowLeft className="w-6 h-6 mr-2 inline mb-0.5" />
                            Cancel
                        </button>
                        <button
                            onClick={onNext}
                            disabled={!isComplete}
                            className={`px-6 py-3 font-semibold rounded-lg transition-colors ${isComplete
                                ? 'bg-blue-600 hover:bg-blue-700 text-white'
                                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                }`}
                        >
                            Generate Email Template
                            <ArrowRight className="w-6 h-6 ml-2 inline mb-0.5" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
} 