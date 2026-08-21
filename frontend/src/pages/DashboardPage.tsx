import {
  ArrowUpRight,
  FileText,
  MessageSquare,
  Upload,
  User,
} from "lucide-react";
import { Link } from "react-router-dom";

import "./DashboardPage.css";

export default function DashboardPage() {
  return (
    <main className="dashboard-page">
      <div className="dashboard-background">
        <div className="dashboard-orb dashboard-orb-one" />
        <div className="dashboard-orb dashboard-orb-two" />
        <div className="dashboard-grid" />
      </div>

      <div className="dashboard-container">
        {/* Header */}
        <header className="dashboard-header glass-card">
          <div className="dashboard-brand">
            <div className="dashboard-brand-icon">
              <FileText size={22} />
            </div>

            <div>
              <h1>Enterprise AI</h1>
              <span>Intelligent workspace</span>
            </div>
          </div>

          <div className="dashboard-header-actions">
            <Link
              to="/profile"
              className="dashboard-profile"
              aria-label="Profile"
            >
              <User size={19} />
            </Link>
          </div>
        </header>

        {/* Welcome */}
        <section className="dashboard-welcome">
          <div>
            <span className="dashboard-eyebrow">
              AI WORKSPACE
            </span>

            <h2>
              Welcome back.
              <span> Let&apos;s work smarter.</span>
            </h2>

            <p>
              Manage your documents, search your knowledge, and
              have intelligent conversations with your data.
            </p>
          </div>

          <Link
            to="/documents"
            className="dashboard-upload-button"
          >
            <Upload size={18} />
            Upload document
            <ArrowUpRight size={17} />
          </Link>
        </section>

        {/* Stats */}
        <section className="dashboard-stats">
          <div className="dashboard-stat glass-card">
            <div className="dashboard-stat-icon">
              <FileText size={20} />
            </div>

            <div>
              <span>Total documents</span>
              <strong>0</strong>
            </div>
          </div>

          <div className="dashboard-stat glass-card">
            <div className="dashboard-stat-icon">
              <MessageSquare size={20} />
            </div>

            <div>
              <span>AI conversations</span>
              <strong>0</strong>
            </div>
          </div>

          <div className="dashboard-stat glass-card">
            <div className="dashboard-stat-icon">
              <Upload size={20} />
            </div>

            <div>
              <span>Documents processed</span>
              <strong>0</strong>
            </div>
          </div>
        </section>

        {/* Quick Actions */}
        <section className="dashboard-section">
          <div className="dashboard-section-heading">
            <div>
              <span className="dashboard-eyebrow">
                QUICK ACTIONS
              </span>

              <h3>Get started</h3>
            </div>
          </div>

          <div className="dashboard-actions-grid">
            <Link
              to="/documents"
              className="dashboard-action glass-card"
            >
              <div className="dashboard-action-icon">
                <Upload size={22} />
              </div>

              <div>
                <h4>Upload documents</h4>
                <p>
                  Add PDFs and other supported files to your
                  workspace.
                </p>
              </div>

              <ArrowUpRight size={18} />
            </Link>

            <Link
              to="/chat"
              className="dashboard-action glass-card"
            >
              <div className="dashboard-action-icon">
                <MessageSquare size={22} />
              </div>

              <div>
                <h4>Chat with AI</h4>
                <p>
                  Ask questions and get intelligent answers
                  from your documents.
                </p>
              </div>

              <ArrowUpRight size={18} />
            </Link>
          </div>
        </section>

        {/* Recent documents */}
        <section className="dashboard-section">
          <div className="dashboard-section-heading">
            <div>
              <span className="dashboard-eyebrow">
                YOUR WORKSPACE
              </span>

              <h3>Recent documents</h3>
            </div>

            <Link
              to="/documents"
              className="dashboard-view-link"
            >
              View all
              <ArrowUpRight size={16} />
            </Link>
          </div>

          <div className="dashboard-empty glass-card">
            <div className="dashboard-empty-icon">
              <FileText size={26} />
            </div>

            <h4>No documents yet</h4>

            <p>
              Upload your first document to start building
              your AI-powered knowledge workspace.
            </p>

            <Link
              to="/documents"
              className="dashboard-empty-button"
            >
              <Upload size={17} />
              Upload your first document
            </Link>
          </div>
        </section>
      </div>
    </main>
  );
}
