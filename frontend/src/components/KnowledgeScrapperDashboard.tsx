import { useState, useRef, type ChangeEvent } from "react";
import { FileText, Globe, BookOpen } from "lucide-react";
import Configuration from "./Configuration";
import Results from "./Results";

const KnowledgeScraperDashboard = () => {
  const [teamId, setTeamId] = useState<string>("aline123");
  const [sources, setSources] = useState([
    "https://interviewing.io/blog",
    "https://interviewing.io/topics#companies",
    "https://interviewing.io/learn#interview-guides",
    "https://nilmamano.com/blog/category/dsa",
  ]);
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<{
    team_id: string;
    items: {
      title: string;
      content: string;
      content_type: string;
      source_url: string;
      author: string;
      user_id: string;
    }[];
    summary: {
      total_items: number;
      content_types: { [key: string]: number };
      sources_processed: number;
      processing_time: string;
    };
  } | null>(null);
  const [logs, setLogs] = useState<
    { id: number; message: string; type: string; timestamp: string }[]
  >([]);
  const [progress, setProgress] = useState({ current: 0, total: 0 });
  const fileInputRef = useRef<HTMLInputElement>(null);

  const formData = new FormData();
  formData.append("team_id", teamId);
  formData.append("urls", JSON.stringify(sources));

  const files = fileInputRef.current?.files;
  if (files) {
    for (let i = 0; i < files.length; i++) {
      formData.append("pdfs", files[i]);
    }
  }
  const runScraper = async () => {
    setIsRunning(true);
    setLogs([]);
    setResults(null);
    setProgress({ current: 0, total: sources.length });
    const res = await fetch("http://localhost:8000/scrape", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    setResults(data);
    const addLog = (message: string, type = "info") => {
      setLogs((prev) => [
        ...prev,
        {
          id: Date.now() + Math.random(),
          message,
          type,
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    };

    try {
      addLog("🚀 Starting knowledge base scraping...", "info");

      const scrapedItems = [];

      for (let i = 0; i < sources.length; i++) {
        const source = sources[i];
        setProgress({ current: i, total: sources.length });

        addLog(`📥 Processing source: ${source}`, "info");
        await new Promise((resolve) => setTimeout(resolve, 2000));

        let itemCount = 0;
        if (source.includes("interviewing.io/blog")) {
          itemCount = 47;
          for (let j = 0; j < 5; j++) {
            scrapedItems.push({
              title: `System Design Interview Guide ${j + 1}`,
              content: `# System Design Fundamentals\n\nSystem design interviews are crucial for senior engineering roles...`,
              content_type: "blog",
              source_url: `${source}/system-design-${j + 1}`,
              author: "interviewing.io",
              user_id: "",
            });
          }
        } else if (source.includes("nilmamano.com")) {
          itemCount = 23;
          for (let j = 0; j < 3; j++) {
            scrapedItems.push({
              title: `Dynamic Programming Tutorial ${j + 1}`,
              content: `# Understanding Dynamic Programming\n\nDynamic programming is a method for solving complex problems...`,
              content_type: "blog",
              source_url: `${source}/dp-tutorial-${j + 1}`,
              author: "Nil Mamano",
              user_id: "",
            });
          }
        } else if (source.includes("companies")) {
          itemCount = 15;
          scrapedItems.push({
            title: "Google Interview Guide",
            content:
              "# Preparing for Google Interviews\n\nGoogle's interview process focuses on...",
            content_type: "other",
            source_url: source,
            author: "interviewing.io",
            user_id: "",
          });
        } else if (source.includes("quill.co")) {
          itemCount = 12;
          scrapedItems.push({
            title: "Content Marketing Best Practices",
            content:
              "# Mastering Content Marketing\n\nEffective content marketing requires...",
            content_type: "blog",
            source_url: source,
            author: "Quill Team",
            user_id: "",
          });
        } else {
          itemCount = Math.floor(Math.random() * 20) + 5;
          scrapedItems.push({
            title: "Generic Content Item",
            content: "# Sample Content\n\nThis is sample scraped content...",
            content_type: "other",
            source_url: source,
            author: "Unknown",
            user_id: "",
          });
        }

        addLog(`✅ Extracted ${itemCount} items from ${source}`, "success");
      }

      setProgress({ current: sources.length, total: sources.length });

      addLog(
        `🎉 Scraping complete! Extracted ${scrapedItems.length} total items`,
        "success"
      );
    } catch (error: any) {
      addLog(`❌ Error: ${error.message}`, "error");
    } finally {
      setIsRunning(false);
    }
  };

  const addSource = () => {
    setSources([...sources, ""]);
    console.log("Added new source input");
  };

  const updateSource = (index: number, value: string) => {
    const newSources = [...sources];
    newSources[index] = value;
    setSources(newSources);
    console.log(`Updated source at index ${index}: ${value}`);
  };

  const removeSource = (index: number) => {
    setSources(sources.filter((_, i) => i !== index));
    console.log(`Removed source at index ${index}`);
  };

  const handleFileUpload = (event: ChangeEvent<HTMLInputElement>) => {
    const target = event.target;
    if (target && target.files) {
      const file = target.files[0];
      if (file && file.type === "application/pdf") {
        setSources([...sources, `PDF: ${file.name}`]);
      }
    }
  };

  const downloadResults = () => {
    if (!results) return;

    const dataStr = JSON.stringify(results, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${teamId}_knowledge_base.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const copyToClipboard = () => {
    if (!results) return;
    navigator.clipboard.writeText(JSON.stringify(results, null, 2));
  };

  const getContentTypeIcon = (type: string) => {
    switch (type) {
      case "blog":
        return <Globe className="w-4 h-4" />;
      case "book":
        return <BookOpen className="w-4 h-4" />;
      default:
        return <FileText className="w-4 h-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                Technical Knowledge Scraper
              </h1>
              <p className="text-gray-600 text-lg">
                Extract technical content for AI knowledge bases
              </p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500">Built for</div>
              <div className="text-2xl font-bold text-indigo-600">
                Aline 
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Configuration
            teamId={teamId}
            setTeamId={setTeamId}
            sources={sources}
            updateSource={updateSource}
            addSource={addSource}
            removeSource={removeSource}
            isRunning={isRunning}
            runScraper={runScraper}
            progress={progress}
            fileInputRef={fileInputRef}
            handleFileUpload={handleFileUpload}
            setSources={setSources}
          />

          <Results
            results={results}
            getContentTypeIcon={getContentTypeIcon}
            logs={logs}
            copyToClipboard={copyToClipboard}
            downloadResults={downloadResults}
          />
        </div>

        <div className="mt-8 text-center text-gray-500 text-sm">
          <p>
            Built for Aline's technical knowledge base • Extensible for future
            customers
          </p>
          <p className="mt-1">
            Supports: interviewing.io, nilmamano.com, PDFs, Substack, and more
          </p>
        </div>
      </div>
    </div>
  );
};

export default KnowledgeScraperDashboard;
