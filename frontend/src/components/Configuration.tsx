import React from "react";
import { Upload, Play, Clock, Plus, Trash2 } from "lucide-react";

type Props = {
  teamId: string;
  setTeamId: (id: string) => void;
  sources: string[];
  setSources: (sources: string[]) => void;
  isRunning: boolean;
  runScraper: () => void;
  progress: { current: number; total: number };
  fileInputRef: React.RefObject<HTMLInputElement | null>;
  handleFileUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
  updateSource: (index: number, value: string) => void;
  addSource: () => void;
  removeSource: (index: number) => void;
};

const Configuration = ({
  teamId,
  setTeamId,
  sources,
  updateSource,
  addSource,
  removeSource,
  isRunning,
  runScraper,
  progress,
  fileInputRef,
  handleFileUpload,
}: Props) => {
  return (
    <div className="bg-white rounded-2xl shadow-xl p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
        <Play className="w-6 h-6 mr-2 text-indigo-600" />
        Configuration
      </h2>

      {/* Team ID */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Team ID
        </label>
        <input
          type="text"
          value={teamId}
          onChange={(e) => setTeamId(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          placeholder="e.g., aline123"
        />
      </div>

      {/* Sources */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <label className="block text-sm font-medium text-gray-700">
            Content Sources
          </label>
          <button
            onClick={addSource}
            className="text-indigo-600 hover:text-indigo-700 flex items-center text-sm"
          >
            <Plus className="w-4 h-4 mr-1" />
            Add Source
          </button>
        </div>

        <div className="space-y-3 max-h-64 overflow-y-auto">
          {sources.map((source, index) => (
            <div key={index} className="flex items-center space-x-2">
              <input
                type="text"
                value={source}
                onChange={(e) => updateSource(index, e.target.value)}
                className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="https://example.com/blog"
              />
              <button
                onClick={() => removeSource(index)}
                className="text-red-500 hover:text-red-700 p-1"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* File Upload */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Upload PDF (e.g., Aline's Book)
        </label>
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-4">
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileUpload}
            ref={fileInputRef}
            className="hidden"
          />
          <button
            onClick={() => fileInputRef?.current?.click()}
            className="w-full flex items-center justify-center space-x-2 text-gray-600 hover:text-gray-800"
          >
            <Upload className="w-5 h-5" />
            <span>Click to upload PDF</span>
          </button>
        </div>
      </div>

      {/* Run Button */}
      <button
        onClick={runScraper}
        disabled={isRunning || sources.length === 0}
        className={`w-full py-3 px-6 rounded-lg font-semibold flex items-center justify-center space-x-2 ${
          isRunning || sources.length === 0
            ? "bg-gray-300 text-gray-500 cursor-not-allowed"
            : "bg-indigo-600 text-white hover:bg-indigo-700 transform hover:scale-105 transition-all"
        }`}
      >
        {isRunning ? (
          <>
            <Clock className="w-5 h-5 animate-spin" />
            <span>
              Scraping... ({progress.current}/{progress.total})
            </span>
          </>
        ) : (
          <>
            <Play className="w-5 h-5" />
            <span>Start Scraping</span>
          </>
        )}
      </button>

      {/* Progress Bar */}
      {isRunning && (
        <div className="mt-4">
          <div className="bg-gray-200 rounded-full h-2">
            <div
              className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
              style={{
                width: `${(progress.current / progress.total) * 100}%`,
              }}
            ></div>
          </div>
          <div className="text-sm text-gray-600 mt-1 text-center">
            Processing {progress.current} of {progress.total} sources
          </div>
        </div>
      )}
    </div>
  );
};

export default Configuration;
